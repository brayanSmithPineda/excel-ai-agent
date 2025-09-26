"""
Excel formula parser service for Phase 3.3 of Gemini AI Backend - Infinite Search Implementation
This service handles real-time parsing for excel formulas into AST (Abstract Syntax Trees)
Basically this abstraction allows us to search/find queries into the existing code/excel data base of the user

Example:
Users ask "Fix my IF statement" → We can parse their actual IF formulas and provide context-aware help
"""
from enum import Enum #Enum is a class that allows us to define a set of named values
from dataclasses import dataclass #dataclass is a class that allows us to define a class that has default values for its attributes
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import re
import formulas #Library for Excel formula parsing and AST generation


class SymbolType(Enum):
    """
     This class basically defines the type of symbols we can find/extract from the excel formulas
    """
    CELL_REFERENCE = "cell_reference" #Users can ask something about a cell like A1,$C$3
    RANGE_REFERENCE = "range_reference" #A1:B10, Sheet1!A1:B10
    FUNCTION_CALL = "function_call" #SUM()
    LITERAL_VALUE = "literal_value" #Where is the value 10 or 'Category 10' or the boleeans 
    NAMED_RANGE = "named_range" #user-defined names for example "Total Sales" for a specific range
    EXTERNAL_REFERENCE = "external_reference" #[Workbook.xlsx]Sheet!A1 Other workbook reference

@dataclass #This allows us to define a class that has default values for its attributes
class Symbol:
    """
    Represent a symbol extracted from Excel formulas
    """
    name: str #Name of the symbol (eg. "A1", "SUM", "MyRange")
    symbol_type : SymbolType #Type of the symbol (NAMED_RANGE, EXTERNAL_REFERENCE, etc)
    source_formula: str #The original formula this came from
    context: Dict[str, Any] #Context of the symbol (eg. sheet name, range, etc)
    dependencies: List[str] #Symbols this symbol depends on

