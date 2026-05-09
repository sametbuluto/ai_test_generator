"""
AST Parser Module
=================
Parses Python source code into an Abstract Syntax Tree (AST).
Provides the foundational analysis for the entire pipeline.

Academic Concepts:
- Abstract Syntax Tree (AST) construction
- Static Code Analysis
- Compiler Theory fundamentals
"""

import ast
import logging
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    """
    Represents the result of parsing Python source code.
    
    Attributes:
        tree: The AST tree object
        source_code: Original source code string
        is_valid: Whether the code was successfully parsed
        error_message: Error message if parsing failed
        line_count: Total number of lines in source code
        node_count: Total number of AST nodes
    """
    tree: Optional[ast.AST] = None
    source_code: str = ""
    is_valid: bool = False
    error_message: str = ""
    line_count: int = 0
    node_count: int = 0


class CodeParser:
    """
    Python Source Code Parser using AST module.
    
    This class provides static analysis capabilities by parsing
    Python source code into Abstract Syntax Trees for further
    analysis by downstream pipeline components.
    
    Design Pattern: Single Responsibility Principle
    Each method handles one specific parsing task.
    """
    
    def __init__(self):
        """Initialize the CodeParser."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def parse(self, source_code: str) -> ParseResult:
        """
        Parse Python source code into an AST.
        
        Args:
            source_code: Python source code as a string
            
        Returns:
            ParseResult containing the AST tree and metadata
        """
        result = ParseResult(source_code=source_code)
        
        if not source_code or not source_code.strip():
            result.error_message = "Empty source code provided"
            self.logger.warning(result.error_message)
            return result
        
        try:
            tree = ast.parse(source_code)
            result.tree = tree
            result.is_valid = True
            result.line_count = len(source_code.splitlines())
            result.node_count = self._count_nodes(tree)
            self.logger.info(
                f"Successfully parsed code: {result.line_count} lines, "
                f"{result.node_count} AST nodes"
            )
        except SyntaxError as e:
            result.error_message = f"Syntax Error at line {e.lineno}: {e.msg}"
            self.logger.error(result.error_message)
        except Exception as e:
            result.error_message = f"Unexpected parsing error: {str(e)}"
            self.logger.error(result.error_message)
        
        return result
    
    def parse_file(self, filepath: str) -> ParseResult:
        """
        Parse a Python file into an AST.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            ParseResult containing the AST tree and metadata
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source_code = f.read()
            return self.parse(source_code)
        except FileNotFoundError:
            result = ParseResult()
            result.error_message = f"File not found: {filepath}"
            self.logger.error(result.error_message)
            return result
        except IOError as e:
            result = ParseResult()
            result.error_message = f"IO Error reading file: {str(e)}"
            self.logger.error(result.error_message)
            return result
    
    def _count_nodes(self, tree: ast.AST) -> int:
        """
        Count the total number of nodes in an AST.
        
        Args:
            tree: AST tree to count nodes in
            
        Returns:
            Total number of AST nodes
        """
        count = 0
        for _ in ast.walk(tree):
            count += 1
        return count
    
    def get_function_nodes(self, tree: ast.AST) -> list:
        """
        Extract all function definition nodes from an AST.
        
        Args:
            tree: AST tree to search
            
        Returns:
            List of ast.FunctionDef nodes
        """
        return [
            node for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
    
    def get_class_nodes(self, tree: ast.AST) -> list:
        """
        Extract all class definition nodes from an AST.
        
        Args:
            tree: AST tree to search
            
        Returns:
            List of ast.ClassDef nodes
        """
        return [
            node for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        ]
    
    def validate_syntax(self, source_code: str) -> tuple[bool, str]:
        """
        Validate Python syntax without full parsing.
        
        Args:
            source_code: Python source code string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            compile(source_code, "<string>", "exec")
            return True, ""
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
