"""
Test suite for the hybrid search system (Phase 3.3.4)
This test if  our code properly integrates the three search strategies: finite, infinite, and semantic search.
it does not test the actual search strategies, it only tests the integration of the three search strategies.
"""
import sys
sys.path.append('../') #add the backend directory to the path
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List, Optional
import pytest_asyncio
from app.services.excel_parser_service import ExcelContext, Symbol, SymbolType
from app.services.gemini_service import GeminiService

class TestHybridSearchSystem:
    """
    Test suite for the hybrind dearch system (Phase 3.3.4)
    """

    def setup_method(self):
        """ Set up test enviroment before each test, this function will be run before each test"""
        self.gemini_service = GeminiService()

        #We will mock supabase client to avoid actual database interactions (we do not want to create actual conversations in the database)
        self.gemini_service.supabase = MagicMock() #This will replace the actual supabase client with a mock object

        self.gemini_service.client = MagicMock() #This will replace the actual gemini client with a mock object

    def create_mock_finite_search_results(self) -> List[Dict]:
        """Create mock results for finite search (Mimic excel function database in supabase)"""
        return [
            {
                'id': '1',
                'function_name': 'VLOOKUP',
                'description': 'Searches for a value in a table and returns a corresponding value',
                'category': 'Lookup',
                'relevance_score': 100,
                'match_type': 'exact'
            },
            {
                'id': '2',
                'function_name': 'SUMIF',
                'description': 'Sums cells that meet a specific criteria',
                'category': 'Math',
                'relevance_score': 80,
                'match_type': 'keyword'
            }
        ]

    def create_mock_infinite_search_results(self) -> List[Dict]:
        """Create mock results for infinite search (Mimic the DynamicSymbolTable)"""
        return [
            {
                'symbol_key': 'Sheet1!A1',
                'symbol_name': 'Sales_Data',
                'symbol_type': 'range_reference',
                'data_type': 'range',
                'sheet_context': 'Sheet1',
                'current_value': 'A1:C10',
                'relevance_score': 90,
                'match_type': 'exact_name'
            },
            {
                'symbol_key': 'Sheet1!TotalRevenue',
                'symbol_name': 'TotalRevenue',
                'symbol_type': 'named_range',
                'data_type': 'number',
                'sheet_context': 'Sheet1',
                'current_value': 150000,
                'relevance_score': 85,
                'match_type': 'value_match'
            }
        ]

    def create_mock_semantic_search_results(self) -> List[Dict]:
        """Create mock results for semantic search (Mimicpast conversations is our semantic similarity search)"""
        return [
            {
                'conversation_id': 'conv_123',
                'chunk_text': 'User: How do I calculate sales totals? Assistant: You can use SUM or SUMIF functions...',
                'similarity_score': 0.85,
                'metadata': {'excel_functions_mentioned': ['SUM', 'SUMIF']},
                'created_at': '2024-01-01T10:00:00Z',
                'distance': 0.15
            },
            {
                'conversation_id': 'conv_456',
                'chunk_text': 'User: Need help with lookup formulas. Assistant: VLOOKUP is perfect for finding data...',
                'similarity_score': 0.78,
                'metadata': {'excel_functions_mentioned': ['VLOOKUP']},
                'created_at': '2024-01-02T11:00:00Z',
                'distance': 0.22
            }
        ]
    
    @pytest.mark.asyncio #decorator to mark the below function as an async test, is the only way to test async functions with pytest
    async def test_hybrid_search_integration_success(self):
        """Test case 1: All three strategies return results and are properly integrated"""
        query = "sales data lookup totals"
        user_id = "user_123"
        excel_context = ExcelContext(sheet_name="Sheet1", workbook_name = "SalesReport.xlsx")
        
        #Mock each individual search strategy
        mock_finite_results = self.create_mock_finite_search_results()
        mock_infinite_results = self.create_mock_infinite_search_results()
        mock_semantic_results = self.create_mock_semantic_search_results()

        #Patch basically replace actual method in the gemini_service class with the mock method we created above
        #For example, replace gemini_service.excel_function_search with the mock_finite_results
        with patch.object(self.gemini_service, 'excel_function_search',
                            new_callable=AsyncMock, return_value=mock_finite_results), \
            patch.object(self.gemini_service, '_infinite_search_user_symbols',
                            new_callable=AsyncMock, return_value=mock_infinite_results), \
            patch.object(self.gemini_service, 'semantic_similarity_search',
                            new_callable=AsyncMock, return_value=mock_semantic_results):
            
            #Call the hybrid search method
            result = await self.gemini_service.hybrid_lexical_search(query, user_id, excel_context, limit=10)

            #Verify the result structure and content
            assert result is not None, "Hybrid search results should not be None"
            assert result['query'] == query, "Query should be the same as the input query"
            assert result['total_results'] > 0, "Should have at least one result"

            #Verify all three search strategies
            expected_strategies = ['finite_search', 'infinite_search', 'semantic_search']
            actual_strategies = result['search_metadata']['search_strategies']
            assert all(strategy in actual_strategies for strategy in expected_strategies), "Should have all three search strategies"

            # Verify each search type returned results
            assert len(result['finite_search_results']) == 2, "Should have finite search results"
            assert len(result['infinite_search_results']) == 2, "Should have infinite search results"
            assert len(result['semantic_search_results']) == 2, "Should have semantic search results"

            # Verify combined results are properly structured
            assert 'combined_results' in result, "Should have combined results"
            assert len(result['combined_results']) > 0, "Combined results should not be empty"

            # Verify metadata structure
            metadata = result['search_metadata']
            assert metadata['has_user_id'] is True, "Should recognize user_id is provided"
            assert metadata['has_excel_context'] is True, "Should recognize excel_context is provided"

            print("✅ SUCCESS: All three search strategies integrated successfully!")
    
    @pytest.mark.asyncio
    async def test_hybrid_search_semantic_failure(self):
        """
        Test Case 1: System handles gracefully when semantic search fails
        Finite ✅ + Infinite ✅ + Semantic ❌
        """
        query = "excel formulas"
        user_id = "test_user_456"
        excel_context = ExcelContext(sheet_name="Sheet1")

        # Mock scenario: Finite works, infinite works, semantic FAILS
        mock_finite_results = self.create_mock_finite_search_results()
        mock_infinite_results = self.create_mock_infinite_search_results()

        with patch.object(self.gemini_service, 'excel_function_search',
                        new_callable=AsyncMock, return_value=mock_finite_results), \
            patch.object(self.gemini_service, '_infinite_search_user_symbols',
                        new_callable=AsyncMock, return_value=mock_infinite_results), \
            patch.object(self.gemini_service, 'semantic_similarity_search',
                        new_callable=AsyncMock, side_effect=Exception("Semantic search error")):

            result = await self.gemini_service.hybrid_lexical_search(
                query=query,
                user_id=user_id,
                excel_context=excel_context,
                limit=5
            )

            # ASSERT: Should work with 2 out of 3 strategies
            assert result is not None, "Should return results despite semantic failure"
            assert len(result['finite_search_results']) == 2, "Finite search should work"
            assert len(result['infinite_search_results']) == 2, "Infinite search should work"
            assert len(result['semantic_search_results']) == 0, "Semantic search should fail"

            strategies = result['search_metadata']['search_strategies']
            assert 'finite_search' in strategies, "Finite search should be recorded"
            assert 'infinite_search' in strategies, "Infinite search should be recorded"
            assert 'semantic_search' not in strategies, "Semantic search should be skipped due to error"

            print("✅ SUCCESS: System handles semantic search failures gracefully!")

    @pytest.mark.asyncio
    async def test_hybrid_search_finite_failure(self):
        """
        Test Case 2: System handles gracefully when finite search fails
        Finite ❌ + Infinite ✅ + Semantic ✅
        """
        query = "lookup data"
        user_id = "test_user_789"
        excel_context = ExcelContext(sheet_name="Sheet1")

        # Mock scenario: Finite FAILS, infinite works, semantic works
        mock_infinite_results = self.create_mock_infinite_search_results()
        mock_semantic_results = self.create_mock_semantic_search_results()

        with patch.object(self.gemini_service, 'excel_function_search',
                        new_callable=AsyncMock, side_effect=Exception("Database connection error")), \
            patch.object(self.gemini_service, '_infinite_search_user_symbols',
                        new_callable=AsyncMock, return_value=mock_infinite_results), \
            patch.object(self.gemini_service, 'semantic_similarity_search',
                        new_callable=AsyncMock, return_value=mock_semantic_results):

            result = await self.gemini_service.hybrid_lexical_search(
                query=query,
                user_id=user_id,
                excel_context=excel_context,
                limit=5
            )

            # ASSERT: Should work with 2 out of 3 strategies
            assert result is not None, "Should return results despite finite failure"
            assert len(result['finite_search_results']) == 0, "Finite search should fail"
            assert len(result['infinite_search_results']) == 2, "Infinite search should work"
            assert len(result['semantic_search_results']) == 2, "Semantic search should work"

            strategies = result['search_metadata']['search_strategies']
            assert 'finite_search' not in strategies, "Finite search should be skipped due to error"
            assert 'infinite_search' in strategies, "Infinite search should be recorded"
            assert 'semantic_search' in strategies, "Semantic search should be recorded"

            print("✅ SUCCESS: System handles finite search failures gracefully!")

    @pytest.mark.asyncio
    async def test_hybrid_search_infinite_failure(self):
        """
        Test Case 3: System handles gracefully when infinite search fails
        Finite ✅ + Infinite ❌ + Semantic ✅
        """
        query = "calculate totals"
        user_id = "test_user_101"
        excel_context = ExcelContext(sheet_name="Sheet1")

        # Mock scenario: Finite works, infinite FAILS, semantic works
        mock_finite_results = self.create_mock_finite_search_results()
        mock_semantic_results = self.create_mock_semantic_search_results()

        with patch.object(self.gemini_service, 'excel_function_search',
                        new_callable=AsyncMock, return_value=mock_finite_results), \
            patch.object(self.gemini_service, '_infinite_search_user_symbols',
                        new_callable=AsyncMock, side_effect=Exception("Symbol table error")), \
            patch.object(self.gemini_service, 'semantic_similarity_search',
                        new_callable=AsyncMock, return_value=mock_semantic_results):

            result = await self.gemini_service.hybrid_lexical_search(
                query=query,
                user_id=user_id,
                excel_context=excel_context,
                limit=5
            )

            # ASSERT: Should work with 2 out of 3 strategies
            assert result is not None, "Should return results despite infinite failure"
            assert len(result['finite_search_results']) == 2, "Finite search should work"
            assert len(result['infinite_search_results']) == 0, "Infinite search should fail"
            assert len(result['semantic_search_results']) == 2, "Semantic search should work"

            strategies = result['search_metadata']['search_strategies']
            assert 'finite_search' in strategies, "Finite search should be recorded"
            assert 'infinite_search' not in strategies, "Infinite search should be skipped due to error"
            assert 'semantic_search' in strategies, "Semantic search should be recorded"

            print("✅ SUCCESS: System handles infinite search failures gracefully!")

    @pytest.mark.asyncio
    async def test_hybrid_search_no_excel_context(self):
        """
        Test Case 4: System works when no Excel context is provided
        Tests fallback behavior when only finite + semantic search are available
        """
        query = "sum function"
        user_id = "user_789"
        excel_context = None #No excel context provided to skip infinite search

        mock_finite_results = self.create_mock_finite_search_results()
        mock_semantic_results = self.create_mock_semantic_search_results()

        with patch.object(self.gemini_service, 'excel_function_search',
                        new_callable=AsyncMock, return_value=mock_finite_results), \
            patch.object(self.gemini_service, 'semantic_similarity_search',
                        new_callable=AsyncMock, return_value=mock_semantic_results):

            result = await self.gemini_service.hybrid_lexical_search(
                query=query,
                user_id=user_id,
                excel_context=excel_context,
                limit=5
            )

            # ASSERT: Should work with only 2 strategies (finite + semantic)
            assert result is not None, "Should work without Excel context"
            assert len(result['finite_search_results']) == 2, "Finite search should work"
            assert len(result['infinite_search_results']) == 0, "No infinite search without context"
            assert len(result['semantic_search_results']) == 2, "Semantic search should work"

            strategies = result['search_metadata']['search_strategies']
            assert 'finite_search' in strategies, "Finite search should be recorded"
            assert 'semantic_search' in strategies, "Semantic search should be recorded"
            assert 'infinite_search' not in strategies, "Infinite search should be skipped"
            assert result['search_metadata']['has_excel_context'] is False

            print("✅ SUCCESS: System works without Excel context!")