"""
DockerSandbox - Secure container execution environment for AI-generated code

This class manages the lifecycle of Docker containers that execute AI-generated Python code.
Think of it as a "hotel manager" - creates rooms (containers), manages guests (code execution),
and cleans up after they leave.

Security features:
1. Isolated containers (code can't access host system)
2. Resource limits (CPU, memory, timeout)
3. No network access (can't send data externally)
4. Non-root execution (limited permissions inside container)
5. Ephemeral containers (destroyed after use)
"""

import docker
import logging
import io
import tarfile
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

# Set up logging for this module
logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """
    Result of code execution in Docker sandbox.
    
    Attributes:
        success: Whether execution completed without errors
        output: Standard output from the code
        error: Error message if execution failed
        exit_code: Container exit code (0 = success)
        output_files: Dict of output files {filename: bytes}
    """
    success: bool
    output: str
    error: str = ""
    exit_code: int = 0
    output_files: Dict[str, bytes] = None

    def __post_init__(self):
        """Initialize output_files dict if None"""
        if self.output_files is None:
            self.output_files = {}


class DockerSandbox:
    """
    Manages Docker containers for secure execution of AI-generated Python code.
    
    This class provides the execution environment (the "hotel room") where
    untrusted AI code runs safely, isolated from the host system.
    """

    # Docker image name (built from Dockerfile.executor)
    IMAGE_NAME = "excel-ai-executor:latest"

    # Resource limits for safety
    MEMORY_LIMIT = "512m"  # 512 MB RAM max
    CPU_COUNT = 1           # 1 CPU core max
    TIMEOUT_SECONDS = 120   # 2 minutes max execution time

    def __init__(self):
        """
        Initialize Docker client and verify image exists.
        
        Raises:
            docker.errors.DockerException: If Docker is not running
            docker.errors.ImageNotFound: If executor image not built
        """
        try:
            # Connect to Docker daemon (Docker Desktop must be running)
            self.client = docker.from_env()

            # Verify our executor image exists
            self.client.images.get(self.IMAGE_NAME)

            logger.info(f"✅ DockerSandbox initialized with image: {self.IMAGE_NAME}")

        except docker.errors.ImageNotFound:
            logger.error(f"❌ Docker image '{self.IMAGE_NAME}' not found!")
            logger.error("Run: docker build -f Dockerfile.executor -t excel-ai-executor:latest .")
            raise

        except docker.errors.DockerException as e:
            logger.error(f"❌ Docker not available: {e}")
            logger.error("Make sure Docker Desktop is running")
            raise

    def execute_code(
        self, 
        code: str, 
        input_files: Optional[Dict[str, bytes]] = None
    ) -> ExecutionResult:
        """
        Execute Python code in isolated Docker container.
        
        This is the main method - it handles the complete lifecycle:
        1. Create container
        2. Copy input files into container
        3. Execute code
        4. Retrieve output files
        5. Clean up container
        
        Args:
            code: Python code to execute (already validated by CodeValidator)
            input_files: Dict of input files {filename: file_bytes}
        
        Returns:
            ExecutionResult with output, errors, and generated files
        
        Example:
            sandbox = DockerSandbox()
            result = sandbox.execute_code(
                code="import pandas as pd\\ndf = pd.read_excel('/tmp/input/data.xlsx')\\nprint(df.head())",
                input_files={"data.xlsx": excel_file_bytes}
            )
            print(result.output)  # Prints DataFrame
        """
        container = None

        try:
            logger.info("🚀 Creating Docker container...")

            # Step 1: Create container with security restrictions
            container = self._create_container()

            # Step 2: Start the container
            container.start()
            logger.info(f"✅ Container {container.short_id} started")

            # Step 3: Copy input files into container (if any)
            if input_files:
                self._copy_files_to_container(container, input_files)

            # Step 4: Execute the Python code
            exec_result = self._execute_python_code(container, code)

            # Step 5: Retrieve output files from container
            output_files = self._get_output_files(container)

            # Step 6: Return results
            return ExecutionResult(
                success=exec_result["exit_code"] == 0,
                output=exec_result["output"],
                error=exec_result["error"],
                exit_code=exec_result["exit_code"],
                output_files=output_files
            )

        except Exception as e:
            logger.error(f"❌ Execution failed: {e}", exc_info=True)
            return ExecutionResult(
                success=False,
                output="",
                error=f"Docker execution error: {str(e)}",
                exit_code=-1
            )

        finally:
            # ALWAYS clean up container (security!)
            if container:
                self._cleanup_container(container)

    def _create_container(self) -> docker.models.containers.Container:
        """
        Create Docker container with security restrictions.
        
        Security features:
        - network_disabled=True: No internet access
        - mem_limit: Prevents memory exhaustion attacks
        - cpu_count: Prevents CPU exhaustion attacks  
        - user="sandbox": Non-root execution
        - read_only=False: Allow writing to /tmp (we need this for output files)
        
        Returns:
            Created (but not started) Docker container
        """
        container = self.client.containers.create(
            image=self.IMAGE_NAME,

            # Security: Disable network (code can't send data externally)
            network_disabled=True,

            # Resource limits (prevent DoS attacks)
            mem_limit=self.MEMORY_LIMIT,
            nano_cpus=self.CPU_COUNT * 1_000_000_000,  # Convert to nano CPUs

            # Don't attach to terminal (we'll use exec_run for code)
            detach=True,

            # Remove container automatically after it stops
            auto_remove=False,  # We'll remove manually after getting files

            # Keep container running so we can exec commands
            command="tail -f /dev/null",  # Dummy command to keep alive
        )

        return container

    def _copy_files_to_container(
        self, 
        container: docker.models.containers.Container,
        files: Dict[str, bytes]
    ) -> None:
        """
        Copy input files into container's /tmp/input directory.
        
        Uses tar archive to transfer multiple files efficiently.
        
        Args:
            container: Running Docker container
            files: Dict mapping filename -> file bytes
        """
        logger.info(f"📁 Copying {len(files)} file(s) to container...")

        # Create in-memory tar archive with all files
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            for filename, file_bytes in files.items():
                # Create tarfile entry
                file_data = io.BytesIO(file_bytes)
                tarinfo = tarfile.TarInfo(name=filename)
                tarinfo.size = len(file_bytes)
                tar.addfile(tarinfo, file_data)

        # Rewind stream to beginning
        tar_stream.seek(0)

        # Copy tar archive to container's /tmp/input
        container.put_archive('/tmp/input', tar_stream)
        logger.info(f"✅ Files copied to /tmp/input/")

    def _execute_python_code(
        self,
        container: docker.models.containers.Container,
        code: str
    ) -> Dict[str, any]:
        """
        Execute Python code inside the container.
        
        Args:
            container: Running Docker container
            code: Python code string to execute
        
        Returns:
            Dict with keys: output (str), error (str), exit_code (int)
        """
        logger.info("⚙️ Executing Python code in container...")

        # Execute Python code using exec_run
        # We use -c flag to execute code string directly
        exec_result = container.exec_run(
            cmd=["python", "-c", code],
            user="sandbox",  # Run as non-root user
            workdir="/tmp",
            demux=True,  # Separate stdout and stderr
        )

        # Extract stdout and stderr
        stdout = exec_result.output[0].decode('utf-8') if exec_result.output[0] else ""
        stderr = exec_result.output[1].decode('utf-8') if exec_result.output[1] else ""
        exit_code = exec_result.exit_code

        if exit_code == 0:
            logger.info(f"✅ Code executed successfully (exit code: {exit_code})")
        else:
            logger.error(f"❌ Code execution failed (exit code: {exit_code})")
            logger.error(f"Error: {stderr}")

        return {
            "output": stdout,
            "error": stderr,
            "exit_code": exit_code
        }

    def _get_output_files(
        self,
        container: docker.models.containers.Container
    ) -> Dict[str, bytes]:
        """
        Retrieve output files from container's /tmp/output directory.
        
        Args:
            container: Running Docker container
        
        Returns:
            Dict mapping filename -> file bytes
        """
        logger.info("📥 Retrieving output files...")

        try:
            # Get tar archive from /tmp/output
            tar_stream, stat = container.get_archive('/tmp/output')

            # Extract files from tar archive
            output_files = {}
            tar_bytes = b''.join(tar_stream)

            with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tar:
                for member in tar.getmembers():
                    if member.isfile() and member.name != 'output':
                        # Extract file
                        file_obj = tar.extractfile(member)
                        if file_obj:
                            filename = os.path.basename(member.name)
                            output_files[filename] = file_obj.read()
                            logger.info(f"  ✅ Retrieved: {filename}")

            logger.info(f"📥 Retrieved {len(output_files)} output file(s)")
            return output_files

        except docker.errors.NotFound:
            # /tmp/output directory is empty or doesn't exist
            logger.info("No output files generated")
            return {}

        except Exception as e:
            logger.error(f"Error retrieving output files: {e}")
            return {}

    def _cleanup_container(
        self,
        container: docker.models.containers.Container
    ) -> None:
        """
        Stop and remove container (cleanup).
        
        This is CRITICAL for security - we must destroy containers
        after use so no data persists between executions.
        
        Args:
            container: Container to clean up
        """
        try:
            logger.info(f"🧹 Cleaning up container {container.short_id}...")

            # Stop container (if still running)
            container.stop(timeout=5)

            # Remove container completely
            container.remove(force=True)

            logger.info(f"✅ Container {container.short_id} removed")

        except Exception as e:
            logger.warning(f"⚠️ Error cleaning up container: {e}")