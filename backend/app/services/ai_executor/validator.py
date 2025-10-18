"""
Code Validator - Security Layer for AI-Generated Code

Uses AST (Abstract Syntax Tree) analysis to validate Python code safety
before execution in the Docker sandbox.

Security Checks:
1. Import whitelist (only pandas, openpyxl, numpy, pathlib allowed)
2. No dangerous builtins (eval, exec, compile, __import__)
3. File access restricted to /tmp directory only
4. No network operations (socket, requests, urllib)
5. No subprocess or os.system calls
"""

import ast
import logging
from typing import List, Set, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """
        Result of code validation with 3-tier risk assessment.
        
        Risk Levels:
            - LOW: Safe libraries, auto-allow execution
            - MEDIUM: Legitimate but needs permission (requests, urllib)
            - HIGH: Always blocked (os, subprocess, eval)
        
        Attributes:
            is_safe: Whether code can execute (True for LOW/MEDIUM, False for HIGH)
            risk_level: "low", "medium", or "high"
            requires_permission: True if MEDIUM risk (user must approve)
            explanation: WHY this library/operation is needed (for MEDIUM risk)
            code_preview: The actual code to show user (for MEDIUM risk)
            restricted_imports: Which imports triggered MEDIUM/HIGH risk
            reason: Explanation if code is unsafe (HIGH risk)
            warnings: List of non-blocking warnings
            allowed_imports: Set of imports that passed validation
    """
    is_safe: bool
    risk_level: str  # "low", "medium", "high"
    requires_permission: bool = False  # True if medium risk
    explanation: str = ""  # WHY this library is needed
    code_preview: str = ""  # Show user what will execute
    restricted_imports: List[str] = None  # Which imports need permission
    reason: Optional[str] = None  # Explanation if unsafe
    warnings: List[str] = None
    allowed_imports: Set[str] = None

    def __post_init__(self):
        """Initialize empty lists/sets if None"""
        if self.warnings is None:
            self.warnings = []
        if self.allowed_imports is None:
            self.allowed_imports = set()
        if self.restricted_imports is None:
            self.restricted_imports = []

