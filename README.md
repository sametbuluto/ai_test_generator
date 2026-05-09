# AI-Based Automated Test Case Generation System

## 🧪 Project Overview

An AI-powered automated test case generation system that analyzes Python source code and generates intelligent, comprehensive pytest test cases. The system uses a combination of **LLM-based AI generation** and **rule-based heuristics** to create high-quality test suites.

### Key Features

- 🔍 **Static Code Analysis** — AST-based parsing and feature extraction
- 🤖 **AI Test Generation** — LLM-powered intelligent test creation
- 📐 **Rule-Based Edge Cases** — Boundary Value Analysis, Equivalence Partitioning
- ✅ **Test Validation** — Syntax checking, duplicate detection, safety analysis
- ▶️ **Automatic Execution** — Pytest integration with result parsing
- 📊 **Coverage Analysis** — Line and branch coverage measurement
- ⚡ **Test Optimization** — Duplicate removal and priority ranking
- 🖥️ **Professional Dashboard** — Streamlit-based interactive UI

## 🏗️ Architecture

```text
Input Source Code
        ↓
   Code Parser (AST)
        ↓
  Feature Extractor
        ↓
  ┌─────────────────┐
  │  AI Generator   │ ←── OpenAI API / Template Fallback
  │  Rule Generator │ ←── BVA, Equivalence Partitioning
  └─────────────────┘
        ↓
   Test Validator
        ↓
   Pytest Executor
        ↓
  Coverage Analyzer
        ↓
  Test Optimizer
        ↓
     Dashboard
```

## 📁 Project Structure

```text
project/
├── app.py                    # Main entry point
├── requirements.txt          # Dependencies
├── README.md                 # Documentation
│
├── analyzer/                 # Static Code Analysis
│   ├── parser.py             # AST Parser
│   ├── extractor.py          # Feature Extractor
│   └── ast_utils.py          # AST Utilities
│
├── generator/                # Test Generation
│   ├── ai_generator.py       # AI/LLM Generator
│   ├── rule_generator.py     # Rule-Based Generator
│   └── prompt_builder.py     # Prompt Engineering
│
├── validator/                # Test Validation
│   ├── syntax_validator.py   # Syntax Checker
│   └── test_validator.py     # Quality Validator
│
├── executor/                 # Test Execution
│   ├── pytest_runner.py      # Pytest Integration
│   └── coverage_runner.py    # Coverage Measurement
│
├── optimizer/                # Test Optimization
│   ├── duplicate_remover.py  # Deduplication
│   └── prioritizer.py        # Priority Ranking
│
├── frontend/                 # User Interface
│   ├── dashboard.py          # Streamlit Dashboard
│   └── components.py         # UI Components
│
├── sample_codes/             # Sample Python Files
├── generated_tests/          # Output Directory
└── uploads/                  # User Uploads
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

Or:

```bash
python app.py
```

### 3. (Optional) Configure OpenAI API

Set your API key in the sidebar settings for AI-powered generation.
Without an API key, the system uses intelligent template-based generation.

## 📋 Usage

1. **Upload or Paste** Python source code
2. Click **🚀 Run Full Pipeline** to:
   - Analyze code structure
   - Generate test cases (AI + Rule-based)
   - Validate generated tests
   - Execute tests automatically
   - Measure code coverage
   - Optimize test suite
3. View results in the dashboard

## 🔬 Academic Concepts

| Concept | Implementation |
|---------|---------------|
| Abstract Syntax Tree (AST) | `analyzer/parser.py` |
| Feature Extraction | `analyzer/extractor.py` |
| Cyclomatic Complexity | `analyzer/ast_utils.py` |
| Prompt Engineering | `generator/prompt_builder.py` |
| LLM Code Generation | `generator/ai_generator.py` |
| Boundary Value Analysis | `generator/rule_generator.py` |
| Equivalence Partitioning | `generator/rule_generator.py` |
| Test Case Prioritization | `optimizer/prioritizer.py` |
| Code Coverage Analysis | `executor/coverage_runner.py` |
| Test Suite Minimization | `optimizer/duplicate_remover.py` |

## 🛠️ Technology Stack

- **Python 3.11+**
- **Streamlit** — Web Dashboard
- **pytest** — Test Execution
- **coverage.py** — Coverage Analysis
- **OpenAI API** — LLM Integration (optional)
- **Plotly** — Data Visualization
- **AST Module** — Static Analysis

## 📄 License

University AI Project — Academic Use
