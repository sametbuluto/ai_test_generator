"""
Duplicate Remover Module
=========================
Removes redundant and duplicate test cases.

Academic Concepts:
- Code Deduplication
- Test Suite Minimization
- Redundancy Analysis
"""

import ast
import hashlib
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class DuplicateRemover:
    """
    Removes duplicate and redundant test cases.
    
    Detection methods:
    1. Exact duplicate detection (hash-based)
    2. Structural duplicate detection (AST-based)
    3. Semantic similarity detection (name-based)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def remove_duplicates(self, test_code: str) -> dict:
        """
        Remove duplicate tests from code.
        
        Returns:
            dict with cleaned_code, removed_count, removed_tests
        """
        result = {
            "cleaned_code": test_code,
            "removed_count": 0,
            "removed_tests": [],
            "original_count": 0,
            "final_count": 0
        }
        
        try:
            tree = ast.parse(test_code)
        except SyntaxError:
            return result
        
        # Collect all test functions
        test_funcs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                test_funcs.append(node)
        
        result["original_count"] = len(test_funcs)
        
        # Detect duplicates using multiple methods
        keep = set()
        remove = set()
        seen_hashes = {}
        seen_structures = {}
        
        for func in test_funcs:
            # Method 1: Exact hash
            func_code = ast.dump(func)
            code_hash = hashlib.md5(func_code.encode()).hexdigest()
            
            # Method 2: Structural hash (ignoring names)
            struct_hash = self._structural_hash(func)
            
            if code_hash in seen_hashes:
                remove.add(func.name)
                result["removed_tests"].append(
                    f"{func.name} (exact duplicate of {seen_hashes[code_hash]})"
                )
            elif struct_hash in seen_structures:
                remove.add(func.name)
                result["removed_tests"].append(
                    f"{func.name} (structural duplicate of {seen_structures[struct_hash]})"
                )
            else:
                keep.add(func.name)
                seen_hashes[code_hash] = func.name
                seen_structures[struct_hash] = func.name
        
        result["removed_count"] = len(remove)
        result["final_count"] = len(keep)
        
        # Remove duplicate functions from code
        if remove:
            result["cleaned_code"] = self._remove_functions(test_code, remove)
        
        return result
    
    def _structural_hash(self, func: ast.FunctionDef) -> str:
        """Generate a hash based on function structure (ignoring names)."""
        # Create a normalized version of the AST
        body_dump = ""
        for node in ast.walk(func):
            if isinstance(node, ast.Assert):
                body_dump += "ASSERT:"
                if node.test:
                    body_dump += ast.dump(node.test)
            elif isinstance(node, ast.Call):
                body_dump += "CALL:"
                if isinstance(node.func, ast.Name):
                    body_dump += node.func.id
                body_dump += str(len(node.args))
            elif isinstance(node, ast.Try):
                body_dump += "TRY"
        
        return hashlib.md5(body_dump.encode()).hexdigest()
    
    def _remove_functions(self, code: str, func_names: set) -> str:
        """Remove specified functions from code string."""
        lines = code.splitlines()
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code
        
        # Collect line ranges to remove
        ranges_to_remove = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in func_names:
                start = node.lineno - 1
                end = getattr(node, 'end_lineno', node.lineno)
                # Include any preceding blank lines/comments
                while start > 0 and (not lines[start - 1].strip() or lines[start - 1].strip().startswith('#')):
                    start -= 1
                ranges_to_remove.append((start, end))
        
        # Remove in reverse order
        ranges_to_remove.sort(reverse=True)
        for start, end in ranges_to_remove:
            del lines[start:end]
        
        # Clean up extra blank lines
        cleaned = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines))
        return cleaned.strip()
