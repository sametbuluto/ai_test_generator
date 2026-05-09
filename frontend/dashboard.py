"""
Dashboard Module
================
Main Streamlit dashboard for the AI Test Generator.

This is the primary user interface providing:
- Source code input (upload or paste)
- Code analysis visualization
- AI test generation controls
- Test execution results
- Coverage analysis display
- Optimization results
"""

import os
import sys
import time
import logging
import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.parser import CodeParser
from analyzer.extractor import FeatureExtractor
from analyzer.ast_utils import detect_patterns, count_lines_of_code
from generator.ai_generator import AITestGenerator
from generator.rule_generator import RuleBasedGenerator
from validator.syntax_validator import SyntaxValidator
from validator.test_validator import TestValidator
from executor.pytest_runner import PytestRunner
from executor.coverage_runner import CoverageRunner
from optimizer.duplicate_remover import DuplicateRemover
from optimizer.prioritizer import TestPrioritizer
from frontend.components import (
    render_header, render_metric_card, render_status_badge,
    render_coverage_gauge, render_test_results_chart,
    render_priority_chart, render_complexity_chart,
    render_pipeline_status
)

logger = logging.getLogger(__name__)


# ─── Page Config ──────────────────────────────────────────────
def setup_page(theme="Dark"):
    st.set_page_config(
        page_title="AI Test Generator",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if theme == "Light":
        bg_color = "#f8fafc"
        bg_secondary = "#ffffff"
        text_color = "#334155"
        text_muted = "#64748b"
        border_color = "#e2e8f0"
    else:
        bg_color = "#0f172a"
        bg_secondary = "#1e293b"
        text_color = "#e2e8f0"
        text_muted = "#94a3b8"
        border_color = "#334155"

    # Custom CSS
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        .stApp {{
            font-family: 'Inter', sans-serif;
            background-color: {bg_color};
            color: {text_color};
        }}
        
        /* Dark/Light theme overrides */
        .stTextArea textarea {{
            background-color: {bg_secondary} !important;
            color: {text_color} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
            font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
            font-size: 0.85rem !important;
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(102,126,234,0.4) !important;
        }}
        
        .stSelectbox > div > div {{
            background-color: {bg_secondary} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
            color: {text_color} !important;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: {bg_secondary};
            border-radius: 8px;
            color: {text_muted};
            padding: 8px 16px;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
        }}
        
        .stExpander {{
            background-color: {bg_secondary} !important;
            border: 1px solid {border_color} !important;
            border-radius: 10px !important;
        }}
        
        h1, h2, h3, h4 {{ color: {text_color} !important; }}
        p, li {{ color: {text_color}; }}
        
        .stCodeBlock {{ border-radius: 10px !important; }}
        
        div[data-testid="stSidebar"] {{
            background-color: {bg_color};
            border-right: 1px solid {border_color};
        }}
        
        .stFileUploader {{
            background-color: {bg_secondary};
            border: 2px dashed {border_color};
            border-radius: 12px;
            padding: 1rem;
        }}
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: {bg_color}; }}
        ::-webkit-scrollbar-thumb {{ background: {border_color}; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: {text_muted}; }}
        
        .block-container {{ padding: 1rem 2rem !important; }}
    </style>
    """, unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0;">
            <h2 style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 1.3rem;
            ">⚙️ Settings</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Theme Setting
        st.markdown("### 🎨 Appearance")
        selected_theme = st.radio("Theme Mode", ["Dark", "Light"], horizontal=True, key="theme")
        
        st.markdown("---")
        
        # AI Model settings
        st.markdown("### 🤖 AI Configuration")
        
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Optional. Leave empty for template-based generation."
        )
        
        model = st.selectbox(
            "Model",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            help="Select the OpenAI model to use"
        )
        
        st.markdown("---")
        
        # Generation settings
        st.markdown("### 🎯 Generation Settings")
        
        use_ai = st.checkbox("Use AI Generation", value=True, help="Enable LLM-based test generation")
        use_rules = st.checkbox("Use Rule-Based Generation", value=True, help="Enable rule-based edge case generation")
        auto_execute = st.checkbox("Auto-Execute Tests", value=True, help="Automatically run generated tests")
        auto_coverage = st.checkbox("Auto-Measure Coverage", value=True, help="Automatically measure code coverage")
        auto_optimize = st.checkbox("Auto-Optimize Tests", value=True, help="Remove duplicates and prioritize")
        
        st.markdown("---")
        
        # Sample code loader
        st.markdown("### 📁 Sample Codes")
        sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_codes")
        
        sample_files = []
        if os.path.exists(sample_dir):
            sample_files = [f for f in os.listdir(sample_dir) if f.endswith('.py')]
        
        selected_sample = st.selectbox(
            "Load Sample",
            ["-- Select --"] + sample_files,
            help="Load a sample Python file for testing"
        )
        
        sample_code = None
        if selected_sample and selected_sample != "-- Select --":
            filepath = os.path.join(sample_dir, selected_sample)
            with open(filepath, 'r') as f:
                sample_code = f.read()
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color: #64748b; font-size: 0.75rem; padding: 1rem 0;">
            <p>AI Test Generator v1.0</p>
            <p>University AI Project</p>
        </div>
        """, unsafe_allow_html=True)
        
        return {
            "api_key": api_key,
            "model": model,
            "use_ai": use_ai,
            "use_rules": use_rules,
            "auto_execute": auto_execute,
            "auto_coverage": auto_coverage,
            "auto_optimize": auto_optimize,
            "sample_code": sample_code
        }


