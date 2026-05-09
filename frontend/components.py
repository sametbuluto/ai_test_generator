"""
UI Components Module
====================
Reusable Streamlit UI components for the dashboard.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

def get_theme_colors(theme):
    if theme == "Light":
        return {
            "bg": "#f8fafc",
            "bg_card": "#ffffff",
            "text": "#334155",
            "text_muted": "#64748b",
            "border": "#e2e8f0",
            "grid": "#e2e8f0"
        }
    return {
        "bg": "#0f172a",
        "bg_card": "#1e293b",
        "text": "#e2e8f0",
        "text_muted": "#94a3b8",
        "border": "#334155",
        "grid": "#1e293b"
    }


def render_header():
    """Render the application header."""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        ">🧪 AI Test Generator</h1>
        <p style="color: #94a3b8; font-size: 1.1rem; font-weight: 300;">
            Intelligent Automated Test Case Generation System
        </p>
        <div style="
            width: 100px; height: 3px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 1rem auto; border-radius: 2px;
        "></div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(title: str, value: str, subtitle: str = "", icon: str = "📊", color: str = "#667eea", theme: str = "Dark"):
    """Render a styled metric card."""
    t = get_theme_colors(theme)
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}15, {color}08);
        background-color: {t['bg_card']};
        border: 1px solid {t['border']};
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
    ">
        <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">{icon}</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: {color};">{value}</div>
        <div style="font-size: 0.85rem; font-weight: 600; color: {t['text']}; margin-top: 0.2rem;">{title}</div>
        <div style="font-size: 0.75rem; color: {t['text_muted']}; margin-top: 0.1rem;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str, text: str = ""):
    """Render a status badge."""
    colors = {
        "success": ("#10b981", "✅"),
        "error": ("#ef4444", "❌"),
        "warning": ("#f59e0b", "⚠️"),
        "info": ("#3b82f6", "ℹ️"),
        "running": ("#8b5cf6", "⏳"),
    }
    color, icon = colors.get(status, ("#6b7280", "•"))
    display_text = text or status.upper()
    st.markdown(f"""
    <span style="
        background: {color}20;
        color: {color};
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    ">{icon} {display_text}</span>
    """, unsafe_allow_html=True)


def render_coverage_gauge(coverage: float, label: str = "Line Coverage", theme: str = "Dark"):
    """Render a coverage gauge chart."""
    t = get_theme_colors(theme)
    color = "#10b981" if coverage >= 80 else "#f59e0b" if coverage >= 50 else "#ef4444"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=coverage,
        number={"suffix": "%", "font": {"size": 36, "color": t["text"]}},
        title={"text": label, "font": {"size": 14, "color": t["text_muted"]}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": t["text_muted"]}},
            "bar": {"color": color},
            "bgcolor": t["bg_card"],
            "bordercolor": t["border"],
            "steps": [
                {"range": [0, 50], "color": t["bg_card"]},
                {"range": [50, 80], "color": t["bg_card"]},
                {"range": [80, 100], "color": t["bg_card"]},
            ],
            "threshold": {
                "line": {"color": t["text"], "width": 2},
                "thickness": 0.75,
                "value": coverage
            }
        }
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": t["text"]}
    )
    return fig


def render_test_results_chart(passed: int, failed: int, errors: int, theme: str = "Dark"):
    """Render test results as a donut chart."""
    t = get_theme_colors(theme)
    labels = ["Passed", "Failed", "Errors"]
    values = [passed, failed, errors]
    colors = ["#10b981", "#ef4444", "#f59e0b"]
    
    # Filter out zero values
    filtered = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
    if not filtered:
        return None
    
    labels, values, colors = zip(*filtered)
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker_colors=colors,
        textinfo="label+value",
        textfont={"size": 13, "color": t["text"]},
        hoverinfo="label+percent+value"
    )])
    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": t["text"]},
        showlegend=True,
        legend=dict(font=dict(color=t["text_muted"]))
    )
    return fig


def render_priority_chart(high: int, medium: int, low: int, theme: str = "Dark"):
    """Render priority distribution chart."""
    t = get_theme_colors(theme)
    fig = go.Figure(data=[go.Bar(
        x=["🔴 High", "🟡 Medium", "🟢 Low"],
        y=[high, medium, low],
        marker_color=["#ef4444", "#f59e0b", "#10b981"],
        text=[high, medium, low],
        textposition="outside",
        textfont={"color": t["text"], "size": 14}
    )])
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color=t["text_muted"])),
        yaxis=dict(tickfont=dict(color=t["text_muted"]), gridcolor=t["grid"]),
        font={"color": t["text"]}
    )
    return fig


def render_complexity_chart(functions: list, theme: str = "Dark"):
    """Render function complexity chart."""
    if not functions:
        return None
    
    t = get_theme_colors(theme)
    names = [f.name for f in functions]
    complexities = [f.complexity for f in functions]
    branches = [f.branch_count for f in functions]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Complexity",
        x=names, y=complexities,
        marker_color="#667eea",
        text=complexities,
        textposition="outside",
        textfont={"color": t["text"]}
    ))
    fig.add_trace(go.Bar(
        name="Branches",
        x=names, y=branches,
        marker_color="#764ba2",
        text=branches,
        textposition="outside",
        textfont={"color": t["text"]}
    ))
    fig.update_layout(
        barmode='group',
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color=t["text_muted"])),
        yaxis=dict(tickfont=dict(color=t["text_muted"]), gridcolor=t["grid"]),
        font={"color": t["text"]},
        legend=dict(font=dict(color=t["text_muted"]))
    )
    return fig


def render_pipeline_status(steps: dict, theme: str = "Dark"):
    """Render pipeline progress indicator."""
    t = get_theme_colors(theme)
    icons = {
        "analyze": "🔍", "generate": "🤖", "validate": "✅",
        "execute": "▶️", "coverage": "📊", "optimize": "⚡"
    }
    status_colors = {
        "done": "#10b981", "running": "#667eea",
        "pending": t["text_muted"], "error": "#ef4444"
    }
    
    cols = st.columns(len(steps))
    for i, (step, status) in enumerate(steps.items()):
        with cols[i]:
            color = status_colors.get(status, t["text_muted"])
            icon = icons.get(step, "•")
            st.markdown(f"""
            <div style="text-align:center;">
                <div style="
                    width: 40px; height: 40px;
                    border-radius: 50%;
                    background: {color}30;
                    border: 2px solid {color};
                    display: flex; align-items: center; justify-content: center;
                    margin: 0 auto 0.4rem auto;
                    font-size: 1.2rem;
                ">{icon}</div>
                <div style="font-size: 0.7rem; color: {color}; font-weight: 600;">
                    {step.upper()}
                </div>
            </div>
            """, unsafe_allow_html=True)
