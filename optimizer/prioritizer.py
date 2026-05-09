"""
Test Prioritizer Module
========================
Ranks and prioritizes test cases by importance.

Academic Concepts:
- Test Case Prioritization (TCP)
- Risk-Based Testing
- Coverage-Based Prioritization
- Fault Detection Probability
"""

import ast
import logging
import re

logger = logging.getLogger(__name__)


class TestPrioritizer:
    """
    Prioritizes test cases based on multiple criteria.
    
    Scoring factors:
    1. Edge case coverage (high priority)
    2. Branch coverage impact
    3. Error handling verification
    4. Boundary value testing
    5. Code complexity correlation
    """
    
    PRIORITY_KEYWORDS = {
        "high": ["zero", "none", "null", "error", "exception", "boundary", "overflow",
                 "divide", "empty", "invalid", "negative", "crash", "fail"],
        "medium": ["edge", "special", "large", "small", "limit", "max", "min",
                   "string", "type", "convert", "format"],
        "low": ["basic", "simple", "valid", "normal", "positive", "default", "return"]
    }
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prioritize(self, test_code: str) -> dict:
        """
        Prioritize test cases and return ranked results.
        
        Returns:
            dict with prioritized tests and statistics
        """
        result = {
            "prioritized_tests": [],
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0,
            "total": 0,
            "prioritized_code": ""
        }
        
        try:
            tree = ast.parse(test_code)
        except SyntaxError:
            return result
        
        # Extract and score test functions
        scored_tests = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                score = self._score_test(node)
                priority = self._get_priority_label(score)
                docstring = ast.get_docstring(node) or ""
                
                scored_tests.append({
                    "name": node.name,
                    "score": score,
                    "priority": priority,
                    "docstring": docstring,
                    "line": node.lineno
                })
        
        # Sort by score (highest first)
        scored_tests.sort(key=lambda x: x["score"], reverse=True)
        
        result["prioritized_tests"] = scored_tests
        result["total"] = len(scored_tests)
        result["high_priority"] = sum(1 for t in scored_tests if t["priority"] == "High")
        result["medium_priority"] = sum(1 for t in scored_tests if t["priority"] == "Medium")
        result["low_priority"] = sum(1 for t in scored_tests if t["priority"] == "Low")
        
        # Reorder code by priority
        result["prioritized_code"] = self._reorder_code(test_code, scored_tests)
        
        return result
    
    def _score_test(self, func: ast.FunctionDef) -> float:
        """Score a test function (0-100)."""
        score = 50.0  # Base score
        name_lower = func.name.lower()
        
        # Keyword-based scoring
        for keyword in self.PRIORITY_KEYWORDS["high"]:
            if keyword in name_lower:
                score += 15
        for keyword in self.PRIORITY_KEYWORDS["medium"]:
            if keyword in name_lower:
                score += 8
        for keyword in self.PRIORITY_KEYWORDS["low"]:
            if keyword in name_lower:
                score += 3
        
        # Assertion count bonus
        assert_count = sum(1 for n in ast.walk(func) if isinstance(n, ast.Assert))
        score += min(assert_count * 5, 15)
        
        # Error handling test bonus
        try_count = sum(1 for n in ast.walk(func) if isinstance(n, ast.Try))
        if try_count > 0:
            score += 10
        
        # Docstring bonus
        if ast.get_docstring(func):
            score += 5
        
        # Rule-based test bonus (from rule generator)
        if "rule_" in name_lower:
            score += 10
        
        return min(score, 100.0)
    
    def _get_priority_label(self, score: float) -> str:
        """Convert score to priority label."""
        if score >= 75:
            return "High"
        elif score >= 55:
            return "Medium"
        else:
            return "Low"
    
    def _reorder_code(self, test_code: str, scored_tests: list) -> str:
        """Reorder test functions by priority."""
        try:
            tree = ast.parse(test_code)
        except SyntaxError:
            return test_code
        
        lines = test_code.splitlines()
        func_blocks = []
        
        for test_info in scored_tests:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == test_info["name"]:
                    start = node.lineno - 1
                    end = getattr(node, 'end_lineno', node.lineno)
                    block = "\n".join(lines[start:end])
                    func_blocks.append(f"# Priority: {test_info['priority']} (Score: {test_info['score']:.0f})\n{block}")
                    break
        
        return "\n\n\n".join(func_blocks)
