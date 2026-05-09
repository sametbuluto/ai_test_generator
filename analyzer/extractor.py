"""
Code Feature Extractor Module
==============================
Extracts meaningful features from parsed AST for test generation.

This module implements the core intelligence of the static analysis
pipeline by identifying testable elements in source code.

Academic Concepts:
- Feature Extraction (analogous to NLP/ML feature engineering)
- Control Flow Analysis
- Data Flow Analysis
- Branch Analysis for coverage optimization
"""

import ast
import logging
from typing import Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ParameterInfo:
    """Information about a function parameter."""
    name: str
    default_value: Optional[Any] = None
    has_default: bool = False
    annotation: Optional[str] = None


@dataclass
class ConditionInfo:
    """Information about a conditional branch."""
    condition_text: str
    line_number: int
    condition_type: str = "if"  # if, elif, while
    comparisons: list = field(default_factory=list)


@dataclass
class ReturnInfo:
    """Information about a return statement."""
    return_text: str
    line_number: int
    returns_value: bool = True


@dataclass
class ExceptionInfo:
    """Information about exception handling."""
    exception_type: str
    line_number: int
    handler_type: str = "raise"  # raise, except


@dataclass
class LoopInfo:
    """Information about loop constructs."""
    loop_type: str  # for, while
    line_number: int
    iterator_text: str = ""


@dataclass
class FunctionInfo:
    """
    Comprehensive information about a Python function.
    
    This dataclass aggregates all extracted features from a single
    function, providing a complete picture for test generation.
    """
    name: str
    line_number: int
    end_line: int
    source_code: str = ""
    docstring: Optional[str] = None
    parameters: list[ParameterInfo] = field(default_factory=list)
    conditions: list[ConditionInfo] = field(default_factory=list)
    returns: list[ReturnInfo] = field(default_factory=list)
    exceptions: list[ExceptionInfo] = field(default_factory=list)
    loops: list[LoopInfo] = field(default_factory=list)
    is_async: bool = False
    decorators: list[str] = field(default_factory=list)
    complexity: int = 1  # Cyclomatic complexity
    calls: list[str] = field(default_factory=list)
    
    @property
    def branch_count(self) -> int:
        """Calculate total number of branches."""
        return len(self.conditions) + len(self.exceptions)
    
    @property
    def has_edge_cases(self) -> bool:
        """Check if function likely has edge cases."""
        return (
            len(self.conditions) > 0 or
            len(self.exceptions) > 0 or
            any(p.has_default for p in self.parameters)
        )


@dataclass
class CodeAnalysis:
    """
    Complete analysis result for a Python source file.
    
    Aggregates all extracted information into a single result object.
    """
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    global_variables: list[str] = field(default_factory=list)
    total_lines: int = 0
    total_functions: int = 0
    total_branches: int = 0
    avg_complexity: float = 0.0


