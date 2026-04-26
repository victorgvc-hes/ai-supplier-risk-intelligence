"""
Plotly Dash entry point — multi-page supplier risk intelligence dashboard.
Run: python dashboard/app.py
Open: http://localhost:8050
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
)

TIER_COLORS = {
    "low":      "#2ecc71",
    "medium":   "#f39c12",
    "high":     "#e74c3c",
    "critical": "#8e44ad",
}

NAV = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand(
            [html.I(className="me-2"), "Supplier Risk Intelligence"],
            href="/",
            className="fw-bold fs-5",
        ),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Portfolio Overview", href="/")),
            dbc.NavItem(dbc.NavLink("Supplier Drilldown", href="/supplier")),
            dbc.NavItem(dbc.NavLink("Alert Feed", href="/alerts")),
        ], navbar=True, className="ms-auto"),
    ]),
    color="dark",
    dark=True,
    className="mb-4",
)

app.layout = dbc.Container([
    NAV,
    dash.page_container,
], fluid=True)


if __name__ == "__main__":
    app.run(debug=True, port=8050)
