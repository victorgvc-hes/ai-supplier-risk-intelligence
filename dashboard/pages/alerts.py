"""
Alert Feed page — /alerts
  - Severity filter buttons
  - Alerts table with type, severity, supplier, and message
  - OTD rate vs defect rate scatter plot coloured by tier
"""

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, dash_table

dash.register_page(__name__, path="/alerts", name="Alert Feed")

ALERTS_PATH = "data/processed/supplier_alerts.csv"
RISK_PATH   = "data/processed/risk_scores.csv"
KPI_PATH    = "data/processed/supplier_kpis.csv"

TIER_COLOR = {
    "low":      "#2ecc71",
    "medium":   "#f39c12",
    "high":     "#e74c3c",
    "critical": "#8e44ad",
}

SEV_COLOR = {
    "critical": "#8e44ad",
    "high":     "#e74c3c",
    "medium":   "#f39c12",
    "low":      "#2ecc71",
}


def _load():
    alerts = pd.read_csv(ALERTS_PATH)
    risk   = pd.read_csv(RISK_PATH)
    kpis   = pd.read_csv(KPI_PATH)
    return alerts, risk, kpis


def _scatter(risk: pd.DataFrame, kpis: pd.DataFrame) -> go.Figure:
    merged = risk.merge(
        kpis[["supplier_name", "otd_rate", "defect_rate"]],
        on="supplier_name",
    )
    merged["otd_pct"]     = (merged["otd_rate"] * 100).round(1)
    merged["defect_pct"]  = (merged["defect_rate"] * 100).round(2)
    merged["tier_label"]  = merged["tier"].str.upper()

    fig = px.scatter(
        merged,
        x="otd_pct",
        y="defect_pct",
        color="tier",
        color_discrete_map=TIER_COLOR,
        text="supplier_name",
        size="composite_score",
        size_max=28,
        hover_data={"composite_score": ":.1f", "otd_pct": ":.1f", "defect_pct": ":.2f"},
        labels={
            "otd_pct":         "On-Time Delivery Rate (%)",
            "defect_pct":      "Defect Rate (%)",
            "composite_score": "Risk Score",
            "tier":            "Tier",
        },
        title="On-Time Delivery vs Defect Rate",
    )
    fig.update_traces(textposition="top center", textfont_size=9)
    fig.add_vline(x=80, line_dash="dot", line_color="#aaa",
                  annotation_text="OTD 80%", annotation_position="bottom right")
    fig.add_hline(y=3, line_dash="dot", line_color="#aaa",
                  annotation_text="Defect 3%", annotation_position="top left")
    fig.update_layout(
        height=450,
        margin=dict(l=0, r=0, t=40, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


layout = html.Div([
    dbc.Row([
        dbc.Col(html.H5("Filter by Severity", className="fw-semibold mb-0 mt-1"), width="auto"),
        dbc.Col(
            dbc.ButtonGroup([
                dbc.Button("All",      id="sev-all",      color="secondary", outline=True, size="sm", n_clicks=0),
                dbc.Button("Critical", id="sev-critical", color="dark",      outline=True, size="sm", n_clicks=0),
                dbc.Button("High",     id="sev-high",     color="danger",    outline=True, size="sm", n_clicks=0),
                dbc.Button("Medium",   id="sev-medium",   color="warning",   outline=True, size="sm", n_clicks=0),
            ]),
            width="auto",
        ),
        dbc.Col(html.Div(id="alert-count-badge"), width="auto", className="d-flex align-items-center"),
    ], align="center", className="mb-3 g-2"),

    html.Div(id="alerts-table", className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="otd-defect-scatter"), width=12),
    ]),
])


@callback(
    Output("alerts-table",       "children"),
    Output("alert-count-badge",  "children"),
    Output("otd-defect-scatter", "figure"),
    Input("sev-all",      "n_clicks"),
    Input("sev-critical", "n_clicks"),
    Input("sev-high",     "n_clicks"),
    Input("sev-medium",   "n_clicks"),
)
def update(n_all, n_crit, n_high, n_med):
    alerts, risk, kpis = _load()

    from dash import ctx
    triggered = ctx.triggered_id or "sev-all"

    sev_filter = {
        "sev-all":      None,
        "sev-critical": "critical",
        "sev-high":     "high",
        "sev-medium":   "medium",
    }.get(triggered)

    filtered = alerts if sev_filter is None else alerts[alerts["severity"] == sev_filter]

    display_cols = ["supplier_name", "alert_type", "severity", "message"]
    display = filtered[display_cols].rename(columns={
        "supplier_name": "Supplier",
        "alert_type":    "Alert Type",
        "severity":      "Severity",
        "message":       "Message",
    })

    table = dash_table.DataTable(
        data=display.to_dict("records"),
        columns=[{"name": c, "id": c} for c in display.columns],
        page_size=15,
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "8px 12px",
            "fontFamily": "sans-serif",
            "fontSize": "13px",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_header={
            "fontWeight": "bold",
            "backgroundColor": "#f8f9fa",
            "borderBottom": "2px solid #dee2e6",
        },
        style_data_conditional=[
            {"if": {"filter_query": '{Severity} = "critical"'}, "color": "#8e44ad", "fontWeight": "600"},
            {"if": {"filter_query": '{Severity} = "high"'},     "color": "#e74c3c", "fontWeight": "600"},
            {"if": {"filter_query": '{Severity} = "medium"'},   "color": "#f39c12"},
        ],
    )

    badge = dbc.Badge(f"{len(filtered)} alerts", color="secondary", pill=True, className="fs-6")
    return table, badge, _scatter(risk, kpis)
