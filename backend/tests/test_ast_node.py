from app.services.excel_parser_service import ExcelFormulaParser
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

parser = ExcelFormulaParser()
result = parser.parse_formula("=SUM(A1:A10)")
print(result)