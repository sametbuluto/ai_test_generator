"""
AST Utility Functions
=====================
Helper functions for AST manipulation and analysis.

Provides reusable utilities for:
- AST node inspection
- Code complexity calculation
- Pattern matching in AST trees
- Source code reconstruction
"""

import ast
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def calculate_cyclomatic_complexity(node: ast.AST) -> int:
    """
    Calculate the cyclomatic complexity of an AST node.
    
    Cyclomatic complexity measures the number of linearly independent
    paths through a program's source code. Higher complexity indicates
    more test cases are needed for full branch coverage.
    
    Formula: M = E - N + 2P
    Simplified: Count decision points + 1
    
    Args:
        node: AST node to analyze
        
    Returns:
        Cyclomatic complexity score (integer >= 1)
    """
    complexity = 1
    
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For)):
            complexity += 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, ast.Assert):
            complexity += 1
        elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            complexity += 1
    
    return complexity


def get_all_names(node: ast.AST) -> list[str]:
    """
    Get all variable/function names referenced in an AST subtree.
    
    Args:
        node: AST node to search
        
    Returns:
        List of name strings
    """
    names = []
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            names.append(child.id)
    return names


def get_all_constants(node: ast.AST) -> list:
    """
    Get all constant values in an AST subtree.
    
    Args:
        node: AST node to search
        
    Returns:
        List of constant values
    """
    constants = []
    for child in ast.walk(node):
        if isinstance(child, ast.Constant):
            constants.append(child.value)
    return constants


def detect_patterns(node: ast.AST) -> list[str]:
    """
    Detect common code patterns for edge case generation.
    
    Patterns detected:
    - Division operations (potential divide-by-zero)
    - List/dict indexing (potential IndexError/KeyError)
    - String operations (potential empty string issues)
    - Type comparisons (potential type errors)
    - Boundary comparisons (boundary value analysis)
    - None comparisons (null reference patterns)
    - File operations (IO error patterns)
    - Recursion (stack overflow patterns)
    
    Args:
        node: AST node to analyze
        
    Returns:
        List of detected pattern names
    """
    patterns = []
    
    for child in ast.walk(node):
        # Division pattern
        if isinstance(child, ast.BinOp) and isinstance(child.op, (ast.Div, ast.FloorDiv, ast.Mod)):
            patterns.append("division")
        
        # Indexing pattern
        if isinstance(child, ast.Subscript):
            patterns.append("indexing")
        
        # Comparison patterns
        if isinstance(child, ast.Compare):
            for op in child.ops:
                if isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                    patterns.append("boundary_comparison")
                elif isinstance(op, (ast.Eq, ast.NotEq)):
                    patterns.append("equality_comparison")
                elif isinstance(op, (ast.Is, ast.IsNot)):
                    patterns.append("identity_comparison")
                elif isinstance(op, (ast.In, ast.NotIn)):
                    patterns.append("membership_test")
        
        # String method calls
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
            attr = child.func.attr
            if attr in ('split', 'strip', 'replace', 'find', 'index', 'upper', 'lower', 'join'):
                patterns.append("string_operation")
            elif attr in ('append', 'extend', 'insert', 'pop', 'remove'):
                patterns.append("list_operation")
            elif attr in ('get', 'keys', 'values', 'items', 'update'):
                patterns.append("dict_operation")
            elif attr in ('open', 'read', 'write', 'close'):
                patterns.append("file_operation")
        
        # Built-in function calls
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
            func_name = child.func.id
            if func_name in ('int', 'float', 'str', 'bool'):
                patterns.append("type_conversion")
            elif func_name in ('len', 'range', 'enumerate'):
                patterns.append("sequence_operation")
            elif func_name == 'open':
                patterns.append("file_operation")
            elif func_name in ('sorted', 'reversed', 'filter', 'map'):
                patterns.append("iterable_operation")
        
        # None comparison
        if isinstance(child, ast.Compare):
            for comparator in child.comparators:
                if isinstance(comparator, ast.Constant) and comparator.value is None:
                    patterns.append("none_check")
        
        # Recursion detection
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
            # Check if function calls itself (basic recursion detection)
            parent_func = _find_parent_function(node, child)
            if parent_func and isinstance(child.func, ast.Name):
                if child.func.id == parent_func.name:
                    patterns.append("recursion")
    
    return list(set(patterns))  # Remove duplicates


def _find_parent_function(
    root: ast.AST, target: ast.AST
) -> Optional[ast.FunctionDef]:
    """
    Find the parent function of a given AST node.
    
    Args:
        root: Root AST node to search from
        target: Target node to find parent for
        
    Returns:
        Parent FunctionDef node if found, None otherwise
    """
    for node in ast.walk(root):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if child is target:
                    return node
    return None


def extract_docstring(node: ast.FunctionDef) -> Optional[str]:
    """
    Extract docstring from a function definition.
    
    Args:
        node: Function definition AST node
        
    Returns:
        Docstring string if present, None otherwise
    """
    return ast.get_docstring(node)


def get_function_signature(node: ast.FunctionDef) -> str:
    """
    Reconstruct function signature from AST.
    
    Args:
        node: Function definition AST node
        
    Returns:
        Function signature string
    """
    try:
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        # Handle defaults
        num_defaults = len(node.args.defaults)
        if num_defaults > 0:
            offset = len(args) - num_defaults
            for i, default in enumerate(node.args.defaults):
                args[offset + i] += f"={ast.unparse(default)}"
        
        # Handle *args and **kwargs
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
        
        sig = f"def {node.name}({', '.join(args)})"
        
        # Return annotation
        if node.returns:
            sig += f" -> {ast.unparse(node.returns)}"
        
        return sig
    except Exception:
        return f"def {node.name}(...)"


def count_lines_of_code(source_code: str) -> dict:
    """
    Count different types of lines in source code.
    
    Args:
        source_code: Python source code string
        
    Returns:
        Dictionary with line counts by type
    """
    lines = source_code.splitlines()
    total = len(lines)
    blank = sum(1 for line in lines if not line.strip())
    comments = sum(1 for line in lines if line.strip().startswith('#'))
    code = total - blank - comments
    
    return {
        "total": total,
        "code": code,
        "blank": blank,
        "comments": comments
    }
