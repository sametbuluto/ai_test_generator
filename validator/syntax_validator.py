"""
Syntax Validator Module
=======================
Validates generated test code for syntactic correctness.
"""

import ast
import logging
import re

logger = logging.getLogger(__name__)


class SyntaxValidator:
    """Validates Python test code syntax before execution."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate(self, test_code: str) -> dict:
        """
        Validate test code syntax.
        
        Returns:
            dict with keys: is_valid, errors, warnings, cleaned_code
        """
        result = {"is_valid": False, "errors": [], "warnings": [], "cleaned_code": ""}
        
        if not test_code or not test_code.strip():
            result["errors"].append("Empty test code")
            return result
        
        # Check for unsafe operations
        unsafe = self._check_unsafe_operations(test_code)
        if unsafe:
            result["warnings"].extend(unsafe)
        
        # Try to compile
        try:
            compile(test_code, "<generated_test>", "exec")
            result["is_valid"] = True
            result["cleaned_code"] = test_code
        except SyntaxError as e:
            result["errors"].append(f"Syntax error at line {e.lineno}: {e.msg}")
            # Try to fix common issues
            fixed = self._attempt_fix(test_code)
            if fixed:
                try:
                    compile(fixed, "<generated_test>", "exec")
                    result["is_valid"] = True
                    result["cleaned_code"] = fixed
                    result["warnings"].append("Code was auto-fixed")
                except SyntaxError:
                    pass
        
        # Verify test functions exist
        if result["is_valid"]:
            tree = ast.parse(result["cleaned_code"])
            test_funcs = [
                n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
            ]
            if not test_funcs:
                result["warnings"].append("No test functions (starting with test_) found")
            else:
                result["test_count"] = len(test_funcs)
        
        return result
    
    def _check_unsafe_operations(self, code: str) -> list:
        """Check for potentially unsafe operations in generated code."""
        warnings = []
        unsafe_patterns = [
            (r'\bos\.(remove|rmdir|unlink|system)\b', "File system modification detected"),
            (r'\bshutil\.(rmtree|move)\b', "Dangerous file operation detected"),
            (r'\bsubprocess\.(run|call|Popen)\b', "Subprocess execution detected"),
            (r'\beval\s*\(', "eval() usage detected"),
            (r'\bexec\s*\(', "exec() usage detected"),
            (r'\b__import__\s*\(', "Dynamic import detected"),
            (r'\bopen\s*\(.+["\']w', "File write operation detected"),
        ]
        for pattern, msg in unsafe_patterns:
            if re.search(pattern, code):
                warnings.append(f"⚠️ {msg}")
        return warnings
    
    def _attempt_fix(self, code: str) -> str:
        """Attempt to fix common syntax issues."""
        lines = code.splitlines()
        fixed_lines = []
        
        for line in lines:
            # Remove markdown artifacts
            if line.strip().startswith("```"):
                continue
            fixed_lines.append(line)
        
        return "\n".join(fixed_lines)
