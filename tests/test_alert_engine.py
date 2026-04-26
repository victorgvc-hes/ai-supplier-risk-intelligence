import pandas as pd
import pytest
from intelligence.alert_engine import generate_alerts


@pytest.fixture
def risk_df():
    return pd.DataFrame({
        "supplier_name":    ["SupA", "SupB", "SupC"],
        "country":          ["Germany", "Bangladesh", "China"],
        "otd_risk":         [6.0,  76.0, 50.0],
        "ltv_risk":         [5.0,  80.0, 30.0],
        "defect_risk":      [3.75, 97.5, 20.0],
        "sentiment_risk":   [10.0, 65.0, 30.0],
        "geo_risk":         [5.0,  62.0, 55.0],
        "concentration_risk": [0.0, 0.0, 75.0],
        "composite_score":  [14.0, 68.0, 45.0],
        "tier":             ["low", "high", "medium"],
    })


@pytest.fixture
def kpi_df():
    return pd.DataFrame({
        "supplier_name":      ["SupA", "SupB", "SupC"],
        "otd_rate":           [0.97,  0.62,  0.75],
        "defect_rate":        [0.003, 0.078, 0.020],
        "concentration_pct":  [5.0,   2.0,   16.0],
        "avg_lead_time_days": [14.0,  42.0,  28.0],
        "lead_time_std":      [1.5,   15.0,  8.0],
    })


def test_no_alerts_for_low_risk(risk_df, kpi_df):
    alerts = generate_alerts(risk_df, kpi_df)
    supa_alerts = alerts[alerts["supplier_name"] == "SupA"]
    # SupA score=14, OTD=97%, defect=0.3% — no thresholds breached
    assert len(supa_alerts) == 0


def test_high_risk_supplier_triggers_alerts(risk_df, kpi_df):
    alerts = generate_alerts(risk_df, kpi_df)
    supb_alerts = alerts[alerts["supplier_name"] == "SupB"]
    assert len(supb_alerts) > 0


def test_composite_breach_alert_fired(risk_df, kpi_df):
    alerts = generate_alerts(risk_df, kpi_df)
    breach = alerts[
        (alerts["supplier_name"] == "SupB") &
        (alerts["alert_type"] == "composite_score_breach")
    ]
    assert len(breach) == 1


def test_concentration_alert_fired(risk_df, kpi_df):
    alerts = generate_alerts(risk_df, kpi_df)
    conc = alerts[
        (alerts["supplier_name"] == "SupC") &
        (alerts["alert_type"] == "high_concentration")
    ]
    assert len(conc) == 1


def test_output_columns(risk_df, kpi_df):
    alerts = generate_alerts(risk_df, kpi_df)
    expected = {"supplier_name", "alert_type", "severity", "message", "triggered_at"}
    assert expected.issubset(set(alerts.columns))


def test_severity_values_valid(risk_df, kpi_df):
    alerts = generate_alerts(risk_df, kpi_df)
    assert set(alerts["severity"].unique()).issubset({"low", "medium", "high", "critical"})