class FeatureExtractor:
    """
    Extracts testable features from Python AST.
    
    This class implements the feature extraction pipeline that
    converts raw AST nodes into structured, actionable information
    for the test generation engine.
    
    Design Pattern: Visitor Pattern (via ast.NodeVisitor)
    """
    
    def __init__(self):
        """Initialize the FeatureExtractor."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract(self, tree: ast.AST, source_code: str) -> CodeAnalysis:
        """
        Extract all features from an AST.
        
        Args:
            tree: Parsed AST tree
            source_code: Original source code for reference
            
        Returns:
            CodeAnalysis containing all extracted features
        """
        analysis = CodeAnalysis()
        analysis.total_lines = len(source_code.splitlines())
        
        # Extract functions
        source_lines = source_code.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = self._extract_function(node, source_lines)
                analysis.functions.append(func_info)
            elif isinstance(node, ast.ClassDef):
                analysis.classes.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                analysis.imports.extend(self._extract_imports(node))
        
        # Calculate summary statistics
        analysis.total_functions = len(analysis.functions)
        analysis.total_branches = sum(f.branch_count for f in analysis.functions)
        if analysis.functions:
            analysis.avg_complexity = sum(
                f.complexity for f in analysis.functions
            ) / len(analysis.functions)
        
        self.logger.info(
            f"Extracted {analysis.total_functions} functions, "
            f"{analysis.total_branches} branches"
        )
        
        return analysis
    
    def _extract_function(
        self, node: ast.FunctionDef, source_lines: list[str]
    ) -> FunctionInfo:
        """
        Extract comprehensive information from a function definition.
        
        Args:
            node: AST FunctionDef node
            source_lines: Source code lines for extracting text
            
        Returns:
            FunctionInfo with all extracted features
        """
        # Get function source code
        start_line = node.lineno - 1
        end_line = getattr(node, 'end_lineno', node.lineno)
        func_source = "\n".join(source_lines[start_line:end_line])
        
        func_info = FunctionInfo(
            name=node.name,
            line_number=node.lineno,
            end_line=end_line,
            source_code=func_source,
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )
        
        # Extract docstring
        func_info.docstring = ast.get_docstring(node)
        
        # Extract parameters
        func_info.parameters = self._extract_parameters(node.args)
        
        # Extract decorators
        func_info.decorators = [
            ast.dump(d) for d in node.decorator_list
        ]
        
        # Walk through function body for detailed analysis
        complexity = 1
        for child in ast.walk(node):
            # Conditions
            if isinstance(child, ast.If):
                cond = self._extract_condition(child, "if")
                func_info.conditions.append(cond)
                complexity += 1
            elif isinstance(child, ast.While):
                cond = self._extract_condition(child, "while")
                func_info.conditions.append(cond)
                loop = LoopInfo(
                    loop_type="while",
                    line_number=child.lineno,
                    iterator_text=ast.dump(child.test)
                )
                func_info.loops.append(loop)
                complexity += 1
            elif isinstance(child, ast.For):
                loop = LoopInfo(
                    loop_type="for",
                    line_number=child.lineno,
                    iterator_text=self._safe_unparse(child.iter)
                )
                func_info.loops.append(loop)
                complexity += 1
            
            # Returns
            elif isinstance(child, ast.Return):
                ret = ReturnInfo(
                    return_text=self._safe_unparse(child.value) if child.value else "None",
                    line_number=child.lineno,
                    returns_value=child.value is not None
                )
                func_info.returns.append(ret)
            
            # Exceptions
            elif isinstance(child, ast.Raise):
                exc_type = ""
                if child.exc:
                    exc_type = self._safe_unparse(child.exc)
                exc = ExceptionInfo(
                    exception_type=exc_type,
                    line_number=child.lineno,
                    handler_type="raise"
                )
                func_info.exceptions.append(exc)
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                exc_type = child.type.id if (child.type and hasattr(child.type, 'id')) else "Exception"
                exc = ExceptionInfo(
                    exception_type=exc_type,
                    line_number=child.lineno,
                    handler_type="except"
                )
                func_info.exceptions.append(exc)
            
            # Function calls
            elif isinstance(child, ast.Call):
                call_name = self._extract_call_name(child)
                if call_name:
                    func_info.calls.append(call_name)
            
            # Boolean operators add to complexity
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        func_info.complexity = complexity
        
        return func_info
    
    def _extract_parameters(self, args: ast.arguments) -> list[ParameterInfo]:
        """
        Extract parameter information from function arguments.
        
        Args:
            args: AST arguments node
            
        Returns:
            List of ParameterInfo objects
        """
        params = []
        
        # Calculate defaults offset
        num_defaults = len(args.defaults)
        num_args = len(args.args)
        defaults_offset = num_args - num_defaults
        
        for i, arg in enumerate(args.args):
            if arg.arg == 'self':
                continue
            
            param = ParameterInfo(name=arg.arg)
            
            # Check for type annotation
            if arg.annotation:
                param.annotation = self._safe_unparse(arg.annotation)
            
            # Check for default value
            default_index = i - defaults_offset
            if default_index >= 0 and default_index < len(args.defaults):
                param.has_default = True
                param.default_value = self._safe_unparse(args.defaults[default_index])
            
            params.append(param)
        
        # Handle *args and **kwargs
        if args.vararg:
            params.append(ParameterInfo(name=f"*{args.vararg.arg}"))
        if args.kwarg:
            params.append(ParameterInfo(name=f"**{args.kwarg.arg}"))
        
        return params
    
    def _extract_condition(
        self, node: ast.AST, cond_type: str
    ) -> ConditionInfo:
        """
        Extract condition information from an if/while node.
        
        Args:
            node: AST If or While node
            cond_type: Type of condition ("if", "while")
            
        Returns:
            ConditionInfo with extracted details
        """
        condition_text = self._safe_unparse(node.test)
        comparisons = self._extract_comparisons(node.test)
        
        return ConditionInfo(
            condition_text=condition_text,
            line_number=node.lineno,
            condition_type=cond_type,
            comparisons=comparisons
        )
    
    def _extract_comparisons(self, node: ast.AST) -> list[dict]:
        """
        Extract comparison operations from a condition.
        
        Args:
            node: AST node to analyze
            
        Returns:
            List of comparison dictionaries with operator and operands
        """
        comparisons = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Compare):
                left = self._safe_unparse(child.left)
                for op, comparator in zip(child.ops, child.comparators):
                    comp = {
                        "left": left,
                        "operator": type(op).__name__,
                        "right": self._safe_unparse(comparator)
                    }
                    comparisons.append(comp)
                    left = self._safe_unparse(comparator)
        
        return comparisons
    
    def _extract_imports(self, node: ast.AST) -> list[str]:
        """Extract import names from import nodes."""
        imports = []
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
        return imports
    
    def _extract_call_name(self, node: ast.Call) -> Optional[str]:
        """Extract the name of a function call."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None
    
    def _safe_unparse(self, node: Optional[ast.AST]) -> str:
        """
        Safely convert an AST node back to source code.
        
        Args:
            node: AST node to unparse
            
        Returns:
            String representation of the node
        """
        if node is None:
            return "None"
        try:
            return ast.unparse(node)
        except Exception:
            return ast.dump(node)
