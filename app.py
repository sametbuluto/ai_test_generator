"""
AI-Based Automated Test Case Generation System
==============================================

Main entry point for the application.
Launches the Streamlit dashboard.

Usage:
    streamlit run app.py

Academic Project: Artificial Intelligence
"""

import os
import sys
import subprocess


def main():
    """Launch the AI Test Generator dashboard."""
    # Get the dashboard path
    dashboard_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "frontend",
        "dashboard.py"
    )
    
    # Ensure generated_tests and uploads directories exist
    os.makedirs("generated_tests", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    # Launch Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        dashboard_path,
        "--server.headless", "true",
        "--theme.base", "dark",
        "--theme.primaryColor", "#667eea",
        "--theme.backgroundColor", "#0f172a",
        "--theme.secondaryBackgroundColor", "#1e293b",
        "--theme.textColor", "#e2e8f0",
    ])


if __name__ == "__main__":
    main()
