"""
Integration Tests for AI Code Executor Orchestrator

Tests the complete flow:
1. User request → AI generates code → Validator checks → Docker executes → Return results

Test Scenarios:
- LOW_RISK: Code with pandas only (auto-execute)
- MEDIUM_RISK: Code with requests (ask permission)
- HIGH_RISK: Code with os import (block)
- File Operations: Real Excel file processing
"""
import pytest
import tempfile
from pathlib import Path
from app.services.ai_executor.executor import AICodeExecutor
from loguru import logger
import pandas as pd
import io


class TestOrchestratorIntegration:
    """Integration tests for complete AICodeExecutor orchestration"""

    @pytest.fixture
    def executor(self):
        """Create AICodeExecutor instance for testing"""
        return AICodeExecutor(user_id="test-user-123")

    @pytest.fixture
    def sample_excel_file(self):
        """
        Create a temporary Excel file for testing.
        
        Creates a simple Excel file with sample data that we can use
        to test real file processing.
        """
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')

        # Create sample DataFrame
        df = pd.DataFrame({
            'Product': ['Apple', 'Banana', 'Orange', 'Grape'],
            'Price': [1.20, 0.50, 0.80, 2.00],
            'Quantity': [100, 150, 80, 60]
        })

        # Save to Excel
        df.to_excel(temp_file.name, index=False)

        yield Path(temp_file.name)

        # Cleanup after test
        Path(temp_file.name).unlink()

    @pytest.mark.asyncio
    async def test_low_risk_execution_with_real_file(self, executor, sample_excel_file):
        """
        Test LOW_RISK scenario: Pandas-only code with real Excel file.
        
        Flow:
        1. User uploads Excel file
        2. User asks: "Read this Excel file and show the first 3 rows"
        3. AI generates pandas code
        4. Validator approves (LOW_RISK)
        5. Docker executes code
        6. Returns output
        
        Expected: Should execute successfully without permission request
        """
        logger.info("🧪 Testing LOW_RISK scenario with real Excel file...")

        user_request = "Read the Excel file and print the first 3 rows"
        uploaded_files = [sample_excel_file]

        # Execute task
        result = await executor.execute_task(user_request, uploaded_files)

        # Assertions
        assert result["success"] == True, "Execution should succeed"
        assert "requires_permission" not in result, "Should NOT require permission for pandas"
        assert "output" in result, "Should have output"
        assert "exit_code" in result, "Should have exit code"
        assert result["exit_code"] == 0, "Exit code should be 0 (success)"

        # Check output contains data (AI might print the dataframe)
        logger.info(f"✅ Output: {result['output'][:200]}")  # Print first 200 chars

        logger.info("✅ LOW_RISK test passed!")

    @pytest.mark.asyncio
    async def test_medium_risk_permission_required(self, executor, sample_excel_file):
        """
        Test MEDIUM_RISK scenario: Code that needs network access.
        
        Flow:
        1. User asks: "Download data from https://api.example.com and save to Excel"
        2. AI generates code with 'requests' import
        3. Validator detects MEDIUM_RISK
        4. Returns permission request (does NOT execute)
        
        Expected: Should return requires_permission=True, NOT execute
        """
        logger.info("🧪 Testing MEDIUM_RISK scenario (requests import)...")

        # This request will likely cause AI to use 'requests' library
        user_request = "Download JSON data from https://api.coinbase.com/v2/prices/BTC-USD/spot and save it to an Excel file"
        uploaded_files = []

        # Execute task
        result = await executor.execute_task(user_request, uploaded_files)

        # Assertions
        assert result["success"] == False, "Should NOT execute without permission"
        assert result.get("requires_permission") == True, "Should require permission"
        assert result.get("risk_level") == "medium", "Risk level should be medium"
        assert "explanation" in result, "Should provide explanation"
        assert "code_preview" in result, "Should show code preview"
        assert "restricted_imports" in result, "Should list restricted imports"

        # Check that restricted imports include network-related libraries
        restricted = result["restricted_imports"]
        logger.info(f"⚠️ Restricted imports: {restricted}")

        # Should contain at least one network library
        has_network_lib = any(lib in restricted for lib in ["requests", "urllib", "urllib3", "httpx"])
        assert has_network_lib, f"Should flag network library, got: {restricted}"

        logger.info("✅ MEDIUM_RISK test passed!")

    @pytest.mark.asyncio
    async def test_high_risk_blocked(self, executor):
        """
        Test HIGH_RISK scenario: Code with dangerous imports.
        
        Flow:
        1. User asks malicious request (or AI generates risky code)
        2. AI generates code with 'os' or 'subprocess'
        3. Validator detects HIGH_RISK
        4. Blocks execution completely
        
        Expected: Should return success=False with security error
        """
        logger.info("🧪 Testing HIGH_RISK scenario (os import)...")

        # This request might cause AI to use 'os' module
        user_request = "List all files in the current directory and delete any file containing 'temp' in the name"
        uploaded_files = []

        # Execute task
        result = await executor.execute_task(user_request, uploaded_files)

        # Assertions
        assert result["success"] == False, "Should block HIGH_RISK code"

        # Should either:
        # 1. Be blocked by validator (error message contains "security validation")
        # 2. AI might avoid using dangerous imports (success with pandas approach)

        if "error" in result:
            logger.info(f"❌ Blocked with error: {result['error']}")
            assert "security validation" in result.get("error", "").lower() or \
                    "high risk" in result.get("reason", "").lower(), \
                    "Should mention security/high risk"

        logger.info("✅ HIGH_RISK test passed!")

    @pytest.mark.asyncio
    async def test_file_processing_with_output(self, executor, sample_excel_file):
        """
        Test complete file processing workflow with output file generation.
        
        Flow:
        1. Upload Excel file with sales data
        2. Ask AI to filter data and save to new file
        3. AI generates pandas code
        4. Docker executes and creates output file
        5. Returns output file in response
        
        Expected: Should return output_files dict with processed file
        """
        logger.info("🧪 Testing file processing with output generation...")

        user_request = "Read the Excel file, filter rows where Price > 1.00, and save the result to /tmp/output/filtered.xlsx"
        uploaded_files = [sample_excel_file]

        # Execute task
        result = await executor.execute_task(user_request, uploaded_files)

        # Assertions
        assert result["success"] == True, "Execution should succeed"

        # Check if output files were generated
        if "output_files" in result and result["output_files"]:
            logger.info(f"📁 Output files generated: {list(result['output_files'].keys())}")

            # Verify output file exists
            assert len(result["output_files"]) > 0, "Should generate at least one output file"

            # Check file is valid Excel (has bytes)
            for filename, file_bytes in result["output_files"].items():
                assert len(file_bytes) > 0, f"Output file {filename} should have content"
                logger.info(f"✅ {filename}: {len(file_bytes)} bytes")
        else:
            logger.warning("⚠️ No output files generated (AI might have just printed results)")

        logger.info("✅ File processing test passed!")
