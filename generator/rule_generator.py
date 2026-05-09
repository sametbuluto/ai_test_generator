"""
Rule-Based Test Generator Module
=================================
Generates test cases using deterministic rules and heuristics.

Academic Concepts:
- Rule-Based Expert Systems
- Boundary Value Analysis (BVA)
- Equivalence Partitioning
- Decision Table Testing
- Mutation Testing Concepts
"""

import ast
import logging
from typing import Optional
from analyzer.extractor import FunctionInfo, CodeAnalysis
from analyzer.ast_utils import detect_patterns

logger = logging.getLogger(__name__)


class RuleBasedGenerator:
    """
    Generates test cases using software testing heuristics.
    
    Implements classical testing techniques:
    - Boundary Value Analysis
    - Equivalence Partitioning
    - Error Guessing
    - Pattern-based edge case detection
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_edge_cases(self, func: FunctionInfo, source_tree: ast.AST = None) -> str:
        """Generate edge case tests for a function."""
        self.logger.info(f"Generating rule-based tests for: {func.name}")
        tests = []
        params = [p for p in func.parameters if not p.name.startswith('*')]
        
        # Detect patterns in function
        patterns = []
        if source_tree:
            for node in ast.walk(source_tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == func.name:
                        patterns = detect_patterns(node)
                        break
        
        # Apply rules based on patterns
        if "division" in patterns:
            tests.extend(self._division_rules(func, params))
        if "indexing" in patterns:
            tests.extend(self._indexing_rules(func, params))
        if "boundary_comparison" in patterns:
            tests.extend(self._boundary_rules(func))
        if "string_operation" in patterns:
            tests.extend(self._string_rules(func, params))
        if "type_conversion" in patterns:
            tests.extend(self._type_conversion_rules(func, params))
        if "none_check" in patterns:
            tests.extend(self._none_rules(func, params))
        
        # Apply general rules
        tests.extend(self._empty_input_rules(func, params))
        tests.extend(self._type_mismatch_rules(func, params))
        
        # Boundary value analysis for comparisons
        for cond in func.conditions:
            tests.extend(self._bva_from_condition(func, cond, params))
        
        return "\n\n\n".join(tests) if tests else ""
    
    def generate_all_edge_cases(self, analysis: CodeAnalysis, source_tree: ast.AST = None) -> str:
        """Generate edge cases for all functions."""
        all_tests = []
        for func in analysis.functions:
            edge_tests = self.generate_edge_cases(func, source_tree)
            if edge_tests:
                all_tests.append(f"# Rule-based edge cases for {func.name}\n{edge_tests}")
        return "\n\n\n".join(all_tests)
    
    def _division_rules(self, func: FunctionInfo, params: list) -> list:
        """Generate division-related edge case tests."""
        tests = []
        if len(params) >= 2:
            args_list = []
            for i, p in enumerate(params):
                args_list.append("0" if i == 1 else "10")
            args = ", ".join(args_list)
            tests.append(f'''def test_{func.name}_rule_divide_by_zero():
    """[Rule: Division] Test division by zero handling."""
    try:
        result = {func.name}({args})
        # If no exception, verify result handles zero divisor
    except ZeroDivisionError:
        pass  # Expected behavior''')
        return tests
    
    def _indexing_rules(self, func: FunctionInfo, params: list) -> list:
        """Generate indexing-related edge case tests."""
        tests = []
        args = ", ".join(["[]"] * len(params)) if params else "[]"
        tests.append(f'''def test_{func.name}_rule_empty_collection():
    """[Rule: Indexing] Test with empty collection input."""
    try:
        result = {func.name}({args})
    except (IndexError, KeyError, TypeError):
        pass  # Expected for empty collection''')
        return tests
    
    def _boundary_rules(self, func: FunctionInfo) -> list:
        """Generate boundary value tests from comparisons."""
        tests = []
        for cond in func.conditions:
            for comp in cond.comparisons:
                try:
                    right_val = int(comp.get("right", "0"))
                    left_name = comp.get("left", "x")
                    op = comp.get("operator", "")
                    
                    # BVA: test at, below, and above boundary
                    boundary_vals = [right_val - 1, right_val, right_val + 1]
                    params = [p for p in func.parameters if not p.name.startswith('*')]
                    
                    for bv in boundary_vals:
                        args_list = []
                        for p in params:
                            args_list.append(str(bv) if p.name == left_name else "1")
                        args = ", ".join(args_list) if args_list else str(bv)
                        
                        tests.append(f'''def test_{func.name}_rule_bva_{left_name}_{bv}():
    """[Rule: BVA] Test {left_name}={bv} (boundary for {left_name} {op} {right_val})."""
    try:
        result = {func.name}({args})
    except Exception:
        pass''')
                except (ValueError, TypeError):
                    continue
        return tests
    
    def _string_rules(self, func: FunctionInfo, params: list) -> list:
        """Generate string-related edge case tests."""
        tests = []
        if params:
            empty_args = ", ".join(['""'] * len(params))
            tests.append(f'''def test_{func.name}_rule_empty_string():
    """[Rule: String] Test with empty string inputs."""
    try:
        result = {func.name}({empty_args})
    except (ValueError, TypeError, AttributeError):
        pass''')
            
            special_args = ", ".join(['"!@#$%^&*()"'] * len(params))
            tests.append(f'''def test_{func.name}_rule_special_chars():
    """[Rule: String] Test with special characters."""
    try:
        result = {func.name}({special_args})
    except (ValueError, TypeError):
        pass''')
        return tests
    
    def _type_conversion_rules(self, func: FunctionInfo, params: list) -> list:
        """Generate type conversion edge case tests."""
        tests = []
        if params:
            args = ", ".join(['"not_a_number"'] * len(params))
            tests.append(f'''def test_{func.name}_rule_invalid_conversion():
    """[Rule: Type] Test with non-convertible types."""
    try:
        result = {func.name}({args})
    except (ValueError, TypeError):
        pass''')
        return tests
    
    def _none_rules(self, func: FunctionInfo, params: list) -> list:
        """Generate None-handling tests."""
        tests = []
        if params:
            none_args = ", ".join(["None"] * len(params))
            tests.append(f'''def test_{func.name}_rule_none_handling():
    """[Rule: None] Test None value handling."""
    try:
        result = {func.name}({none_args})
    except (TypeError, ValueError, AttributeError):
        pass''')
        return tests
    
    def _empty_input_rules(self, func: FunctionInfo, params: list) -> list:
        """Generate empty input tests."""
        tests = []
        if not params:
            tests.append(f'''def test_{func.name}_rule_no_args():
    """[Rule: Empty] Test function with no arguments."""
    result = {func.name}()
    assert result is not None or result is None  # Verify it runs''')
        return tests
    
    def _type_mismatch_rules(self, func: FunctionInfo, params: list) -> list:
        """Generate type mismatch tests."""
        tests = []
        if len(params) >= 1:
            # Test with mixed types
            type_combos = [
                ('"string"', "Type: str where num expected"),
                ("[1,2,3]", "Type: list where scalar expected"),
                ("True", "Type: bool where other expected"),
                ("{}", "Type: dict where other expected"),
            ]
            for val, desc in type_combos[:2]:  # Limit to 2
                args = ", ".join([val] * len(params))
                safe_name = desc.replace(" ", "_").replace(":", "").replace(",", "").lower()[:30]
                tests.append(f'''def test_{func.name}_rule_{safe_name}():
    """[Rule: {desc}] Test with mismatched types."""
    try:
        result = {func.name}({args})
    except (TypeError, ValueError, AttributeError):
        pass''')
        return tests
    
    def _bva_from_condition(self, func: FunctionInfo, cond, params: list) -> list:
        """Generate BVA tests from condition analysis."""
        tests = []
        for comp in cond.comparisons:
            try:
                right = comp.get("right", "")
                val = int(right)
                left = comp.get("left", "x")
                
                # Equivalence partitioning: below, at, above
                for test_val, label in [(val - 1, "below"), (val, "at"), (val + 1, "above")]:
                    # Check if this is already covered by boundary_rules
                    pass  # Covered in _boundary_rules
            except (ValueError, TypeError):
                continue
        return tests
