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
            "bg": "#EEF2F6",
            "bg_card": "#EEF2F6",
            "bg_sidebar": "#EEF2F6",
            "text": "#1E293B",
            "text_secondary": "#475569",
            "text_muted": "#64748B",
            "border": "#CBD5E1",
            "input_border": "#94A3B8",
            "grid": "#E2E8F0",
            "primary": "#4F46E5",
            "secondary": "#7C3AED",
            "accent": "#4F46E5",
            "gradient": "linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)",
            "hover": "#E2E8F0",
            "focus": "rgba(79, 70, 229, 0.12)",
            "shadow": "none",
            "card_shadow": "none"
        }
    return {
        "bg": "#0f172a",
        "bg_card": "#1e293b",
        "bg_sidebar": "#0f172a",
        "text": "#e2e8f0",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "border": "#334155",
        "input_border": "#334155",
        "grid": "#1e293b",
        "primary": "#667eea",
        "secondary": "#764ba2",
        "accent": "#667eea",
        "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "hover": "#2d3748",
        "focus": "rgba(102, 126, 234, 0.2)",
        "shadow": "none",
        "card_shadow": "none"
    }


def render_header(theme="Dark"):
    """Render a compact, modern premium SaaS hero section."""
    t = get_theme_colors(theme)
    gradient = t["gradient"]
    shadow = t["shadow"] if theme == "Light" else "none"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0 3rem 0;">
        <div style="
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 48px; height: 48px;
            background: {gradient};
            border-radius: 14px;
            margin-bottom: 1.25rem;
            box-shadow: {shadow};
        ">
            <span style="font-size: 1.75rem;">🧪</span>
        </div>
        <h1 style="
            background: {gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            color: {t['primary']};
            font-size: 2.75rem;
            font-weight: 800;
            margin: 0;
            line-height: 1.2;
            letter-spacing: -0.03em;
        ">AI Test Generator</h1>
        <p style="
            color: {t['text_secondary']};
            font-size: 1.1rem;
            font-weight: 500;
            margin-top: 0.75rem;
            max-width: 550px;
            margin-left: auto;
            margin-right: auto;
            letter-spacing: -0.01em;
            line-height: 1.5;
        ">
            Professional AI-powered static analysis and automated test generation for high-quality Python codebases.
        </p>
        <div style="
            width: 40px; height: 3px;
            background: {t['primary']}40;
            margin: 1.5rem auto;
            border-radius: 2px;
        "></div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(title: str, value: str, subtitle: str = "", icon: str = "📊", color: str = None, theme: str = "Dark"):
    """Render a high-contrast premium metric card."""
    t = get_theme_colors(theme)
    if color is None:
        color = t["primary"]
        
    shadow = t["card_shadow"] if theme == "Light" else "none"
    
    st.markdown(f"""
    <div style="
        background-color: {t['bg_card']};
        border: 1px solid {t['border']};
        border-radius: 20px;
        padding: 1.5rem;
        text-align: left;
        box-shadow: {shadow};
        transition: all 0.3s ease;
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
        ">
            <div style="
                width: 36px; height: 36px;
                display: flex; align-items: center; justify-content: center;
                background: {color}15;
                border: 1px solid {color}30;
                border-radius: 10px;
                font-size: 1.1rem;
            ">{icon}</div>
            <div style="font-size: 0.8rem; font-weight: 700; color: {t['text_secondary']}; letter-spacing: 0.05em; text-transform: uppercase;">{title}</div>
        </div>
        <div style="font-size: 2rem; font-weight: 800; color: {t['text']}; line-height: 1; letter-spacing: -0.02em;">{value}</div>
        <div style="font-size: 0.85rem; color: {t['text_muted']}; margin-top: 0.6rem; font-weight: 600;">{subtitle}</div>
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
