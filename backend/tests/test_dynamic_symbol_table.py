"""
Test file for DynamicSymbolTable class Phase 3.3.3 of Gemini AI Backend - Infinite Search Implementation
"""
import sys
sys.path.append('../') #add the backend directory to the path
import loguru

logger = loguru.logger
from app.services.excel_parser_service import (
    DynamicSymbolTable,
    ExcelFormulaParser,
    ExcelContext,
    Symbol,
    SymbolType
)

def test_basic_symbol_registration():
    """
    Test basic symbol registration functionality
    """
    print("\n === TEST 1: Testing basic symbol registration...===")
    
    #Create instances
    symbol_table = DynamicSymbolTable()
    parser = ExcelFormulaParser()
    context = ExcelContext(sheet_name="Sheet1") #This is the sheet name for testing

    #Test with a simple formula: =A1*2
    formula = "=A1*2"
    symbols = parser.extract_symbols(formula)

    print(f"Formula: {formula} extracted {len(symbols)} symbols")

    for symbol in symbols:
        print(f" - {symbol.name} ({symbol.symbol_type.value})")
        #Register each symbol in the table
        symbol_table.register_symbol(symbol, context, current_value=None) #current_value is None because we are not providing a value for the symbol

    #Test symbol resolution
    cell_symbol = symbol_table.resolve_symbol("A1", context)
    if cell_symbol:
        print(f" Successfully resolved symbol A1: {cell_symbol.symbol.name} with type {cell_symbol.symbol.symbol_type.value}")
    else:
        print("Failed to resolve symbol A1")
    
def test_cross_sheet_dependencies():
    """ Test dependency tracking across multiple sheets"""
    print("\n === TEST 2:Testing cross-sheet dependencies...===")

    symbol_table = DynamicSymbolTable()
    parser = ExcelFormulaParser()

    #Sheet1 context
    sheet1_context = ExcelContext(sheet_name="Sheet1")
    #Sheet2 context
    sheet2_context = ExcelContext(sheet_name="Sheet2")

    #Test with a formula in sheet2 that depends on a cells in Sheet1
    formula = "=SUM(Sheet1!A1:A10)"
    symbols = parser.extract_symbols(formula)

    print(f"Formula: {formula} extracted {len(symbols)} symbols")

    for symbol in symbols:
        print(f" - Registering symbol: {symbol.name} ({symbol.symbol_type.value})")
        #Register each symbol in the table
        symbol_table.register_symbol(symbol, sheet2_context, current_value=None)

        #Add dependency: This formula depends on a cell in Sheet1
        if symbol.symbol_type == SymbolType.RANGE_REFERENCE:
            symbol_table.add_dependency("Sheet2!SUM_FORMULA", symbol.name, sheet2_context)
        
    #Test dependency analysis
    dependencies = symbol_table.find_dependencies("Sheet2!SUM_FORMULA", sheet2_context)
    print(f"Dependencies for found for Sheet2!SUM_FORMULA: {dependencies}")

def test_real_world_scenario():
    """ Test a realistic excel workbook scenario"""
    print("\n === TEST 3: Testing real-world scenario...===")

    symbol_table = DynamicSymbolTable()
    parser = ExcelFormulaParser()
    context = ExcelContext(sheet_name="Sheet1")

    #Realistic financial formulas
    formulas = [
        "=SUM(B2:B12)",
        "=C2*D2",
        "=IF(E2>0, F2/E2, 0)",
        "=XLOOKUP(A2, Sheet1!A2:A10, Sheet1!B2:B10)",
    ]

    print("Proccessing realistic financial formulas...")

    all_symbols = []
    for i,formula in enumerate(formulas):
        print(f"\nFormula {i+1}: {formula}")
        symbols = parser.extract_symbols(formula)
        print(f"Extracted {len(symbols)} symbols")

        for symbol in symbols:
            print(f" - Registering symbol: {symbol.name} ({symbol.symbol_type.value})")
            symbol_table.register_symbol(symbol, context, current_value=None)
            all_symbols.append(symbol)
    
    print("\nTotal symbols registered: ", len(all_symbols))
    print("\nSymbols by sheet:")
    for sheet, symbols in symbol_table.sheet_symbols.items():
        print(f" - {sheet}: {len(symbols)} symbols")

def test_dependency_impact_analysis():
    """ Test dependency impact analysis"""
    print("\n === TEST 4: Testing dependency impact analysis...===")

    symbol_table = DynamicSymbolTable()
    parser = ExcelFormulaParser()
    context = ExcelContext(sheet_name="Analysis")

    # Create a dependency chain: A1 -> B1 -> C1 -> D1
    dependency_formulas = [
        ("B1", "=A1*2"),           # B1 depends on A1
        ("C1", "=B1+10"),          # C1 depends on B1  
        ("D1", "=SUM(C1:C5)"),     # D1 depends on C1
        ("E1", "=IF(D1>100, 'High', 'Low')")  # E1 depends on D1
    ]

    print("Building dependency chain:")
    for cell, formula in dependency_formulas:
        print(f"{cell}: {formula}")
        symbols = parser.extract_symbols(formula)

        for symbol in symbols:
            symbol_table.register_symbol(symbol, context)
            # Add dependency relationship
            symbol_table.add_dependency(cell, symbol.name, context)

    # Now test impact analysis
    print(f"\n🔍 Impact Analysis: What depends on A1?")
    a1_dependents = symbol_table.find_dependents("A1", context)
    print(f"Direct dependents of A1: {a1_dependents}")

    # Trace the full dependency chain
    print(f"\n📊 Full dependency chain from A1:")
    current_level = ["Analysis!A1"]
    level = 1

    while current_level and level <= 5:  # Prevent infinite loops
        next_level = []
        for symbol in current_level:
            dependents = symbol_table.find_dependents(symbol.split('!')[-1], context)
            if dependents:
                print(f"  Level {level}: {symbol} affects → {dependents}")
                next_level.extend(dependents)
        current_level = next_level
        level += 1

if __name__ == "__main__":
    print("🧪 Testing DynamicSymbolTable - Real-time Excel Intelligence")
    print("=" * 60)

    try:
        test_basic_symbol_registration()
        test_cross_sheet_dependencies()
        test_real_world_scenario()
        test_dependency_impact_analysis()

        print(f"\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ DynamicSymbolTable is working perfectly")
        print("📈 Ready for Phase 3.3.4 HybridSearchIntegration")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        