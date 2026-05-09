"""
Prompt Builder Module
=====================
Constructs optimized prompts for LLM-based test generation.

Academic Concepts:
- Prompt Engineering
- Natural Language Processing (NLP)
- Few-shot Learning
"""

import logging
from typing import Optional
from analyzer.extractor import FunctionInfo, CodeAnalysis

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an expert Python test engineer. 
Generate comprehensive pytest test cases for the given Python code.
Rules:
1. Generate ONLY valid pytest test functions (start with test_)
2. Use assert statements for validation
3. Include docstrings explaining each test
4. Cover all branches and edge cases
5. Test both valid and invalid inputs
6. Output ONLY Python code, no explanations
7. Do NOT include import statements for the tested module
"""


class PromptBuilder:
    """Builds optimized prompts for AI test generation."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def build_generation_prompt(self, function_info: FunctionInfo, analysis=None, include_examples=True) -> str:
        sections = []
        sections.append(f"## Function to Test:\n```python\n{function_info.source_code}\n```")
        
        # Analysis
        lines = [f"## Code Analysis:", f"- Function: `{function_info.name}`"]
        lines.append(f"- Parameters: {', '.join(p.name for p in function_info.parameters) or 'none'}")
        if function_info.conditions:
            for c in function_info.conditions:
                lines.append(f"- Condition: `{c.condition_text}`")
        if function_info.returns:
            for r in function_info.returns:
                lines.append(f"- Return: `{r.return_text}`")
        lines.append(f"- Complexity: {function_info.complexity}")
        sections.append("\n".join(lines))
        
        reqs = ["## Requirements:", "- Positive and negative tests", "- Edge cases (None, 0, empty)", "- Branch coverage", "- Boundary values"]
        sections.append("\n".join(reqs))
        
        sections.append("## Output: ONLY valid Python test code, no imports, no markdown fences.")
        return "\n\n".join(sections)
    
    def build_full_code_prompt(self, source_code: str, analysis: CodeAnalysis) -> str:
        names = [f.name for f in analysis.functions]
        return f"""Generate pytest test cases for this Python code.

```python
{source_code}
```

Functions: {', '.join(names)}
Branches: {analysis.total_branches}, Avg complexity: {analysis.avg_complexity:.1f}

Requirements:
1. Test each function
2. Cover all branches
3. Edge cases (None, empty, zero, negative, large values)
4. Use pytest assert
5. Do NOT include imports
6. Each test needs docstring

Output ONLY Python test code:"""
    
    def build_explanation_prompt(self, test_code: str, source_code: str) -> str:
        return f"""Explain these tests for the source code.

Source:
```python
{source_code}
```

Tests:
```python
{test_code}
```

For each test provide: what it verifies, edge case covered, importance (High/Medium/Low).
Format: Test Name | Explanation | Coverage | Importance"""