class ExcelFormulaParser:
    """
    Core engine for parsing excel formulas into AST and extracting symbols.
    
    """
    def __init__(self):
        self.cache = {} # Will implement caching later
        self.symbol_registry = {} #Track all discovered symbols in the workbook
    
    def parse_formula(self, formula: str) -> Dict[str, Any]:
        """
        Pase an Excel formula into AST representation
        Our regex approach got the symbols like SUM, A1, B10.
        But the AST approach understand the formula structure and the relationships between the symbols.
        Knows that Understands that SUM is a FUNCTION that takes A1:A10 as an ARGUMENT
        Returns: Dict representing the AST data and metadata
        """
        try:
            #Clean and validate the formula
            clean_formula = formula.strip()
            if not clean_formula.startswith(('+', '=', '-')):
                clean_formula = '=' + clean_formula
            
            #Build the AST
            parser_result = formulas.Parser().ast(clean_formula)

            #Extract the builder (index 1 contains the userful AST data)
            ast_builder = parser_result[1] #the builder is the second element in the parser_result list

            #Compile the formula to get the AST node
            ast_node = ast_builder.compile()

            #Extract AST Information
            ast_data = {
                'original_formula': formula,
                'clean_formula': clean_formula,
                'ast_type': str(type(ast_node).__name__),
                'has_ast': ast_node is not None,
                'formula_length': len(clean_formula),
                'parsing_success': True
            }

            #Try to get more detail AST information if available
            if hasattr(ast_node, 'inputs'):
                #Inputs are the dependencies of the formula
                ast_data['inputs'] = list(ast_node.inputs) if ast_node.inputs else []
                ast_data['inputs_count'] = len(ast_data['inputs'])
            
            if hasattr(ast_node, 'function'):
                #If this is a function call, get the function name
                ast_data['primary_function'] = str(ast_node.function) if ast_node.function else None
            
            #Add complexity analysis based on the AST
            ast_data['ast_complexity'] = self._analyze_ast_complexity(ast_node)

            return ast_data
        except Exception as e:
            logger.error(f"Error parsing formula '{formula}': {e}")
            return {
                'original_formula': formula,
                'clean_formula': clean_formula,
                'parsing_success': False,
                'error_message': str(e),
                'error_type': type(e).__name__,
                'fallback_to_regex': True #Fallback to regex if AST parsing fails
            }

    def _analyze_ast_complexity(self, ast_node: Any) -> int:
        """
        The AST Complexity analyzer will help us to understand the complexity of the formula by examing its tree structure
        Returns: Integer complexity score (higher = more complex)
        """
        try:
            complexity = 0
            #1 - Count function calls (+2)
            if hasattr(ast_node, 'function') and ast_node.function:
                complexity += 2

            #2 - Count cell references (+1)
            if hasattr(ast_node, 'inputs') and ast_node.inputs:
                complexity += len(ast_node.inputs)
            

            #4 - Count complex functions (+2)
            if hasattr(ast_node, 'name'):
                function_name = str(ast_node.name).upper()
                complex_functions = ['SUM', 'IF', 'VLOOKUP', 'INDEX', 'MATCH', 'CONCATENATE', 'LEFT', 'RIGHT']
                if any(fun in function_name for fun in complex_functions):
                    complexity += 3
        except Exception as e:
            logger.error(f"Error analyzing AST complexity: {e}")
            return 1
        return max(complexity, 1)
        
    def extract_symbols(self, formula: str) -> List[Symbol]:
        """
        Extract all symbols (cell ref, functions, etc) from a formula 
        Returns the list of symbol objects found in the formula
        """
        try:
            if formula.startswith(('+', '=', '-')):
                formula_content = formula[1:].strip()
            else:
                formula_content = formula.strip()
            
            symbols = []
            
            #Extract ranges references (A1:B10, Sheet1!A1:C4)
            symbols.extend(self._extract_range_references(formula_content, formula))

            #Extract cell references (A1, $B$2, Sheet1!C3)
            symbols.extend(self._extract_cell_references(formula_content, formula, existing_symbols = symbols))

            #Extract function calls (SUM(), AVERAGE(), IF())
            symbols.extend(self._extract_function_calls(formula_content, formula))

            #Extract literals (100, "text", TRUE)
            symbols.extend(self._extract_literal_values(formula_content, formula))
            
            logger.info(f"Extracted {len(symbols)} symbols from formula: {formula}")
            return symbols
        except Exception as e:
            logger.error(f"Error extracting symbols from formula '{formula}': {e}")
            return []
    
    def _extract_cell_references(self, formula_content: str, original_formula: str, existing_symbols: List[Symbol] = None) -> List[Symbol]:
        """Extract cell references, excluding those already covered by range references
        
        Args:
            formula_content: The formula content to extract cell references from
            original_formula: The original formula
            existing_symbols: A list of existing symbols to exclude from the extraction
        
        Returns:
            A list of symbols extracted from the formula
        """
        symbols = []
        existing_symbols = existing_symbols or []

        #Get all renge addresses to exclude individual cells within ranges
        excluded_cells = set()
        for symbol in existing_symbols:
            if symbol.symbol_type == SymbolType.RANGE_REFERENCE:
                # Parse the range and get all cells within it
                range_cells = self._get_cells_in_range(symbol.name)
                excluded_cells.update(range_cells)

                #DEBUG: Let's see what's being excluded
                print(f"DEBUG: Range {symbol.name} excludes cells: {range_cells[:5]}...")

        print(f"DEBUG: Total excluded cells: {len(excluded_cells)}")

        cell_pattern = r"(?:'[^']*'!|\w+!)?(?:\$?[A-Z]+\$?\d+)" 

        matches = re.finditer(cell_pattern, formula_content, re.IGNORECASE)

        for match in matches:
            cell_ref = match.group(0) # group is a function that returns the matched group, for example if the formula is =SUM(A1:B10) the group will be A1:B10
            

            #Normalize the cell reference for comparison with excluded cells (remove $ signs and infer sheet context if needed for example if the cell reference is Sheet1!B100, it will be normalized to B100)
            normalized_cell_ref = self._normalize_cell_reference(cell_ref, existing_symbols)

            print(f"DEBUG: Checking cell {cell_ref} (normalized: {normalized_cell_ref}) against {len(excluded_cells)} excluded cells")

            #Skip if the cell is covered by an existing range
            if normalized_cell_ref in excluded_cells:
                print(f"DEBUG: EXCLUDED cell {cell_ref} because it's covered by an existing range")
                continue
            
            print(f"DEBUG: INCLUDED {cell_ref}")
            
            #Extract the context (sheet name if present)
            context = {}
            if '!' in cell_ref:
                sheet_part, cell_part = cell_ref.split('!',1)
                context['sheet_name'] =sheet_part.strip("'")
                context['cell_address'] = cell_part
            else:
                context['cell_address'] = cell_ref
            
            symbol = Symbol(
                name = cell_ref,
                symbol_type = SymbolType.CELL_REFERENCE,
                source_formula = original_formula,
                context = context,
                dependencies = [] #Cell references dont depend on other sysmbols
            )
            symbols.append(symbol)

        return symbols
    
    def _normalize_cell_reference(self, cell_ref: str, existing_symbols: List[Symbol]) -> str:
        """
        Normalize cell reference for comparison with excluded cells
        
        Args:
            cell_ref: Cell reference like 'B100', '$A$1', 'Sheet1!C1'
            existing_symbols: Existing symbols to infer sheet context
            
        Returns:
            Normalized cell reference for comparison
        """
        # Remove $ signs for comparison
        normalized = cell_ref.replace('$', '')

        # If no sheet prefix, try to infer from range context
        if '!' not in normalized:
            # Look for a range symbol to get sheet context
            for symbol in existing_symbols:
                if symbol.symbol_type == SymbolType.RANGE_REFERENCE and '!' in symbol.name:
                    sheet_part = symbol.name.split('!')[0]
                    normalized = f"{sheet_part}!{normalized}"
                    break

        return normalized

    def _get_cells_in_range(self, range_ref: str) -> List[str]:
        """Get all invidual cells within a range"""

        try:
            #Handle sheet references
            if '!' in range_ref:
                sheet_part, range_part = range_ref.split('!', 1)
                sheet_prefix = sheet_part + '!'
            else:
                #If no sheet reference, just use the range part
                range_part = range_ref
                sheet_prefix = ''
            
            #Parse the range part (A1:B2)
            if ':' not in range_part:
                #Single cell
                return [range_part]
            
            start_cell, end_cell = range_part.split(':',1) #split at most once

            #Parse start cell (remove $ signs)
            start_col, start_row = self._parse_cell_address(start_cell.replace('$',''))
            end_col, end_row = self._parse_cell_address(end_cell.replace('$',''))

            cells = []

            #Generate all cells in that range
            for col in range(start_col, end_col + 1):
                for row in range(start_row, end_row + 1):
                    cell_address = self._column_number_to_letter(col) + str(row)
                    full_cell_ref = sheet_prefix + cell_address
                    cells.append(full_cell_ref)
            
            return cells
        except Exception as e:
            logger.error(f"Error getting cells in range '{range_ref}': {e}")
            return []
    
    def _column_number_to_letter(self, col_number: int) -> str:
        """
        Convert column number to Excel column letters
        
        Args:
            col_number: Column number (1=A, 2=B, 26=Z, 27=AA)
            
        Returns:
            Column letters like 'A', 'BC', etc.
        """
        result = ''
        while col_number > 0:
            col_number -= 1  # Make it 0-based
            result = chr(ord('A') + col_number % 26) + result
            col_number //= 26
        return result

    def _parse_cell_address(self, cell_address: str) -> tuple:
        """Parse a cell address like A1 or $B$2 into column number and row number like (1, 1) or (2, 2)"""
        #Separete letters (Which are the columns) from numbers (Which are the rows)
        col_letter = ''
        row_number = ''

        for char in cell_address:
            if char.isalpha(): #If the character is a letter, it is a column
                col_letter += char
            elif char.isdigit(): #If the character is a digit, it is a row
                row_number += char
        
        #Convert column letter to number (A=1, B=2, ..., Z=26, AA=27, etc.)
        col_number = 0
        for char in col_letter.upper():
            col_number = col_number * 26 + (ord(char) - ord('A') + 1)
        
        return col_number, int(row_number)

    def _extract_range_references(self, formula_content: str, original_formula: str) -> List[Symbol]:
        """Extract range references like A1:B10, Sheet1!A1:C5"""
        symbols = []

        # Pattern for range references: [Sheet!]Cell:Cell
        range_pattern = r"(?:'[^']*'!|\w+!)?(?:\$?[A-Z]+\$?\d+:\$?[A-Z]+\$?\d+)"

        matches = re.finditer(range_pattern, formula_content, re.IGNORECASE)

        for match in matches:
            range_ref = match.group(0)

            # Extract context
            context = {}
            if '!' in range_ref:
                sheet_part, range_part = range_ref.split('!', 1)
                context['sheet_name'] = sheet_part.strip("'")
                context['range_address'] = range_part
            else:
                context['range_address'] = range_ref

            # Parse start and end cells
            if ':' in range_ref:
                start_cell, end_cell = range_ref.split(':')[-2:]  # Take last 2 parts after any !
                context['start_cell'] = start_cell
                context['end_cell'] = end_cell

            symbol = Symbol(
                name=range_ref,
                symbol_type=SymbolType.RANGE_REFERENCE,
                source_formula=original_formula,
                context=context,
                dependencies=[]
            )
            symbols.append(symbol)

        return symbols

    def _extract_function_calls(self, formula_content: str, original_formula: str) -> List[Symbol]:
        """Extract function calls like SUM, IF, VLOOKUP"""
        symbols = []

        # Pattern for function calls: FunctionName(
        function_pattern = r"\b([A-Z][A-Z0-9_]*)\s*\("

        matches = re.finditer(function_pattern, formula_content, re.IGNORECASE)

        for match in matches:
            function_name = match.group(1).upper()

            context = {
                'function_name': function_name,
                'position_in_formula': match.start()
            }

            symbol = Symbol(
                name=function_name,
                symbol_type=SymbolType.FUNCTION_CALL,
                source_formula=original_formula,
                context=context,
                dependencies=[]  # Will be populated later when we analyze arguments
            )
            symbols.append(symbol)

        return symbols

    def _extract_literal_values(self, formula_content: str, original_formula: str) -> List[Symbol]:
        """Extract literal values like numbers, strings, booleans"""
        symbols = []

        # Pattern for string literals: "text" and 'text'
        string_pattern = r'''(?:"([^"]*)"|'([^']*)')'''  # Matches both " and '
        string_matches = re.finditer(string_pattern, formula_content)

        for match in string_matches:
            #Check which group matched (double quotes or single quotes)
            string_value = match.group(1) if match.group(1) is not None else match.group(2)
            quote_type = '"' if match.group(1) is not None else "'"

            context = {
                'value_type': 'string',
                'value': string_value,
                'quote_type': quote_type,
                'position_in_formula': match.start()
            }

            symbol = Symbol(
                name=f'{quote_type}{string_value}{quote_type}',
                symbol_type=SymbolType.LITERAL_VALUE,
                source_formula=original_formula,
                context=context,
                dependencies=[]
            )
            symbols.append(symbol)
        # Pattern for numbers (integers and decimals)
        number_pattern = r'\b(\d+(?:\.\d+)?)\b'
        number_matches = re.finditer(number_pattern, formula_content)

        for match in number_matches:
            number_value = match.group(1)

            context = {
                'value_type': 'number',
                'value': float(number_value) if '.' in number_value else int(number_value),
                'position_in_formula': match.start()
            }

            symbol = Symbol(
                name=number_value,
                symbol_type=SymbolType.LITERAL_VALUE,
                source_formula=original_formula,
                context=context,
                dependencies=[]
            )
            symbols.append(symbol)

        # Pattern for boolean values
        boolean_pattern = r'\b(TRUE|FALSE)\b'
        boolean_matches = re.finditer(boolean_pattern, formula_content, re.IGNORECASE)

        for match in boolean_matches:
            boolean_value = match.group(1).upper()

            context = {
                'value_type': 'boolean',
                'value': boolean_value == 'TRUE',
                'position_in_formula': match.start()
            }

            symbol = Symbol(
                name=boolean_value,
                symbol_type=SymbolType.LITERAL_VALUE,
                source_formula=original_formula,
                context=context,
                dependencies=[]
            )
            symbols.append(symbol)

        return symbols
    
    def validate_formula(self, formula: str) -> Dict[str, Any]:
        """
        Validate the formula syntax and structure
        Excel formula structure:
        1- Always start with + or = or -
        2- Can contains functions
        3- Can have cell references
        4- Can have ranges
        5- Can have literals, 100, "text", TRUE
        """
        try:
            formula = formula.strip()

            if not formula.startswith(('+', '=', '-')):
                return {
                    "is_valid": False,
                    "error_type": "missing_equal_plus_minus",
                    "error_message": "Formula must start with +, =, or -",
                    "formula": formula
                }
            #Remove the leading + or = or -
            formula_content = formula[1:]

            # Check for empty formula
            if not formula_content:
                return {
                    "is_valid": False,
                    "error_type": "empty_formula",
                    "error_message": "Formula cannot be empty after '='",
                    "formula": formula
                }

            # Check for balanced parentheses
            if not self._check_balanced_parentheses(formula_content):
                return {
                    "is_valid": False,
                    "error_type": "unbalanced_parentheses",
                    "error_message": "Formula has unbalanced parentheses",
                    "formula": formula
                }

            # Check for invalid characters (basic validation)
            invalid_chars = ['[', ']', '{', '}']  # Excel doesn't allow these in formulas
            for char in invalid_chars:
                if char in formula_content:
                    return {
                        "is_valid": False,
                        "error_type": "invalid_character",
                        "error_message": f"Formula contains invalid character: '{char}'",
                        "formula": formula
                    }

            # If we get here, basic validation passed
            return {
                "is_valid": True,
                "error_type": None,
                "error_message": None,
                "formula": formula,
                "formula_length": len(formula),
                "complexity_score": self._calculate_complexity(formula_content)
            }

        except Exception as e:
            logger.error(f"Error validating formula '{formula}': {e}")
            return {
                "is_valid": False,
                "error_type": "validation_error",
                "error_message": f"Validation failed: {str(e)}",
                "formula": formula
            }

    def _check_balanced_parentheses(self, formula_content: str) -> bool:
        """
        Check if parentheses are balanced in the formula
        
        Args:
            formula_content: Formula content without the leading =
            
        Returns:
            True if parentheses are balanced, False otherwise
        """
        # Count opening and closing parentheses
        open_count = 0

        for char in formula_content:
            if char == '(':
                open_count += 1
            elif char == ')':
                open_count -= 1
                # If we have more closing than opening, it's unbalanced
                if open_count < 0:
                    return False

        # Must end with zero (all opened parentheses were closed)
        return open_count == 0

    def _calculate_complexity(self, formula_content: str) -> int:
        """
        Calculate a simple complexity score for the formula
        
        Args:
            formula_content: Formula content without the leading =
            
        Returns:
            Integer complexity score (higher = more complex)
        """
        complexity = 0

        # Count nested function calls (each opening parenthesis adds complexity)
        complexity += formula_content.count('(')

        # Count cell references (pattern like A1, B2, etc.)
        cell_ref_pattern = r'\b[A-Z]+\d+\b'
        complexity += len(re.findall(cell_ref_pattern, formula_content))

        # Count range references (pattern like A1:B10)
        range_pattern = r'\b[A-Z]+\d+:[A-Z]+\d+\b'
        complexity += len(re.findall(range_pattern, formula_content)) * 2  # Ranges are more complex

        # Count common Excel functions
        functions = ['SUM', 'IF', 'VLOOKUP', 'INDEX', 'MATCH', 'CONCATENATE', 'LEFT', 'RIGHT']
        for func in functions:
            if func in formula_content.upper():
                complexity += 2  # Functions add significant complexity

        return complexity

