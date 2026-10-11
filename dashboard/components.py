import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


def render_kpi_card(title, value, prefix="", suffix="", change=None, subtitle=""):
    """Render a styled navy and teal KPI card."""
    change_html = ""

    if change is not None:
        change_color = "#34d399" if change >= 0 else "#fb7185"
        change_symbol = "▲" if change >= 0 else "▼"

        change_html = (
            f'<p style="color:{change_color}; font-size:12px; '
            f'margin:10px 0 0 0;">'
            f'{change_symbol} {abs(change):.1f}% vs last period'
            '</p>'
        )

    subtitle_html = (
        f'<p style="color:#8fa5bd; font-size:12px; '
        f'margin:6px 0 0 0;">{subtitle}</p>'
        if subtitle else ""
    )

    st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #1b2b42 0%, #111c30 100%);
            border: 1px solid #2b4058;
            border-left: 4px solid #14b8a6;
            padding: 14px 16px;
            margin-bottom: 10px;
            min-height: 110px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.15);
        ">
            <p style="
                color: #9fb2c8;
                font-size: 13px;
                font-weight: 500;
                margin: 0 0 12px 0;
            ">{title}</p>

            <div style="
                color: #f8fafc;
                font-size: 27px;
                font-weight: 700;
                line-height: 1.25;
                overflow-wrap: anywhere;
            ">{prefix}{value}{suffix}</div>

            {change_html}
            {subtitle_html}
        </div>
    """, unsafe_allow_html=True)


def render_kpi_row(kpis):
    """Render a row of KPI cards."""
    cols = st.columns(len(kpis))
    for i, kpi in enumerate(kpis):
        with cols[i]:
            render_kpi_card(**kpi)

def create_line_chart(df, x, y, title=None, color=None):
    """Create a styled line chart."""
    if df.empty: return empty_chart(title)
    fig = px.line(df, x=x, y=y, title=title, color=color, template="plotly_dark")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=40, b=10, l=10, r=10))
    return fig

def create_bar_chart(df, x, y, title=None, color=None, orientation='v', barmode='group'):
    """Create a styled bar chart."""
    if df.empty: return empty_chart(title)
    fig = px.bar(df, x=x, y=y, title=title, color=color, orientation=orientation, barmode=barmode, template="plotly_dark")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=40, b=10, l=10, r=10))
    return fig

def create_pie_chart(df, names, values, title=None, hole=0.5):
    """Create a styled pie/donut chart."""
    if df.empty: return empty_chart(title)
    fig = px.pie(df, names=names, values=values, title=title, hole=hole, template="plotly_dark")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=40, b=10, l=10, r=10))
    return fig

def create_gauge_chart(value, title, min_val, max_val, suffix=""):
    """Create a styled gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        number={'suffix': suffix},
        gauge={'axis': {'range': [min_val, max_val]},
               'bar': {'color': "#4caf50" if value > (max_val-min_val)*0.6 else "#ff9800" if value > (max_val-min_val)*0.3 else "#f44336"}}
    ))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=40, b=10, l=10, r=10), height=300)
    return fig

def empty_chart(title="No Data"):
    """Return an empty chart placeholder."""
    fig = go.Figure()
    fig.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={'visible': False},
        yaxis={'visible': False},
        annotations=[dict(text="No data available for this selection", xref="paper", yref="paper", showarrow=False, font=dict(size=14, color="#a0a0a0"))]
    )
    return fig

def render_alert_card(alert):
    """Render an alert."""
    colors = {'critical': '#f44336', 'high': '#ff9800', 'medium': '#ffeb3b', 'low': '#4caf50'}
    color = colors.get(alert.get('severity', 'low').lower(), '#a0a0a0')
    st.markdown(f"""
        <div style="border-left: 5px solid {color}; background-color: #1e1e1e; padding: 15px; margin-bottom: 10px; border-radius: 4px;">
            <h4 style="margin: 0; color: {color};">{alert.get('title', 'Alert')}</h4>
            <p style="margin: 5px 0 0 0; font-size: 14px;">{alert.get('message', '')}</p>
            <small style="color: #a0a0a0;">{alert.get('timestamp', '')}</small>
        </div>
    """, unsafe_allow_html=True)

def apply_filters():
    """Render sidebar filters and return selections."""
    st.sidebar.header("Operational Filters")
    facility_options = {
        "All Facilities": None,
        "FAC001 - Central Hospital (500 Beds)": "FAC001",
        "FAC002 - City Care Hospital (300 Beds)": "FAC002",
        "FAC003 - North Branch (150 Beds)": "FAC003",
        "FAC004 - South Branch (150 Beds)": "FAC004"
    }
    facility_label = st.sidebar.selectbox("Facility", list(facility_options.keys()))
    facility_id = facility_options[facility_label]
    
    dept_options = {
        "All Departments": None,
        "DEP001 - Emergency": "DEP001",
        "DEP002 - Cardiology": "DEP002",
        "DEP003 - Neurology": "DEP003",
        "DEP004 - Orthopedics": "DEP004",
        "DEP005 - Pediatrics": "DEP005",
        "DEP006 - General Medicine": "DEP006",
        "DEP007 - Surgery": "DEP007",
        "DEP008 - ICU": "DEP008",
        "DEP009 - Dermatology": "DEP009",
        "DEP010 - Gynecology": "DEP010"
    }
    dept_label = st.sidebar.selectbox("Department", list(dept_options.keys()))
    department_id = dept_options[dept_label]
    
    date_period = st.sidebar.selectbox("Date Period", ["Last 30 Days", "Last 60 Days", "Last 90 Days", "Last 180 Days"])
    
    return {
        "facility": facility_id,
        "facility_label": facility_label,
        "department": department_id,
        "department_label": dept_label,
        "date_period": date_period
    }
