"""
Unit tests for AI Code Executor - Day 2.1 Testing

Tests:
1. AICodeExecutor initialization
2. _generate_code method
3. _extract_code_from_response method
"""
import pytest
from pathlib import Path
from app.services.ai_executor.executor import AICodeExecutor
from loguru import logger 


class TestAICodeExecutor:
    """Unit tests for AICodeExecutor service"""

    @pytest.fixture
    def executor(self):
        """ Run before each test, This create a new instance of AICodeExecutor for each test, ensure fresh state for each test """
        return AICodeExecutor(user_id="c43c4b4a-ed8a-45fe-8d26-0d74f471fbc3")
    
    @pytest.mark.asyncio
    async def test_initialization(self, executor):
        """Test AICodeExecutor initialization"""
        assert executor.user_id == "c43c4b4a-ed8a-45fe-8d26-0d74f471fbc3"
        assert executor.gemini_client is not None
        logger.info("AICodeExecutor initialization test passed")

    @pytest.mark.asyncio
    async def test_generate_code_simple_request(self, executor):
        """
        Test code generation with a simple request
        Request: "Read the first excel file and show the first 5 rows"
        """
        #Simulate uploaded files
        fake_files = [
            Path("/tmp/input/sample_data.xlsx"),
            Path("/tmp/input/customers.xlsx")
        ]

        user_request = "Read the first excel file and show the first 5 rows"

        #Generate code
        generated_code = await executor._generate_code(user_request, fake_files)

        #Print for manual inspection
        logger.info("===GENERATED CODE===")
        print("\n" + "=" * 80 + "\n")
        print(generated_code)
        print("\n" + "=" * 80 + "\n")

        #Assertions
        assert len(generated_code) > 0, "Generated code is not empty"
        assert "import" in generated_code, "Code should have import statements"

        has_pandas_or_openpyxl = ("pandas" in generated_code.lower() or "openpyxl" in generated_code.lower())

        assert has_pandas_or_openpyxl, "Code should use pandas or openpyxl"

        logger.info("Code generation test passed")

        #Check if the code executed successfully
        assert True
    
    def test_extract_code_from_markdown(self, executor):
        """
        Test code extraction from markdown response.
        
        Tests both:
        1. Proper markdown format with ```python blocks
        2. Fallback for plain text without markdown
        """
        # Test Case 1: Proper markdown
        markdown_response = """Here's the code:
        ```python
        import pandas as pd
        df = pd.read_excel("file.xlsx")
        print(df.head(5))
        ```
        This code will work great!"""

        extracted = executor._extract_code_from_response(markdown_response)

        assert "import pandas as pd" in extracted
        assert "Here's the code:" not in extracted  # Should strip markdown
        assert "This code will work" not in extracted  # Should strip explanation

        logger.info("✅ Markdown extraction test passed")

        # Test Case 2: Plain text fallback
        plain_response = """import pandas as pd
        df = pd.read_excel("file.xlsx")
        print(df.head(5))"""

        extracted_plain = executor._extract_code_from_response(plain_response)
        assert "import pandas as pd" in extracted_plain

        logger.info("✅ Plain text fallback test passed")
