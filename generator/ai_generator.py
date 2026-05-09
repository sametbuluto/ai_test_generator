"""
AI Test Generator Module
========================
Uses LLM (OpenAI API or local fallback) for intelligent test generation.

Academic Concepts:
- Large Language Models (LLM)
- Natural Language Processing
- Code Generation
- AI-Assisted Software Engineering
"""

import os
import re
import logging
from typing import Optional
from analyzer.extractor import FunctionInfo, CodeAnalysis
from generator.prompt_builder import PromptBuilder, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class AITestGenerator:
    """
    AI-powered test case generator using LLM.
    
    Supports:
    - OpenAI API (GPT-4, GPT-3.5)
    - Local fallback with template-based generation
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.prompt_builder = PromptBuilder()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._client = None
        
        if self.api_key:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
                self.logger.info(f"OpenAI client initialized with model: {model}")
            except ImportError:
                self.logger.warning("OpenAI package not installed, using fallback")
            except Exception as e:
                self.logger.warning(f"OpenAI init failed: {e}, using fallback")
    
    def generate_tests(self, function_info: FunctionInfo, analysis: Optional[CodeAnalysis] = None) -> str:
        """Generate test cases for a single function."""
        self.logger.info(f"Generating tests for: {function_info.name}")
        
        if self._client:
            return self._generate_with_api(function_info, analysis)
        else:
            return self._generate_with_fallback(function_info)
    
    def generate_tests_for_code(self, source_code: str, analysis: CodeAnalysis) -> str:
        """Generate test cases for entire source code."""
        self.logger.info("Generating tests for full source code")
        
        if self._client:
            return self._generate_full_with_api(source_code, analysis)
        else:
            return self._generate_full_with_fallback(analysis)
    
    def explain_tests(self, test_code: str, source_code: str) -> str:
        """Generate explanations for test cases."""
        if self._client:
            prompt = self.prompt_builder.build_explanation_prompt(test_code, source_code)
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a test engineering expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            except Exception as e:
                self.logger.error(f"API explanation failed: {e}")
        
        return self._generate_fallback_explanations(test_code)
    
    def _generate_with_api(self, func: FunctionInfo, analysis: Optional[CodeAnalysis]) -> str:
        """Generate tests using OpenAI API."""
        prompt = self.prompt_builder.build_generation_prompt(func, analysis)
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=3000
            )
            code = response.choices[0].message.content
            return self._clean_generated_code(code)
        except Exception as e:
            self.logger.error(f"API generation failed: {e}")
            return self._generate_with_fallback(func)
    
    def _generate_full_with_api(self, source_code: str, analysis: CodeAnalysis) -> str:
        """Generate tests for full code using API."""
        prompt = self.prompt_builder.build_full_code_prompt(source_code, analysis)
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=4000
            )
            code = response.choices[0].message.content
            return self._clean_generated_code(code)
        except Exception as e:
            self.logger.error(f"Full API generation failed: {e}")
            return self._generate_full_with_fallback(analysis)
    
    def _generate_with_fallback(self, func: FunctionInfo) -> str:
        """Template-based fallback test generation."""
        self.logger.info(f"Using fallback generation for: {func.name}")
        tests = []
        
        params = [p for p in func.parameters if not p.name.startswith('*')]
        param_names = [p.name for p in params]
        
        # 1. Basic positive test
        args = self._generate_sample_args(params)
        tests.append(f'''def test_{func.name}_basic():
    """Test {func.name} with valid basic inputs."""
    result = {func.name}({args})
    assert result is not None''')
        
        # 2. Boundary / condition tests
        for cond in func.conditions:
            test_name = self._sanitize_name(cond.condition_text)
            for comp in cond.comparisons:
                boundary_args = self._generate_boundary_args(params, comp)
                tests.append(f'''def test_{func.name}_{test_name}_boundary():
    """Test {func.name} at boundary: {cond.condition_text}"""
    result = {func.name}({boundary_args})
    assert result is not None''')
        
        # 3. Zero value test
        if params:
            zero_args = ", ".join(["0"] * len(params))
            tests.append(f'''def test_{func.name}_zero_values():
    """Test {func.name} with zero values."""
    try:
        result = {func.name}({zero_args})
    except (ZeroDivisionError, ValueError, TypeError):
        pass''')
        
        # 4. Negative value test
        if params:
            neg_args = ", ".join(["-1"] * len(params))
            tests.append(f'''def test_{func.name}_negative_values():
    """Test {func.name} with negative values."""
    try:
        result = {func.name}({neg_args})
    except (ValueError, TypeError):
        pass''')
        
        # 5. None input test
        if params:
            none_args = ", ".join(["None"] * len(params))
            tests.append(f'''def test_{func.name}_none_input():
    """Test {func.name} with None inputs."""
    try:
        result = {func.name}({none_args})
    except (TypeError, ValueError, AttributeError):
        pass''')
        
        # 6. String input test
        if params:
            str_args = ", ".join(['"test"'] * len(params))
            tests.append(f'''def test_{func.name}_string_input():
    """Test {func.name} with string inputs."""
    try:
        result = {func.name}({str_args})
    except (TypeError, ValueError):
        pass''')
        
        # 7. Large value test
        if params:
            large_args = ", ".join(["999999"] * len(params))
            tests.append(f'''def test_{func.name}_large_values():
    """Test {func.name} with very large values."""
    try:
        result = {func.name}({large_args})
    except (OverflowError, ValueError, MemoryError):
        pass''')
        
        # 8. Return value type tests
        for ret in func.returns:
            if ret.return_text and ret.return_text != "None":
                tests.append(f'''def test_{func.name}_return_type():
    """Test {func.name} return value is correct type."""
    result = {func.name}({args})
    assert result is not None''')
                break
        
        # 9. Exception tests
        for exc in func.exceptions:
            if exc.handler_type == "raise":
                tests.append(f'''def test_{func.name}_raises_{self._sanitize_name(exc.exception_type)}():
    """Test {func.name} raises {exc.exception_type}."""
    try:
        result = {func.name}({args})
    except Exception:
        pass''')
        
        # 10. Default parameter tests
        for p in params:
            if p.has_default:
                other_args = self._generate_sample_args([pp for pp in params if pp.name != p.name])
                tests.append(f'''def test_{func.name}_default_{p.name}():
    """Test {func.name} with default value for {p.name}."""
    result = {func.name}({other_args})
    assert result is not None''')
        
        return "\n\n\n".join(tests)
    
    def _generate_full_with_fallback(self, analysis: CodeAnalysis) -> str:
        """Generate tests for all functions using fallback."""
        all_tests = []
        for func in analysis.functions:
            tests = self._generate_with_fallback(func)
            all_tests.append(f"# Tests for {func.name}\n{tests}")
        return "\n\n\n".join(all_tests)
    
    def _generate_sample_args(self, params: list) -> str:
        """Generate sample argument values for function parameters."""
        if not params:
            return ""
        args = []
        for i, p in enumerate(params):
            if p.annotation:
                ann = p.annotation.lower()
                if 'str' in ann:
                    args.append(f'"test_{p.name}"')
                elif 'float' in ann:
                    args.append(str(float(i + 1)))
                elif 'bool' in ann:
                    args.append("True")
                elif 'list' in ann:
                    args.append("[1, 2, 3]")
                elif 'dict' in ann:
                    args.append('{"key": "value"}')
                else:
                    args.append(str(i + 1))
            elif p.has_default and p.default_value:
                args.append(str(p.default_value))
            else:
                args.append(str(i + 1))
        return ", ".join(args)
    
    def _generate_boundary_args(self, params: list, comparison: dict) -> str:
        """Generate boundary value arguments based on comparison."""
        args = []
        for p in params:
            if p.name == comparison.get("left"):
                right_val = comparison.get("right", "0")
                try:
                    val = int(right_val)
                    args.append(str(val))
                except (ValueError, TypeError):
                    args.append(right_val)
            else:
                args.append("1")
        return ", ".join(args) if args else "1"
    
    def _sanitize_name(self, text: str) -> str:
        """Convert text to valid Python identifier."""
        clean = re.sub(r'[^a-zA-Z0-9]', '_', text)
        clean = re.sub(r'_+', '_', clean).strip('_').lower()
        return clean[:40] if clean else "case"
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean LLM-generated code output."""
        # Remove markdown code fences
        code = re.sub(r'```python\s*', '', code)
        code = re.sub(r'```\s*', '', code)
        # Remove import lines for the module under test
        lines = code.splitlines()
        cleaned = [l for l in lines if not l.strip().startswith(('import ', 'from '))]
        return "\n".join(cleaned).strip()
    
    def _generate_fallback_explanations(self, test_code: str) -> str:
        """Generate basic explanations without API."""
        explanations = []
        func_pattern = re.compile(r'def (test_\w+)\(')
        doc_pattern = re.compile(r'"""(.+?)"""', re.DOTALL)
        
        matches = func_pattern.findall(test_code)
        docs = doc_pattern.findall(test_code)
        
        for i, name in enumerate(matches):
            doc = docs[i].strip() if i < len(docs) else "Tests function behavior"
            importance = "High" if any(k in name for k in ['zero', 'none', 'error', 'boundary', 'negative']) else "Medium"
            
            if 'zero' in name:
                coverage = "Tests zero/division-by-zero edge case"
            elif 'none' in name:
                coverage = "Tests null reference handling"
            elif 'negative' in name:
                coverage = "Tests negative value boundary"
            elif 'large' in name:
                coverage = "Tests overflow/large input handling"
            elif 'string' in name:
                coverage = "Tests type mismatch handling"
            elif 'boundary' in name:
                coverage = "Tests conditional branch boundary"
            elif 'basic' in name:
                coverage = "Tests normal execution path"
            elif 'return' in name:
                coverage = "Validates return value correctness"
            else:
                coverage = "Tests specific behavior scenario"
            
            explanations.append(f"**{name}**\n  - Explanation: {doc}\n  - Coverage: {coverage}\n  - Importance: {importance}")
        
        return "\n\n".join(explanations) if explanations else "No test explanations available."
