import pandas as pd
import pytest
from features.risk_scorer import (
    _otd_risk, _ltv_risk, _defect_risk, _geo_risk,
    _concentration_risk, _assign_tier, compute_risk_scores,
)


# ---------------------------------------------------------------------------
# Unit tests for individual normalisation helpers
# ---------------------------------------------------------------------------

def test_otd_risk_perfect():
    assert _otd_risk(1.0) == pytest.approx(0.0)


def test_otd_risk_zero():
    assert _otd_risk(0.0) == pytest.approx(100.0)


def test_otd_risk_half():
    assert _otd_risk(0.5) == pytest.approx(100.0)   # clamped at 100


def test_ltv_risk_zero_std():
    assert _ltv_risk(0.0, 20.0) == pytest.approx(0.0)


def test_ltv_risk_high_cv():
    # CV = 0.6 / 0.6 * 100 = 100
    assert _ltv_risk(12.0, 20.0) == pytest.approx(100.0)


def test_defect_risk_zero():
    assert _defect_risk(0.0) == pytest.approx(0.0)


def test_defect_risk_max():
    assert _defect_risk(0.08) == pytest.approx(100.0)


def test_defect_risk_clamped():
    assert _defect_risk(0.20) == pytest.approx(100.0)


def test_geo_risk_clamp():
    assert _geo_risk(150.0) == pytest.approx(100.0)
    assert _geo_risk(-5.0)  == pytest.approx(0.0)


def test_concentration_risk_below_threshold():
    assert _concentration_risk(2.0) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Tier assignment
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("score,expected", [
    (0.0,   "low"),
    (15.0,  "low"),
    (30.0,  "low"),
    (30.5,  "low"),
    (31.0,  "medium"),
    (60.0,  "medium"),
    (60.9,  "medium"),
    (61.0,  "high"),
    (80.0,  "high"),
    (81.0,  "critical"),
    (100.0, "critical"),
])
def test_assign_tier(score, expected):
    assert _assign_tier(score) == expected


# ---------------------------------------------------------------------------
# Integration test for compute_risk_scores
# ---------------------------------------------------------------------------

@pytest.fixture
def kpis():
    return pd.DataFrame({
        "supplier_name":      ["SupA", "SupB"],
        "country":            ["Germany", "Bangladesh"],
        "otd_rate":           [0.97, 0.60],
        "avg_lead_time_days": [14.0, 42.0],
        "lead_time_std":      [1.5, 15.0],
        "defect_rate":        [0.003, 0.078],
        "concentration_pct":  [5.0, 2.0],
    })


@pytest.fixture
def sentiment():
    return pd.DataFrame({
        "supplier_name":      ["SupA", "SupB"],
        "sentiment_risk_score": [10.0, 75.0],
    })


@pytest.fixture
def country_risk():
    return {"Germany": 5.0, "Bangladesh": 62.0}


def test_compute_returns_correct_shape(kpis, sentiment, country_risk):
    result = compute_risk_scores(kpis, sentiment, country_risk)
    assert len(result) == 2


def test_low_risk_supplier_scores_low(kpis, sentiment, country_risk):
    result = compute_risk_scores(kpis, sentiment, country_risk).set_index("supplier_name")
    assert result.loc["SupA", "composite_score"] < 31
    assert result.loc["SupA", "tier"] == "low"


def test_high_risk_supplier_scores_higher(kpis, sentiment, country_risk):
    result = compute_risk_scores(kpis, sentiment, country_risk).set_index("supplier_name")
    assert result.loc["SupB", "composite_score"] > result.loc["SupA", "composite_score"]


def test_output_columns(kpis, sentiment, country_risk):
    result = compute_risk_scores(kpis, sentiment, country_risk)
    expected = {
        "supplier_name", "country", "otd_risk", "ltv_risk", "defect_risk",
        "sentiment_risk", "geo_risk", "concentration_risk", "composite_score", "tier",
    }
    assert set(result.columns) == expected
