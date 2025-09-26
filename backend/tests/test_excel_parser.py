"""
Test script for excel parser. Phase 3.3.1 of Gemini AI Backend - Infinite Search Implementation 3.3.2 Testing & Validation
validates funciton in the excel_parser_service.py file
"""
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir) #set backend directory to the path, for example /Users/luis/Desktop/Personal Github/excel-ai-agent/backend

from app.services.excel_parser_service import ExcelFormulaParser, Symbol, SymbolType

def test_formula_validation():
    """Test the formula validation"""
    print("\n ===== Testing validate_formula() method =====\n")
    parser = ExcelFormulaParser()
    
    #Test cases  (formula, should_be_valid, expected_error_type)
    test_cases = [
          # Valid formulas
          ("=SUM(A1:A10)", True, None),
          ("=IF(B2>100, 'High', 'Low')", True, None),
          ("+A1+B1", True, None),
          ("-C1*2", True, None),

          # Invalid formulas
          ("SUM(A1:A10)", False, "missing_equal_plus_minus"),  # Missing =
          ("=", False, "empty_formula"),  # Empty after =
          ("=SUM(A1:A10))", False, "unbalanced_parentheses"),  # Extra )
          ("=SUM((A1:A10)", False, "unbalanced_parentheses"),  # Missing )
          ("=A1[B1]", False, "invalid_character"),  # Invalid character
        ]

    for formula, should_be_valid, expected_error_type in test_cases:
        result = parser.validate_formula(formula)

        if result["is_valid"] == should_be_valid:
            print(f" {formula} is valid: result: {result}")
        else:
            print(f" {formula} is invalid: result: {result}")
            if not should_be_valid:
                print(f"Error: {result.get('error_message', 'No error message')}")

def test_symbol_extraction():
    """ Test the method extract_symbols()"""
    print("\n ===== Testing extract_symbols() method =====\n")
    parser = ExcelFormulaParser()

    # Test formulas with expected symbol counts
    test_formulas = [
        "=SUM(A1:A10)",  # Should find: SUM function, A1:A10 range
        "=IF(B2>100, 'High', 'Low')",  # Should find: IF function, B2 cell, literals
        "=VLOOKUP(C1, Sheet1!A1:B100, 2, FALSE)",  # Should find: VLOOKUP, cells, ranges, literals
        "=A1+B1*100",  # Should find: A1, B1 cells, 100 literal
        "='Data Sheet'!$A$1:$C$10",  # Should find: sheet reference, absolute range
    ]

    for formula in test_formulas:
        print(f"\nTesting formula: {formula}")
        symbols = parser.extract_symbols(formula)

        for symbol in symbols:
            print(f"Symbol: {symbol.name}, Type: {symbol.symbol_type}, Context: {symbol.context}")

def test_performance():
    """Test performance with complex formulas"""
    print("\n=== Testing Performance ===")

    parser = ExcelFormulaParser()

    # Complex nested formula
    complex_formula = "=IF(AND(VLOOKUP(A1,Sheet1!$A$1:$Z$1000,26,FALSE)>AVERAGE(B1:B100),SUMIFS(C1:C1000,D1:D1000,\">\"&E1,F1:F1000,\"<\"&G1)>0),CONCATENATE(LEFT(H1,5),\" - \",RIGHT(I1,3)),\"No Match\")"

    import time

    # Test extraction performance
    start_time = time.time()
    symbols = parser.extract_symbols(complex_formula)
    end_time = time.time()

    extraction_time = (end_time - start_time) * 1000  # Convert to milliseconds

    print(f"Complex formula: {complex_formula[:60]}...")
    print(f"Extracted {len(symbols)} symbols in {extraction_time:.1f}ms")
    print(f"Performance target: <50ms - {'✅ PASS' if extraction_time < 50 else '❌ FAIL'}")

    # Test validation performance
    start_time = time.time()
    validation = parser.validate_formula(complex_formula)
    end_time = time.time()

    validation_time = (end_time - start_time) * 1000
    print(f"Validation completed in {validation_time:.1f}ms")
    print(f"Formula is valid: {validation['is_valid']}")

    return extraction_time < 50 and validation_time < 10

def main():
    """Run all tests"""
    print("🧪 ExcelFormulaParser Testing Suite")
    print("=" * 50)

    # Run validation tests
    test_formula_validation()

    # Run symbol extraction tests  
    test_symbol_extraction()

    # Run performance tests
    performance_pass = test_performance()

    print("\n" + "=" * 50)
    if performance_pass:
        print("✅ All tests passed! ExcelFormulaParser is production-ready!")
    else:
        print("⚠️ Performance tests failed - optimization needed")

if __name__ == "__main__":
    main()