# ─── Main Dashboard ──────────────────────────────────────────
def run_dashboard():
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"
        
    setup_page(st.session_state.theme)
    render_header()
    settings = render_sidebar()
    
    # Initialize session state
    if "source_code" not in st.session_state:
        st.session_state.source_code = ""
    if "generated_tests" not in st.session_state:
        st.session_state.generated_tests = ""
    if "analysis" not in st.session_state:
        st.session_state.analysis = None
    if "execution_results" not in st.session_state:
        st.session_state.execution_results = None
    if "coverage_results" not in st.session_state:
        st.session_state.coverage_results = None
    if "optimization_results" not in st.session_state:
        st.session_state.optimization_results = None
    if "pipeline_status" not in st.session_state:
        st.session_state.pipeline_status = {
            "analyze": "pending", "generate": "pending",
            "validate": "pending", "execute": "pending",
            "coverage": "pending", "optimize": "pending"
        }
    
    # ─── Source Code Input Section ────────────────────────────
    st.markdown("### 📝 Source Code Input")
    
    input_method = st.radio(
        "Input Method",
        ["📋 Paste Code", "📁 Upload File"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if input_method == "📁 Upload File":
        uploaded_file = st.file_uploader(
            "Upload Python File",
            type=["py"],
            help="Upload a .py file to analyze"
        )
        if uploaded_file:
            st.session_state.source_code = uploaded_file.read().decode("utf-8")
    else:
        # Load sample code if selected
        default_code = settings.get("sample_code") or st.session_state.source_code or ""
        source_code = st.text_area(
            "Paste your Python code here:",
            value=default_code,
            height=300,
            placeholder="def my_function(x, y):\n    if x > 0:\n        return x + y\n    return 0"
        )
        st.session_state.source_code = source_code
    
    if not st.session_state.source_code.strip():
        st.info("👆 Paste Python code or upload a file to get started.")
        return
    
    # ─── Pipeline Status ──────────────────────────────────────
    st.markdown("### 🔄 Pipeline Status")
    render_pipeline_status(st.session_state.pipeline_status, st.session_state.theme)
    st.markdown("")
    
    # ─── Action Buttons ───────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analyze_btn = st.button("🔍 Analyze Code", use_container_width=True)
    with col2:
        generate_btn = st.button("🤖 Generate Tests", use_container_width=True)
    with col3:
        full_pipeline_btn = st.button("🚀 Run Full Pipeline", use_container_width=True)
    
    # ─── Full Pipeline ────────────────────────────────────────
    if full_pipeline_btn or generate_btn:
        run_full_pipeline(settings)
    elif analyze_btn:
        run_analysis_only()
    
    # ─── Results Display ──────────────────────────────────────
    display_results(settings)


def run_analysis_only():
    """Run only the analysis step."""
    source_code = st.session_state.source_code
    
    st.session_state.pipeline_status["analyze"] = "running"
    
    with st.spinner("🔍 Analyzing code..."):
        parser = CodeParser()
        extractor = FeatureExtractor()
        
        parse_result = parser.parse(source_code)
        
        if not parse_result.is_valid:
            st.error(f"❌ Parse Error: {parse_result.error_message}")
            st.session_state.pipeline_status["analyze"] = "error"
            return
        
        analysis = extractor.extract(parse_result.tree, source_code)
        st.session_state.analysis = analysis
        st.session_state.parse_result = parse_result
        st.session_state.pipeline_status["analyze"] = "done"
        st.success("✅ Code analysis complete!")


def run_full_pipeline(settings):
    """Run the complete test generation pipeline."""
    source_code = st.session_state.source_code
    
    # Reset states
    for key in st.session_state.pipeline_status:
        st.session_state.pipeline_status[key] = "pending"
    
    progress = st.progress(0, text="Starting pipeline...")
    
    # ─── Step 1: Analyze ──────────────────────────────────────
    st.session_state.pipeline_status["analyze"] = "running"
    progress.progress(10, text="🔍 Analyzing code structure...")
    
    parser = CodeParser()
    extractor = FeatureExtractor()
    
    parse_result = parser.parse(source_code)
    if not parse_result.is_valid:
        st.error(f"❌ Parse Error: {parse_result.error_message}")
        st.session_state.pipeline_status["analyze"] = "error"
        return
    
    analysis = extractor.extract(parse_result.tree, source_code)
    st.session_state.analysis = analysis
    st.session_state.parse_result = parse_result
    st.session_state.pipeline_status["analyze"] = "done"
    
    # ─── Step 2: Generate Tests ───────────────────────────────
    st.session_state.pipeline_status["generate"] = "running"
    progress.progress(30, text="🤖 Generating test cases...")
    
    all_tests = []
    
    # AI generation
    if settings["use_ai"]:
        ai_gen = AITestGenerator(
            api_key=settings.get("api_key"),
            model=settings.get("model", "gpt-3.5-turbo")
        )
        ai_tests = ai_gen.generate_tests_for_code(source_code, analysis)
        if ai_tests:
            all_tests.append(ai_tests)
        
        # Generate explanations
        if ai_tests:
            explanations = ai_gen.explain_tests(ai_tests, source_code)
            st.session_state.explanations = explanations
    
    # Rule-based generation
    if settings["use_rules"]:
        rule_gen = RuleBasedGenerator()
        rule_tests = rule_gen.generate_all_edge_cases(analysis, parse_result.tree)
        if rule_tests:
            all_tests.append(rule_tests)
    
    combined_tests = "\n\n\n".join(all_tests)
    st.session_state.generated_tests = combined_tests
    st.session_state.pipeline_status["generate"] = "done"
    
    if not combined_tests.strip():
        st.warning("⚠️ No tests were generated. Check your code.")
        return
    
    # ─── Step 3: Validate ─────────────────────────────────────
    st.session_state.pipeline_status["validate"] = "running"
    progress.progress(50, text="✅ Validating tests...")
    
    syntax_val = SyntaxValidator()
    test_val = TestValidator()
    
    syntax_result = syntax_val.validate(combined_tests)
    validation_result = test_val.validate_all(combined_tests)
    
    st.session_state.validation_result = validation_result
    
    if validation_result["is_valid"]:
        combined_tests = validation_result["cleaned_code"]
        st.session_state.generated_tests = combined_tests
    
    st.session_state.pipeline_status["validate"] = "done" if validation_result["is_valid"] else "error"
    
    # ─── Step 4: Execute ──────────────────────────────────────
    if settings["auto_execute"] and validation_result["is_valid"]:
        st.session_state.pipeline_status["execute"] = "running"
        progress.progress(65, text="▶️ Executing tests...")
        
        runner = PytestRunner()
        exec_results = runner.run_tests(combined_tests, source_code)
        st.session_state.execution_results = exec_results
        st.session_state.pipeline_status["execute"] = "done"
    
    # ─── Step 5: Coverage ─────────────────────────────────────
    if settings["auto_coverage"] and validation_result["is_valid"]:
        st.session_state.pipeline_status["coverage"] = "running"
        progress.progress(80, text="📊 Measuring coverage...")
        
        cov_runner = CoverageRunner()
        cov_results = cov_runner.measure_coverage(combined_tests, source_code)
        st.session_state.coverage_results = cov_results
        st.session_state.pipeline_status["coverage"] = "done"
    
    # ─── Step 6: Optimize ─────────────────────────────────────
    if settings["auto_optimize"] and validation_result["is_valid"]:
        st.session_state.pipeline_status["optimize"] = "running"
        progress.progress(90, text="⚡ Optimizing tests...")
        
        remover = DuplicateRemover()
        dup_results = remover.remove_duplicates(combined_tests)
        
        prioritizer = TestPrioritizer()
        pri_results = prioritizer.prioritize(
            dup_results["cleaned_code"] if dup_results["removed_count"] > 0 else combined_tests
        )
        
        st.session_state.optimization_results = {
            "duplicates": dup_results,
            "priorities": pri_results
        }
        st.session_state.pipeline_status["optimize"] = "done"
    
    progress.progress(100, text="✅ Pipeline complete!")
    time.sleep(0.5)
    progress.empty()


def display_results(settings):
    """Display all pipeline results."""
    theme = st.session_state.get("theme", "Dark")
    
    # ─── Analysis Results ─────────────────────────────────────
    if st.session_state.analysis:
        analysis = st.session_state.analysis
        
        st.markdown("---")
        st.markdown("### 📊 Code Analysis")
        
        # Metrics row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_metric_card("Functions", str(analysis.total_functions), icon="⚡", color="#667eea", theme=theme)
        with m2:
            render_metric_card("Branches", str(analysis.total_branches), icon="🔀", color="#764ba2", theme=theme)
        with m3:
            render_metric_card("Complexity", f"{analysis.avg_complexity:.1f}", "average", icon="📈", color="#f59e0b", theme=theme)
        with m4:
            loc = count_lines_of_code(st.session_state.source_code)
            render_metric_card("Lines", str(loc["code"]), f"({loc['comments']} comments)", icon="📄", color="#10b981", theme=theme)
        
        # Function details
        with st.expander("🔍 Function Details", expanded=False):
            for func in analysis.functions:
                st.markdown(f"""
                **`{func.name}`** — Complexity: {func.complexity} | Branches: {func.branch_count} | Params: {len(func.parameters)}
                """)
                if func.conditions:
                    for c in func.conditions:
                        st.markdown(f"  - Condition: `{c.condition_text}`")
                if func.returns:
                    for r in func.returns:
                        st.markdown(f"  - Returns: `{r.return_text}`")
        
        # Complexity chart
        if analysis.functions:
            fig = render_complexity_chart(analysis.functions, theme)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    # ─── Generated Tests ──────────────────────────────────────
    if st.session_state.generated_tests:
        st.markdown("---")
        st.markdown("### 🧪 Generated Test Cases")
        
        tab1, tab2, tab3 = st.tabs(["📝 Test Code", "💡 Explanations", "📋 Validation"])
        
        with tab1:
            st.code(st.session_state.generated_tests, language="python")
            
            # Download button
            st.download_button(
                "📥 Download Tests",
                st.session_state.generated_tests,
                file_name="test_generated.py",
                mime="text/x-python"
            )
        
        with tab2:
            if hasattr(st.session_state, 'explanations') and st.session_state.explanations:
                st.markdown(st.session_state.explanations)
            else:
                st.info("Explanations are generated with AI mode enabled.")
        
        with tab3:
            if hasattr(st.session_state, 'validation_result'):
                vr = st.session_state.validation_result
                col1, col2, col3 = st.columns(3)
                with col1:
                    render_metric_card("Tests Found", str(vr.get("test_count", 0)), icon="🧪", color="#667eea", theme=theme)
                with col2:
                    render_metric_card("Quality Score", f"{vr.get('quality_score', 0):.0f}%", icon="⭐", color="#f59e0b", theme=theme)
                with col3:
                    render_metric_card("Duplicates", str(vr.get("duplicate_count", 0)), icon="🔄", color="#ef4444", theme=theme)
                
                if vr.get("errors"):
                    for err in vr["errors"]:
                        st.error(err)
                if vr.get("warnings"):
                    for warn in vr["warnings"]:
                        st.warning(warn)
    
    # ─── Execution Results ────────────────────────────────────
    if st.session_state.execution_results:
        st.markdown("---")
        st.markdown("### ▶️ Execution Results")
        
        er = st.session_state.execution_results
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("Total Tests", str(er["total"]), icon="🧪", color="#667eea", theme=theme)
        with col2:
            render_metric_card("Passed", str(er["passed"]), icon="✅", color="#10b981", theme=theme)
        with col3:
            render_metric_card("Failed", str(er["failed"]), icon="❌", color="#ef4444", theme=theme)
        with col4:
            render_metric_card("Time", f"{er['execution_time']:.2f}s", icon="⏱️", color="#8b5cf6", theme=theme)
        
        # Results chart
        fig = render_test_results_chart(er["passed"], er["failed"], er["errors"], theme)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Execution log
        with st.expander("📋 Execution Log", expanded=False):
            st.code(er["output"], language="text")
        
        # Test details
        if er.get("test_details"):
            with st.expander("📝 Test Details", expanded=False):
                for detail in er["test_details"]:
                    status_icon = "✅" if detail["status"] == "PASSED" else "❌"
                    st.markdown(f"{status_icon} `{detail['name']}` — **{detail['status']}**")
    
    # ─── Coverage Results ─────────────────────────────────────
    if st.session_state.coverage_results:
        st.markdown("---")
        st.markdown("### 📊 Coverage Analysis")
        
        cr = st.session_state.coverage_results
        
        col1, col2 = st.columns(2)
        with col1:
            fig = render_coverage_gauge(cr.get("line_coverage", 0), "Line Coverage", theme)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = render_coverage_gauge(cr.get("branch_coverage", 0), "Branch Coverage", theme)
            st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("Statements", str(cr.get("total_statements", 0)), icon="📄", color="#667eea", theme=theme)
        with col2:
            render_metric_card("Covered", str(cr.get("covered_statements", 0)), icon="✅", color="#10b981", theme=theme)
        with col3:
            missing = cr.get("total_statements", 0) - cr.get("covered_statements", 0)
            render_metric_card("Missing", str(missing), icon="⚠️", color="#f59e0b", theme=theme)
        
        if cr.get("report"):
            with st.expander("📋 Coverage Report", expanded=False):
                st.code(cr["report"], language="text")
    
    # ─── Optimization Results ─────────────────────────────────
    if st.session_state.optimization_results:
        st.markdown("---")
        st.markdown("### ⚡ Optimization Results")
        
        opt = st.session_state.optimization_results
        
        # Duplicate removal
        dup = opt.get("duplicates", {})
        pri = opt.get("priorities", {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("Original", str(dup.get("original_count", 0)), icon="📝", color="#667eea", theme=theme)
        with col2:
            render_metric_card("Removed", str(dup.get("removed_count", 0)), "duplicates", icon="🗑️", color="#ef4444", theme=theme)
        with col3:
            render_metric_card("Final", str(dup.get("final_count", 0)), icon="✅", color="#10b981", theme=theme)
        with col4:
            render_metric_card("High Priority", str(pri.get("high_priority", 0)), icon="🔴", color="#f59e0b", theme=theme)
        
        # Priority chart
        if pri.get("total", 0) > 0:
            fig = render_priority_chart(
                pri.get("high_priority", 0),
                pri.get("medium_priority", 0),
                pri.get("low_priority", 0),
                theme
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Prioritized test list
        if pri.get("prioritized_tests"):
            with st.expander("📋 Prioritized Test List", expanded=False):
                for t in pri["prioritized_tests"]:
                    icon = "🔴" if t["priority"] == "High" else "🟡" if t["priority"] == "Medium" else "🟢"
                    st.markdown(f"{icon} **{t['name']}** — Score: {t['score']:.0f} | {t['priority']}")
                    if t.get("docstring"):
                        st.markdown(f"  _{t['docstring']}_")
        
        # Removed duplicates
        if dup.get("removed_tests"):
            with st.expander("🗑️ Removed Duplicates", expanded=False):
                for removed in dup["removed_tests"]:
                    st.markdown(f"- {removed}")
        
        # Download optimized tests
        if pri.get("prioritized_code"):
            st.download_button(
                "📥 Download Optimized Tests",
                pri["prioritized_code"],
                file_name="test_optimized.py",
                mime="text/x-python"
            )


if __name__ == "__main__":
    run_dashboard()