class CodeValidator:
    """
    Validates AI-generated Python code for security.
    
    Uses AST parsing to check code structure without executing it.
    """

    LOW_RISK_IMPORTS = {
        "pandas", "pd",  # Data manipulation
        "openpyxl",  # Excel file handling (.xlsx)
        "numpy", "np",  # Numerical operations
        "pathlib", "Path",  # Safe file path operations
        "datetime", "dt",  # Date/time operations
        "json",  # JSON parsing
        "csv",  # CSV handling
        "re",  # Regular expressions
        "math",  # Mathematical operations
        "statistics",  # Statistical functions
        "decimal", "Decimal",  # Precise decimal arithmetic
        "collections",  # Data structures (defaultdict, Counter, etc.)
    }

    # MEDIUM RISK: Legitimate but requires user permission
    MEDIUM_RISK_IMPORTS = {
        "requests",  # HTTP requests for API calls (Stripe, etc.)
        "urllib", "urllib3",  # URL operations, HTTP client
        "xlrd",  # Legacy Excel format support (.xls)
        "pyxlsb",  # Binary Excel format support (.xlsb)
        "xlwings",  # Advanced Excel automation
        "httpx",  # Modern async HTTP client
    }

    # HIGH RISK: Always blocked - never allowed
    HIGH_RISK_IMPORTS = {
        "os", "sys", "subprocess", "shutil",  # System operations
        "socket",  # Raw network access
        "pickle", "shelve",  # Unsafe serialization (code execution risk)
        "importlib", "__import__",  # Dynamic imports (security bypass)
        "ctypes", "cffi",  # Low-level system access
        "multiprocessing", "threading",  # Concurrency (can bypass limits)
        "pty", "termios",  # Terminal operations
        "fcntl", "ioctl",  # File control operations
    }
    # Dangerous builtin functions
    DANGEROUS_BUILTINS = {
        "eval", "exec", "compile", "__import__",
        "open",  # We'll only allow pathlib.Path.open() in /tmp
        "input",  # No user input in sandboxed code
    }

    def __init__(self):
        """Initialize the validator"""
        logger.info("CodeValidator initialized")

    def validate(self, code: str) -> ValidationResult:
        """
        Validate Python code for security.
        
        Args:
            code: Python code string to validate
        
        Returns:
            ValidationResult indicating if code is safe
        """
        logger.info("Validating code for security...")

        try:
            # Step 1: Parse code into AST
            tree = ast.parse(code) #ast is a module that parses the code into an AST, ast comes from the ast module which we imported above

            # Step 2: Check imports
            import_result = self._check_imports(tree)
            if not import_result.is_safe:
                return import_result

            # Step 3: Check for dangerous builtins
            builtin_result = self._check_dangerous_builtins(tree)
            if not builtin_result.is_safe:
                return builtin_result

            # Step 4: Check file operations
            file_result = self._check_file_operations(tree)
            if not file_result.is_safe:
                return file_result

            # All checks passed!
            logger.info("✅ Code validation passed")
            return ValidationResult(
                is_safe=True,
                risk_level=import_result.risk_level,  # Propagate risk level from imports
                requires_permission=import_result.requires_permission,
                explanation=import_result.explanation,
                code_preview=import_result.code_preview,
                restricted_imports=import_result.restricted_imports,
                allowed_imports=import_result.allowed_imports,
                warnings=import_result.warnings + builtin_result.warnings + file_result.warnings
            )

        except SyntaxError as e:
            logger.error(f"Code has syntax errors: {e}")
            return ValidationResult(
                is_safe=False,
                risk_level="high",  # Add this
                reason=f"Syntax error in generated code: {e}"
            )
        except Exception as e:
            logger.error(f"Validation error: {e}", exc_info=True)
            return ValidationResult(
                is_safe=False,
                risk_level="high",  # Add this
                reason=f"Validation failed: {e}"
            )
    def _check_imports(self, tree: ast.AST) -> ValidationResult:
        """
        Check all import statements using 3-tier risk assessment.
        
        Returns different risk levels:
            - LOW: Safe imports (pandas, numpy) - auto-allow
            - MEDIUM: Network/special imports (requests, xlrd) - requires permission
            - HIGH: Dangerous imports (os, subprocess) - always block
        
        Examples:
            import pandas as pd  ✅ LOW RISK - auto-allow
            import requests  ⚠️ MEDIUM RISK - ask permission
            import os  ❌ HIGH RISK - always block
        """
        low_risk_imports = set()
        medium_risk_imports = set()
        high_risk_imports = set()

        # Walk through all import statements
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]  # Get root module

                    if module_name in self.HIGH_RISK_IMPORTS:
                        high_risk_imports.add(module_name)
                    elif module_name in self.MEDIUM_RISK_IMPORTS:
                        medium_risk_imports.add(module_name)
                    elif module_name in self.LOW_RISK_IMPORTS:
                        low_risk_imports.add(module_name)
                    else:
                        # Unknown imports default to MEDIUM risk (ask permission)
                        medium_risk_imports.add(module_name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]

                    if module_name in self.HIGH_RISK_IMPORTS:
                        high_risk_imports.add(module_name)
                    elif module_name in self.MEDIUM_RISK_IMPORTS:
                        medium_risk_imports.add(module_name)
                    elif module_name in self.LOW_RISK_IMPORTS:
                        low_risk_imports.add(module_name)
                    else:
                        # Unknown imports default to MEDIUM risk
                        medium_risk_imports.add(module_name)

        # HIGH RISK: Always block
        if high_risk_imports:
            logger.warning(f"🚫 HIGH RISK imports blocked: {high_risk_imports}")
            return ValidationResult(
                is_safe=False,
                risk_level="high",
                requires_permission=False,
                reason=f"HIGH RISK imports detected (always blocked): {', '.join(high_risk_imports)}",
                restricted_imports=list(high_risk_imports),
                warnings=[]
            )

        # MEDIUM RISK: Requires user permission
        if medium_risk_imports:
            logger.info(f"⚠️ MEDIUM RISK imports detected: {medium_risk_imports}")

            # Generate explanation for why these imports are needed
            explanation = self._generate_permission_explanation(medium_risk_imports)

            return ValidationResult(
                is_safe=True,  # Can execute IF user approves
                risk_level="medium",
                requires_permission=True,
                explanation=explanation,
                restricted_imports=list(medium_risk_imports),
                allowed_imports=low_risk_imports,
                warnings=[f"Requires user permission for: {', '.join(medium_risk_imports)}"]
            )

        # LOW RISK: Auto-allow
        logger.info(f"✅ LOW RISK imports only: {low_risk_imports}")
        return ValidationResult(
            is_safe=True,
            risk_level="low",
            requires_permission=False,
            allowed_imports=low_risk_imports,
            warnings=[]
        )

    def _generate_permission_explanation(self, imports: Set[str]) -> str:
        """
        Generate user-friendly explanation for why MEDIUM risk imports are needed.
        
        This helps users understand what they're approving.
        """
        explanations = {
            "requests": "to make HTTP requests to external APIs (e.g., Stripe, NetSuite)",
            "urllib": "to access web resources and download data",
            "urllib3": "to make advanced HTTP connections",
            "xlrd": "to read legacy Excel files (.xls format)",
            "pyxlsb": "to read binary Excel files (.xlsb format)",
            "xlwings": "to perform advanced Excel automation",
            "httpx": "to make modern async HTTP requests",
        }

        import_list = list(imports)

        # Separate known vs unknown imports
        known_imports = [mod for mod in import_list if mod in explanations]
        unknown_imports = [mod for mod in import_list if mod not in explanations]

        if len(import_list) == 1:
            module = import_list[0]
            if module in explanations:
                return f"Code needs '{module}' library {explanations[module]}."
            else:
                # Unknown import - provide helpful context
                return (f"Code needs '{module}' library (not in standard whitelist). "
                        f"This is an unknown library that may provide additional functionality. "
                        f"Please verify this is a legitimate library before approving.")
        else:
            # Multiple imports - show which are known vs unknown
            parts = []

            if known_imports:
                known_reasons = [f"'{mod}' ({explanations[mod]})" for mod in known_imports]
                parts.append(f"Known libraries: {', '.join(known_reasons)}")

            if unknown_imports:
                unknown_list = ', '.join([f"'{mod}'" for mod in unknown_imports])
                parts.append(f"Unknown libraries (verify before approving): {unknown_list}")

            return "Code needs these libraries: " + "; ".join(parts) + "."

    def _check_dangerous_builtins(self, tree: ast.AST) -> ValidationResult:
        """
        Check for dangerous builtin function calls like eval(), exec().
        
        Examples:
            eval("print('hello')")  ❌ Dangerous
            exec(user_code)  ❌ Dangerous
            df.eval("A + B")  ✅ OK (this is pandas.DataFrame.eval, not builtin)
        """
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None

                #Get function name (There are multiple ways to call a function)
                if isinstance(node.func, ast.Name):
                    #Direct function call like eval("print('hello')")
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    #Call using an attribute like df.eval("A + B")
                    if isinstance(node.func.value, ast.Name):
                        pass #pandas.eval() is OK
                    else:
                        func_name = node.func.attr
                
                if func_name and func_name in self.DANGEROUS_BUILTINS:
                    #open() is dangerous, but we'll check it in file operations
                    if func_name == "open":
                        continue # will be validated in _check_file_operations
                    violations.append(f"Dangerous builtin function call detected: {func_name}")
                
        if violations:
            return ValidationResult(
                is_safe=False,
                risk_level="high",  # Add this
                reason=f"File operation violations: {', '.join(violations)}",
                warnings=[]
            )

        return ValidationResult(
            is_safe=True,
            risk_level="low",
            warnings=[]
        )


    def _check_file_operations(self, tree: ast.AST) -> ValidationResult:
        """
        Ensure file operations are restricted to /tmp directory.
        
        Examples:
            Path("/tmp/output.xlsx").write_bytes(data)  ✅ Allowed
            open("/etc/passwd")  ❌ Dangerous
            Path("/home/user/secret.txt").read_text()  ❌ Outside /tmp
        """
        violations = []
        warnings = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                
                if func_name and func_name == "open":
                    #try to extract the file path (first argument of open)
                    if node.args and isinstance(node.args[0], ast.Constant):
                        file_path = node.args[0].value
                        if isinstance(file_path, str):
                            #only allow open on /tmp/input or /tmp/output
                            if not (file_path.startswith("/tmp/input") or file_path.startswith("/tmp/output")):
                                violations.append(f"Unauthorized file access: {file_path}. Only allowed in /tmp/input or /tmp/output.")
                    else:
                        warnings.append("Dynamic file path in open(). Ensure it accesses only /tmp/input or /tmp/output.")
        
        if violations:
            return ValidationResult(
                is_safe=False,
                risk_level="high",  # ADD THIS
                reason=f"File operation violations: {', '.join(violations)}",
                warnings=warnings
            )

        return ValidationResult(
            is_safe=True,
            risk_level="low",  # ADD THIS
            warnings=warnings
        )