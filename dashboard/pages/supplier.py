"""
Supplier Drilldown page — /supplier
  - Supplier selector dropdown
  - Six-dimension risk score cards
  - Radar chart comparing supplier vs portfolio average
  - AI-generated (or mock) risk brief
"""

import dash
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path="/supplier", name="Supplier Drilldown")

RISK_PATH   = "data/processed/risk_scores.csv"
BRIEFS_PATH = "data/processed/supplier_briefs.csv"

TIER_COLOR = {
    "low":      "#2ecc71",
    "medium":   "#f39c12",
    "high":     "#e74c3c",
    "critical": "#8e44ad",
}

DIMENSIONS = ["otd_risk", "ltv_risk", "defect_risk", "sentiment_risk", "geo_risk", "concentration_risk"]
DIM_LABELS  = ["OTD Risk", "Lead Time Var.", "Defect Risk", "Sentiment Risk", "Geo Risk", "Concentration"]


def _load():
    risk   = pd.read_csv(RISK_PATH)
    briefs = pd.read_csv(BRIEFS_PATH)
    return risk, briefs


def _dimension_cards(row: pd.Series) -> list:
    items = zip(DIM_LABELS, DIMENSIONS)
    cols  = []
    for label, col in items:
        val   = row[col]
        color = "success" if val < 31 else ("warning" if val < 61 else "danger")
        cols.append(
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.P(label, className="text-muted small mb-1"),
                        html.H4(f"{val:.1f}", className="mb-0 fw-bold"),
                    ])
                ], color=color, outline=True, className="text-center h-100"),
                width=2,
            )
        )
    return cols


def _radar(supplier_row: pd.Series, avg_row: pd.Series) -> go.Figure:
    labels = DIM_LABELS + [DIM_LABELS[0]]  # close the polygon

    supplier_vals = [supplier_row[d] for d in DIMENSIONS] + [supplier_row[DIMENSIONS[0]]]
    avg_vals      = [avg_row[d]      for d in DIMENSIONS] + [avg_row[DIMENSIONS[0]]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=supplier_vals, theta=labels, fill="toself",
        name=supplier_row["supplier_name"],
        line_color="#e74c3c", fillcolor="rgba(231,76,60,0.15)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=avg_vals, theta=labels, fill="toself",
        name="Portfolio Average",
        line_color="#3498db", fillcolor="rgba(52,152,219,0.10)",
        line_dash="dash",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Risk Dimensions vs Portfolio Average",
        height=420,
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=40, r=40, t=50, b=60),
    )
    return fig


layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Label("Select Supplier", className="fw-semibold"),
            dcc.Dropdown(id="supplier-selector", clearable=False),
        ], width=4),
        dbc.Col(html.Div(id="supplier-tier-badge"), width=8, className="d-flex align-items-end"),
    ], className="mb-4"),

    dbc.Row(id="dimension-cards", className="g-3 mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="radar-chart"), width=6),
        dbc.Col([
            html.H5("Risk Brief", className="fw-semibold mb-2"),
            html.Div(id="brief-text", className="p-3 bg-light rounded border"),
        ], width=6, className="d-flex flex-column justify-content-start"),
    ], className="mb-4"),
])


@callback(
    Output("supplier-selector", "options"),
    Output("supplier-selector", "value"),
    Input("supplier-selector",  "id"),
)
def populate_dropdown(_):
    risk, _ = _load()
    sorted_risk = risk.sort_values("composite_score", ascending=False)
    options = [{"label": r["supplier_name"], "value": r["supplier_name"]}
               for _, r in sorted_risk.iterrows()]
    return options, options[0]["value"]


@callback(
    Output("supplier-tier-badge", "children"),
    Output("dimension-cards",     "children"),
    Output("radar-chart",         "figure"),
    Output("brief-text",          "children"),
    Input("supplier-selector",    "value"),
)
def update_supplier(supplier_name: str):
    risk, briefs = _load()

    row     = risk[risk["supplier_name"] == supplier_name].iloc[0]
    avg_row = risk[DIMENSIONS].mean()
    avg_row["supplier_name"] = "Portfolio Average"

    tier   = row["tier"]
    color  = TIER_COLOR.get(tier, "#999")
    badge  = dbc.Badge(
        f"{tier.upper()}  {row['composite_score']:.1f} / 100",
        color=color, pill=True, className="fs-6 px-3 py-2",
        style={"backgroundColor": color},
    )

    brief_row  = briefs[briefs["supplier_name"] == supplier_name]
    brief_text = brief_row["brief_text"].values[0] if len(brief_row) else "No brief available."

    return (
        badge,
        _dimension_cards(row),
        _radar(row, avg_row),
        html.P(brief_text, className="mb-0"),
    )
