"""
Coverage Runner Module
======================
Measures test coverage using coverage.py.

Academic Concepts:
- Code Coverage Analysis
- Line Coverage
- Branch Coverage
- Coverage Optimization
"""

import os
import sys
import subprocess
import tempfile
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class CoverageRunner:
    """
    Measures code coverage for generated tests.
    
    Metrics:
    - Line coverage percentage
    - Branch coverage percentage
    - Uncovered lines identification
    - Coverage report generation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def measure_coverage(self, test_code: str, source_code: str) -> dict:
        """
        Measure code coverage for test code against source code.
        
        Returns:
            dict with coverage metrics
        """
        results = {
            "line_coverage": 0.0,
            "branch_coverage": 0.0,
            "total_statements": 0,
            "covered_statements": 0,
            "missing_lines": [],
            "report": "",
            "success": False,
            "error": ""
        }
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write files
                source_file = os.path.join(tmpdir, "source_module.py")
                with open(source_file, 'w') as f:
                    f.write(source_code)
                
                # Build test file
                import ast
                try:
                    tree = ast.parse(source_code)
                    func_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                    class_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                    all_names = func_names + class_names
                    import_line = f"from source_module import {', '.join(all_names)}" if all_names else "import source_module"
                except SyntaxError:
                    import_line = "import source_module"
                
                test_file = os.path.join(tmpdir, "test_generated.py")
                with open(test_file, 'w') as f:
                    f.write(f"import pytest\n{import_line}\n\n{test_code}")
                
                # Run coverage
                env = {**os.environ, "PYTHONPATH": tmpdir}
                
                # coverage run
                result = subprocess.run(
                    [sys.executable, "-m", "coverage", "run",
                     "--source", tmpdir,
                     "--branch",
                     "-m", "pytest", test_file, "-v", "--tb=short"],
                    capture_output=True, text=True, cwd=tmpdir,
                    timeout=60, env=env
                )
                
                # coverage report
                report_result = subprocess.run(
                    [sys.executable, "-m", "coverage", "report", "--show-missing"],
                    capture_output=True, text=True, cwd=tmpdir,
                    timeout=30, env=env
                )
                
                results["report"] = report_result.stdout
                results["success"] = True
                
                # Parse coverage report
                self._parse_report(report_result.stdout, results)
                
                # Get JSON report for detailed analysis
                json_result = subprocess.run(
                    [sys.executable, "-m", "coverage", "json", "-o", os.path.join(tmpdir, "cov.json")],
                    capture_output=True, text=True, cwd=tmpdir,
                    timeout=30, env=env
                )
                
                json_file = os.path.join(tmpdir, "cov.json")
                if os.path.exists(json_file):
                    import json
                    with open(json_file) as f:
                        cov_data = json.load(f)
                    self._parse_json_report(cov_data, results)
                
        except subprocess.TimeoutExpired:
            results["error"] = "Coverage measurement timed out"
        except Exception as e:
            results["error"] = f"Coverage error: {str(e)}"
            self.logger.error(f"Coverage measurement failed: {e}")
        
        return results
    
    def _parse_report(self, report: str, results: dict):
        """Parse text coverage report."""
        lines = report.splitlines()
        for line in lines:
            # Look for TOTAL line
            if line.strip().startswith("TOTAL") or line.strip().startswith("source_module"):
                parts = line.split()
                for part in parts:
                    if '%' in part:
                        try:
                            results["line_coverage"] = float(part.replace('%', ''))
                        except ValueError:
                            pass
                
                # Extract numbers
                nums = re.findall(r'\d+', line)
                if len(nums) >= 2:
                    results["total_statements"] = int(nums[0])
                    miss = int(nums[1])
                    results["covered_statements"] = results["total_statements"] - miss
                
                # Extract missing lines
                if "Missing" in report or "missing" in line.lower():
                    missing_part = line.split()[-1] if parts else ""
                    if re.match(r'[\d,\-]+', missing_part):
                        results["missing_lines"] = missing_part.split(',')
    
    def _parse_json_report(self, data: dict, results: dict):
        """Parse JSON coverage report for detailed metrics."""
        try:
            totals = data.get("totals", {})
            results["line_coverage"] = totals.get("percent_covered", results["line_coverage"])
            results["total_statements"] = totals.get("num_statements", results["total_statements"])
            results["covered_statements"] = totals.get("covered_lines", results["covered_statements"])
            
            branch_covered = totals.get("covered_branches", 0)
            branch_total = totals.get("num_branches", 0)
            if branch_total > 0:
                results["branch_coverage"] = round((branch_covered / branch_total) * 100, 1)
        except Exception:
            pass
