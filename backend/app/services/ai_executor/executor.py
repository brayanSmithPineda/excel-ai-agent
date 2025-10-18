"""
AI Code Executor Service

Generates Python code dynamically using Gemini AI and executes it in a secure Docker sandbox.
This service transforms the Excel AI Agent from an advisor to an executor.

Key Features:
- Dynamic code generation (no pre-written templates)
- Security validation via AST analysis
- Sandboxed execution in Docker containers
- Support for pandas, openpyxl, numpy operations

This files is the orchestrator that ties everything together.
1- _generate_code: Generates the code using Gemini AI
2- validator.py: CodeValidator class
3- docker_sandbox.py: DockerSandbox class
"""
from typing import List, Optional, Dict, Any
from pathlib import Path
from loguru import logger
import re #regular expressions
from google import genai #New gemini SDK
from google.genai import types #Types for the new gemini SDK
from app.config.settings import settings
from app.services.ai_executor.validator import CodeValidator
from app.services.ai_executor.docker_sandbox import DockerSandbox

class AICodeExecutor:
    """
    Main service for AI-driven code generation and execution.
    
    This service takes natural language requests like "Stack these 3 workbooks"
    and converts them into executable Python code using Gemini AI.
    """

    def __init__(self, user_id: str):
        """
        Initialize the AI Code executor service, takes as argument uthe User ID of the authenticated user
        """
        self.user_id = user_id # authenticated user id

        #Intilize the Gemini service
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required but not found in environment variables")
        
        self.gemini_client = genai.Client(api_key=settings.gemini_api_key.get_secret_value())

        #Intilize code validator
        self.validator = CodeValidator()

        #Intilize the Docker sandbox
        self.sandbox = DockerSandbox()

    async def execute_task(self, user_request: str, uploaded_files: List[Path], operation_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point for executing user requests.
        
        Flow:
        1. Analyze user request to understand intent
        2. Generate Python code using Gemini AI
        3. Validate code for security (AST analysis)
        4. Execute code in Docker sandbox
        5. Return results or download link
        
        Args:
            user_request: Natural language request (e.g., "Stack these workbooks")
            uploaded_files: List of file paths user uploaded
            operation_type: Optional hint about operation (e.g., "consolidate", "pivot")
        
        Returns:
            Dict with keys:
                - success: bool
                - result_file_path: Path to generated file (if applicable)
                - output: Any text output from execution
                - error: Error message if failed
        """
        logger.info(f"Executing task for user {self.user_id}: {user_request}")
        logger.info(f"Uploaded files: {[str(f) for f in uploaded_files]}")

        try:
            # Step 1: Generate code using AI
            generated_code = await self._generate_code(user_request, uploaded_files)

            # Step 2: Validate code for security
            validation_result = self.validator.validate(generated_code)

            # Check 1: HIGH RISK - Always block (is_safe=False)
            if validation_result.is_safe == False:
                logger.error(f"code validation failed: {validation_result.reason}")
                return {
                    "success": False,
                    "error": "Generated code failed security validation",
                    "reason": validation_result.reason,
                }

            # Check 2: MEDIUM RISK - Requires user permission (is_safe=True, requires_permission=True)
            if validation_result.requires_permission:
                logger.warning(f"⚠️ MEDIUM RISK: Code requires user permission")
                logger.warning(f"Restricted imports: {validation_result.restricted_imports}")

                # Return special response asking for permission
                # (Frontend will show this to user with approve/deny buttons)
                return {
                    "success": False,  # Can't proceed without permission
                    "requires_permission": True,
                    "risk_level": "medium",
                    "explanation": validation_result.explanation,
                    "restricted_imports": validation_result.restricted_imports,
                    "code_preview": generated_code,  # Show user what will run
                    "message": "This operation requires your permission to proceed"
                }

            # Step 3: Execute in Docker sandbox (At this point we already validated the code and the user has approved the permission)
            try:
                input_files = {}
                for file_path in uploaded_files:
                    with open(file_path, "rb") as f: #rb = read binary, to read the file as bytes
                        input_files[file_path.name] = f.read() #f.read() returns the file as bytes
                
                #Execute the code in the Docker sandbox
                execution_result = self.sandbox.execute_code(
                    code = generated_code,
                    input_files = input_files
                )

                #Check if execution was successful
                if execution_result.success == False:
                    logger.error(f"Code execution failed: {execution_result.error}")
                    return {
                        "success": False,
                        "error": "Code execution failed",
                        "details": execution_result.error,
                        "output": execution_result.output
                    }
                # Step 4: Return successful results
                return {
                    "success": True,
                    "output": execution_result.output,
                    "output_files": execution_result.output_files,
                    "exit_code": execution_result.exit_code
                }
            except Exception as e:
                logger.error(f"Docker execution failed: {str(e)}", exc_info=True)
                return {
                    "success": False,
                    "error": f"Docker execution error: {str(e)}"
                }

        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_code(self, user_request: str, uploaded_files: List[Path]) -> str:
        """
        Generate Python code using Gemini AI.
        
        This method will use prompt engineering to instruct Gemini to:
        1. Understand the user's request
        2. Analyze the uploaded files
        3. Generate Python code using pandas/openpyxl
        4. Return ONLY the code, no explanations
        
        We'll implement this in Day 2.
        """
        #Build the context about the upload files
        file_info_list = []
        for file in uploaded_files:
            file_info_list.append(f"- {file.name} (path: /tmp/input/{file.name})")

        file_info = "\n".join(file_info_list) if file_info_list else "No files uploaded"

        # Add a note about file structure
        file_structure_note = """
        NOTE: Uploaded Excel/CSV files may contain multiple columns. 
        Do NOT assume column structure - use pandas to inspect the actual columns first.
        Use df.columns to see what columns exist before processing.
        """
        #Promt engineering for the Gemini AI
        promt = f"""You are a Python code generator for Excel operations.

            USER REQUEST: {user_request}

            AVAILABLE FILES:
            {file_info}
            
            {file_structure_note}

            INSTRUCTIONS:
            1. Generate Python code using pandas and/or openpyxl libraries
            2. Files are located in /tmp/input/ directory
            3. Save any output files to /tmp/output/ directory
            4. Use ONLY these libraries: pandas, openpyxl, numpy, pathlib
            5. Do NOT use os, sys, subprocess, socket, or any system-level modules
            6. File paths are already provided - use them directly without os.path operations
            7. Return ONLY the Python code wrapped in ```python ``` markdown block
            8. Do NOT include explanations - ONLY executable code
            9. Handle errors gracefully with try/except blocks
            10. All input files are guaranteed to exist at /tmp/input/<filename>

            EXAMPLE PATTERN:
            ```python
            import pandas as pd
            from pathlib import Path
            
            # Read files directly
            df1 = pd.read_excel('/tmp/input/file1.xlsx')
            df2 = pd.read_excel('/tmp/input/file2.xlsx')
            
            # Process data
            result = pd.concat([df1, df2])
            
            # Save output
            result.to_excel('/tmp/output/combined.xlsx', index=False)
            ```

            Generate the Python code now:
        """

        try:
            #Call Gemini AI to generate the code
            response = self.gemini_client.models.generate_content(
                model = "gemini-2.0-flash",
                contents = promt
            )

            #Extract code from markdown response
            generated_code = self._extract_code_from_response(response.text)

            logger.info(f"Generated code: length {len(generated_code)} characters")
            #Print the generated code for manual inspection
            print("=" * 80)
            print("GENERATED CODE:")
            print("=" * 80)
            print(generated_code)
            print("=" * 80)

            return generated_code
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            raise RuntimeError(f"Failed to generate code: {str(e)}")

    def _extract_code_from_response(self, response_text: str) -> str:
        """
        Extract Python code from Gemini's markdown response.
        
        Gemini returns code in markdown format like:
        ```python
        import pandas as pd
        df = pd.read_excel("file.xlsx")
        ```
        
        This method extracts just the code part.
        
        Args:
            response_text: Full response from Gemini (includes markdown)
        
        Returns:
            Pure Python code without markdown formatting
        
        Raises:
            ValueError: If no code block found in response
        """
        #Regex patter to extract code between ```python and ```
        pattern = r"```python\s*(.*?)\s*```"

        #Get the match, 
        match = re.search(pattern, response_text, re.DOTALL)

        if match:
            code = match.group(1).strip()
            return code
        else:
            #If not markdown block, assume entire response is code
            logger.warning("No code block found in response, using entire response as code")
            return response_text.strip()
