"""
Portfolio Overview page — /
  - KPI summary cards (total suppliers, tier breakdown, alert count)
  - Top-10 riskiest suppliers bar chart
  - Full portfolio risk heatmap (supplier x dimension)
"""

import dash
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path="/", name="Portfolio Overview")

RISK_PATH   = "data/processed/risk_scores.csv"
ALERTS_PATH = "data/processed/supplier_alerts.csv"

TIER_COLOR = {
    "low":      "#2ecc71",
    "medium":   "#f39c12",
    "high":     "#e74c3c",
    "critical": "#8e44ad",
}

DIMENSIONS = ["otd_risk", "ltv_risk", "defect_risk", "sentiment_risk", "geo_risk", "concentration_risk"]
DIM_LABELS  = ["OTD Risk", "Lead Time Var.", "Defect Risk", "Sentiment Risk", "Geo Risk", "Concentration"]


def _load():
    risk    = pd.read_csv(RISK_PATH)
    alerts  = pd.read_csv(ALERTS_PATH)
    return risk, alerts


def _summary_cards(risk: pd.DataFrame, alerts: pd.DataFrame) -> list:
    tier_counts = risk["tier"].value_counts()
    cards = [
        ("Total Suppliers",  str(len(risk)),                    "primary"),
        ("LOW",              str(tier_counts.get("low", 0)),    "success"),
        ("MEDIUM",           str(tier_counts.get("medium", 0)), "warning"),
        ("HIGH",             str(tier_counts.get("high", 0)),   "danger"),
        ("CRITICAL",         str(tier_counts.get("critical",0)),"dark"),
        ("Active Alerts",    str(len(alerts)),                   "secondary"),
    ]
    return [
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H6(label, className="card-subtitle text-muted mb-1"),
                    html.H3(value, className="card-title mb-0 fw-bold"),
                ])
            ], color=color, outline=True, className="h-100 text-center"),
            width=2,
        )
        for label, value, color in cards
    ]


def _bar_chart(risk: pd.DataFrame) -> go.Figure:
    top10 = risk.nlargest(10, "composite_score").sort_values("composite_score")
    colors = [TIER_COLOR[t] for t in top10["tier"]]
    fig = go.Figure(go.Bar(
        x=top10["composite_score"],
        y=top10["supplier_name"],
        orientation="h",
        marker_color=colors,
        text=top10["composite_score"].apply(lambda v: f"{v:.1f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>",
    ))
    fig.update_layout(
        title="Top 10 Riskiest Suppliers",
        xaxis_title="Composite Risk Score",
        yaxis_title=None,
        xaxis=dict(range=[0, 105]),
        margin=dict(l=0, r=40, t=40, b=20),
        height=380,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.add_vline(x=61, line_dash="dash", line_color="#e74c3c",
                  annotation_text="Alert threshold (61)", annotation_position="top right")
    return fig


def _heatmap(risk: pd.DataFrame) -> go.Figure:
    sorted_risk = risk.sort_values("composite_score", ascending=False)
    z = sorted_risk[DIMENSIONS].values.tolist()
    fig = go.Figure(go.Heatmap(
        z=z,
        x=DIM_LABELS,
        y=sorted_risk["supplier_name"].tolist(),
        colorscale="RdYlGn_r",
        zmin=0, zmax=100,
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}<extra></extra>",
        colorbar=dict(title="Risk Score"),
    ))
    fig.update_layout(
        title="Portfolio Risk Heatmap — All Suppliers",
        margin=dict(l=0, r=0, t=40, b=20),
        height=680,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


layout = html.Div([
    dbc.Row(id="summary-cards", className="g-3 mb-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="bar-chart"), width=5),
        dbc.Col(dcc.Graph(id="heatmap"),   width=7),
    ], className="mb-4"),
    dcc.Interval(id="overview-interval", interval=60_000, n_intervals=0),
])


@callback(
    Output("summary-cards", "children"),
    Output("bar-chart",     "figure"),
    Output("heatmap",       "figure"),
    Input("overview-interval", "n_intervals"),
)
def update(_n):
    risk, alerts = _load()
    return (
        _summary_cards(risk, alerts),
        _bar_chart(risk),
        _heatmap(risk),
    )
