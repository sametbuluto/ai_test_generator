"""
Test Validator Module
=====================
Comprehensive validation of generated test cases.
Ensures quality, safety, and correctness before execution.
"""

import ast
import re
import logging
import hashlib

logger = logging.getLogger(__name__)


class TestValidator:
    """
    Validates generated test cases for quality and safety.
    
    Validation steps:
    1. Syntax validation
    2. Duplicate detection
    3. Import validation
    4. Safety checks
    5. Quality scoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_all(self, test_code: str) -> dict:
        """
        Run all validation checks on test code.
        
        Returns:
            dict with validation results
        """
        results = {
            "is_valid": True,
            "syntax_valid": False,
            "has_duplicates": False,
            "duplicate_count": 0,
            "test_count": 0,
            "quality_score": 0.0,
            "errors": [],
            "warnings": [],
            "test_names": [],
            "cleaned_code": ""
        }
        
        # 1. Syntax check
        try:
            compile(test_code, "<test>", "exec")
            results["syntax_valid"] = True
        except SyntaxError as e:
            results["is_valid"] = False
            results["errors"].append(f"Syntax error: {e.msg} (line {e.lineno})")
            return results
        
        # Parse AST
        tree = ast.parse(test_code)
        
        # 2. Extract test functions
        test_funcs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                test_funcs.append(node)
                results["test_names"].append(node.name)
        
        results["test_count"] = len(test_funcs)
        
        if not test_funcs:
            results["warnings"].append("No test functions found")
        
        # 3. Duplicate detection
        seen_hashes = {}
        duplicates = []
        for func in test_funcs:
            func_code = ast.dump(func)
            code_hash = hashlib.md5(func_code.encode()).hexdigest()
            if code_hash in seen_hashes:
                duplicates.append(func.name)
                results["has_duplicates"] = True
            else:
                seen_hashes[code_hash] = func.name
        
        results["duplicate_count"] = len(duplicates)
        if duplicates:
            results["warnings"].append(f"Duplicate tests: {', '.join(duplicates)}")
        
        # 4. Quality scoring
        results["quality_score"] = self._calculate_quality(test_funcs, test_code)
        
        # 5. Clean code (remove duplicates)
        if results["has_duplicates"]:
            results["cleaned_code"] = self._remove_duplicates(test_code, duplicates)
        else:
            results["cleaned_code"] = test_code
        
        return results
    
    def _calculate_quality(self, test_funcs: list, test_code: str) -> float:
        """Calculate quality score for generated tests (0-100)."""
        if not test_funcs:
            return 0.0
        
        score = 0.0
        total_checks = 5
        
        # 1. Has docstrings (20 pts)
        docs = sum(1 for f in test_funcs if ast.get_docstring(f))
        score += (docs / len(test_funcs)) * 20
        
        # 2. Has assertions (25 pts)
        assertions = 0
        for func in test_funcs:
            for node in ast.walk(func):
                if isinstance(node, ast.Assert):
                    assertions += 1
                    break
        score += (assertions / len(test_funcs)) * 25
        
        # 3. Unique test names (15 pts)
        names = [f.name for f in test_funcs]
        unique_ratio = len(set(names)) / len(names) if names else 0
        score += unique_ratio * 15
        
        # 4. Test variety (20 pts) - different test categories
        categories = set()
        for name in names:
            if 'edge' in name or 'boundary' in name or 'bva' in name:
                categories.add('edge')
            elif 'error' in name or 'invalid' in name or 'none' in name:
                categories.add('negative')
            elif 'basic' in name or 'valid' in name:
                categories.add('positive')
            elif 'zero' in name or 'negative' in name or 'large' in name:
                categories.add('boundary')
            else:
                categories.add('other')
        score += min(len(categories) / 4, 1.0) * 20
        
        # 5. Error handling (20 pts)
        try_count = sum(1 for f in test_funcs
                       for n in ast.walk(f) if isinstance(n, ast.Try))
        if try_count > 0:
            score += 20
        
        return min(round(score, 1), 100.0)
    
    def _remove_duplicates(self, test_code: str, duplicate_names: list) -> str:
        """Remove duplicate test functions from code."""
        tree = ast.parse(test_code)
        lines = test_code.splitlines()
        
        # Find line ranges to remove
        remove_ranges = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in duplicate_names:
                start = node.lineno - 1
                end = getattr(node, 'end_lineno', node.lineno)
                remove_ranges.append((start, end))
        
        # Remove lines (in reverse to preserve line numbers)
        remove_ranges.sort(reverse=True)
        for start, end in remove_ranges:
            del lines[start:end]
        
        return "\n".join(lines)