@dataclass
class SymbolDefinition:
    """
    Enhanced symbol information including current value and metadata
    """
    symbol: Symbol #The original symbol object
    current_value: Any #The current value of the symbol (if known)
    data_type: str #The data type of the symbol (string, number, boolean, etc.)
    sheet_context: str #Which sheets the symbol is used in
    last_updated: datetime #The last time the symbol was updated
    is_volatile: bool = False #Whether the symbol is volatile (changes over time), does it change frequently like NOW(), TODAY(), RAND(), etc.

@dataclass
class ExcelContext:
    """
    Represents Excel  context for symbol resolution
    """
    sheet_name: str
    workbook_name: Optional[str] = None
    cell_address: Optional[str] = None

class DynamicSymbolTable:
    """
    Dynamic symbol table to track symbols and their relationships.
    This allows us to track symbols and their relationships as they are created/modified.

    With this track symbols we can basically have a real-time understand of the codebase/workbook like cursor does for code.
    an respond questions/queries about the codebase/workbook. like "Where are my Q1 Sales?" questions related to the codebase/workbook.
    """
    def __init__(self):
        #Main symbol registry: {symbol_name: SymbolDefinition}
        self.symbols = {}

        #Dependency graph: {symbol: set() set_of_dependencies}
        self.dependencies = {}

        #Reverse dependencies: {symbol: set_of_dependents}, basically the symbols that depend on this symbol
        self.dependents = {}

        # Sheet context tracking
        self.sheet_symbols = {} # {sheet_name: set_of_symbols}
    
        # Performance optimizations
        self.cache = {}

    def register_symbol(self, symbol: Symbol, context: ExcelContext, current_value: Any = None) -> None:
        """
        It adds new symbols to our table and track their relationships.
        """
        #Symbol key: create a unique key for the symbol (This allows us to track the symbol across sheets and workbooks)
        symbol_key = self._create_symbol_key(symbol.name, context)

        #Determine data type
        data_type = self._determine_data_type(symbol, current_value)

        #Create the symbol definition
        symbol_definition = SymbolDefinition(
            symbol=symbol,
            current_value=current_value,
            data_type=data_type,
            sheet_context=context.sheet_name,
            last_updated=datetime.utcnow(),
            is_volatile= self._is_volatile_symbol(symbol)
        )

        #Add to main symbol registry: self.symbols[symbol_key] = symbol_definition take the symbol_key and assign the symbol_definition to it. for example self.symbols['A1'] = symbol_definition, so symbol_key is 'A1' and symbol_definition is the symbol_definition object, the symbol_definition object would look like this: SymbolDefinition(symbol=Symbol(name='A1', symbol_type=SymbolType.CELL_REFERENCE, source_formula='A1', context={'sheet_name': 'Sheet1'}, dependencies=[]), current_value=None, data_type='number', sheet_context='Sheet1', last_updated=datetime.utcnow(), is_volatile=False)
        self.symbols[symbol_key] = symbol_definition

        #Update sheet tracking
        #Track which symbols belong to which sheet
        if context.sheet_name not in self.sheet_symbols:
            self.sheet_symbols[context.sheet_name] = set() #so if the sheet_name is not in the sheet_symbols dictionary, we create a new set for it
        self.sheet_symbols[context.sheet_name].add(symbol_key) #so we add the symbol_key to the set of symbols for the sheet_name

        #Intilize dependency tracking: Initilize empty dependency sets for this symbol
        if symbol_key not in self.dependencies:
            self.dependencies[symbol_key] = set()
        if symbol_key not in self.dependents:
            self.dependents[symbol_key] = set()
     
    def _create_symbol_key(self, symbol_name: str, context: ExcelContext) -> str:
        """
        Create unique key for symbol with sheet context, this ensure each symbol has a unique identifier across sheets and workbooks
        """
        #If symbol already contains a sheet referece (like Sheet1!A1), use it as is:
        if '!' in symbol_name:
            return symbol_name
        
        #Otherwise use a default
        sheet_name = context.sheet_name or "Unknown"

        symbol_key = f"{sheet_name}!{symbol_name}"

        return symbol_key

    def _determine_data_type(self, symbol: Symbol, current_value: Any) -> str:
        """
        Determine data type of the symbol type and value
        """
        #If we have a current value in the arguments, use that to determine the data type
        if current_value is not None:
            if isinstance(current_value, bool): #if the current value is a boolean
                return "boolean"
            elif isinstance(current_value, (int, float)): #if the current value is a number
                return "number"
            elif isinstance(current_value, str): #if the current value is a string
                return "text"
            
        #If no value, use symbol type to determine data type
        if symbol.symbol_type == SymbolType.LITERAL_VALUE:
            #check the context for value_type
            if 'value_type' in symbol.context:
                return symbol.context['value_type']
            return "literal"
        elif symbol.symbol_type == SymbolType.CELL_REFERENCE:
            return "cell"
        elif symbol.symbol_type == SymbolType.RANGE_REFERENCE:
            return "range"
        elif symbol.symbol_type == SymbolType.FUNCTION_CALL:
            return "function"
        elif symbol.symbol_type == SymbolType.NAMED_RANGE:
            return "named_range"
        elif symbol.symbol_type == SymbolType.EXTERNAL_REFERENCE:
            return "external_reference"
        else:
            return "unknown"

    def _is_volatile_symbol(self, symbol: Symbol) -> bool:
        """
        Check if the symbol is volatile
        """
        #List of volatile functions
        volatile_functions = {
          'NOW', 'TODAY', 'RAND', 'RANDBETWEEN',
          'OFFSET', 'INDIRECT', 'INFO', 'CELL'
        }

        #Check if this is a function call and if the function name is in the volatile_functions set
        if symbol.symbol_type == SymbolType.FUNCTION_CALL:
            return symbol.name.upper() in volatile_functions
      
        #Check if symbol's source formula contains a volatile function
        if hasattr(symbol, 'source_formula') and symbol.source_formula:
            formula_upper = symbol.source_formula.upper()
            for volatile_func in volatile_functions:
                if volatile_func + '(' in formula_upper:
                    return True
        
        return False
    
    def update_symbol(self, symbol_name: str, new_value: Any, context: ExcelContext) -> None:
        """
        Update an existing symbol's value and timestamp, this is called when the symbol's value changes
        for example when the user changes the value of a cell, we need to update the symbol's value and timestamp
        """
        #Create the symbol key
        symbol_key = self._create_symbol_key(symbol_name, context)

        #Check if symbol exists in our table
        if symbol_key not in self.symbols:
            logger.warning(f"Attempting to update non-existent symbol: {symbol_key}")
            return
        
        #Get the existing symbol definition
        symbol_definition = self.symbols[symbol_key]

        #Update the symbol definition
        symbol_definition.current_value = new_value
        symbol_definition.last_updated = datetime.utcnow()

        #Update datatype if the value type changed
        symbol_definition.data_type = self._determine_data_type(symbol_definition.symbol, new_value)

        #Clear any cached results that might be affected by this change
        self._invalidate_cache_for_symbol(symbol_key)

        logger.info(f"Updated symbol: {symbol_key} with new value: {new_value}")
    
    def _invalidate_cache_for_symbol(self, symbol_key: str) -> None:
        """
        Clear cached results that might be affected by a symbol change
        This ensures our cache stays consistent when symbols are updated
        
        Args:
            symbol_key: The symbol key that was updated
        """
        # Remove any cache entries that might be affected
        # For now, we'll implement a simple approach: clear cache entries containing this symbol
        keys_to_remove = []
        for cache_key in self.cache:
            if symbol_key in cache_key:
                keys_to_remove.append(cache_key)

        for key in keys_to_remove:
            del self.cache[key]

        if keys_to_remove:
            logger.debug(f"Invalidated {len(keys_to_remove)} cache entries for symbol {symbol_key}")

    def resolve_symbol(self, symbol_name: str, context: ExcelContext) -> Optional[SymbolDefinition]:
        """
        Find and return the symbol definition for a given symbol name and context
        This is to get the symbol definition for a given symbol name and context.
        """
        # Create the symbol key
        symbol_key = self._create_symbol_key(symbol_name, context)

        # Try to find the symbol in our registry
        if symbol_key in self.symbols:
            return self.symbols[symbol_key]

        # If not found with full context, try without sheet context (for functions)
        if context.sheet_name and '!' not in symbol_name:
            # Try looking for the symbol without sheet prefix (for global functions)
            if symbol_name in self.symbols:
                return self.symbols[symbol_name]

        # Symbol not found
        logger.debug(f"Symbol not found: {symbol_key}")
        return None

    def add_dependency(self, dependent_symbol: str, dependency_symbol: str, context: ExcelContext) -> None:
        """
        Add a dependency relationship between two symbols
        This records that dependent_symbol depends on dependency_symbol
        
        Args:
            dependent_symbol: The symbol that depends on another (e.g., "B1" in "=A1*2")  
            dependency_symbol: The symbol being depended upon (e.g., "A1")
            context: Excel context for proper symbol key generation
        """
        # Create symbol keys for both symbols
        dependent_key = self._create_symbol_key(dependent_symbol, context)
        dependency_key = self._create_symbol_key(dependency_symbol, context)

        # Add to dependencies: dependent_key depends on dependency_key
        if dependent_key not in self.dependencies:
            self.dependencies[dependent_key] = set()
        self.dependencies[dependent_key].add(dependency_key)

        # Add to reverse dependencies: dependency_key is depended upon by dependent_key
        if dependency_key not in self.dependents:
            self.dependents[dependency_key] = set()
        self.dependents[dependency_key].add(dependent_key)

        logger.debug(f"Added dependency: {dependent_key} depends on {dependency_key}")

    def find_dependencies(self, symbol_name: str, context: ExcelContext) -> List[str]:
        """
        Find all symbols that this symbol depends on
        
        Args:
            symbol_name: Name of the symbol to analyze
            context: Excel context for proper symbol key generation
            
        Returns:
            List of symbol keys that this symbol depends on
        """
        symbol_key = self._create_symbol_key(symbol_name, context)

        if symbol_key in self.dependencies:
            return list(self.dependencies[symbol_key])
        return []

    def find_dependents(self, symbol_name: str, context: ExcelContext) -> List[str]:
        """
        Find all symbols that depend on this symbol
        
        Args:
            symbol_name: Name of the symbol to analyze  
            context: Excel context for proper symbol key generation
            
        Returns:
            List of symbol keys that depend on this symbol
        """
        symbol_key = self._create_symbol_key(symbol_name, context)

        if symbol_key in self.dependents:
            return list(self.dependents[symbol_key])
        return []