"""
Compute weighted composite risk scores and assign tiers per supplier.
Combines KPI dimensions, sentiment, and geopolitical risk.
"""

import pandas as pd
from config import RISK_WEIGHTS, RISK_TIERS


# ---------------------------------------------------------------------------
# Individual dimension normalisation helpers (all return 0-100, higher = riskier)
# ---------------------------------------------------------------------------

def _otd_risk(otd_rate: float) -> float:
    """Low OTD -> high risk. 100% OTD = 0 risk, 50% OTD = 100 risk."""
    return max(0.0, min(100.0, (1.0 - otd_rate) * 200))


def _ltv_risk(lead_time_std: float, avg_lead_time: float) -> float:
    """
    Coefficient of variation (std / mean) normalised to 0-100.
    CV of 0 = 0 risk; CV >= 0.6 = 100 risk.
    """
    if avg_lead_time <= 0:
        return 0.0
    cv = lead_time_std / avg_lead_time
    return max(0.0, min(100.0, cv / 0.6 * 100))


def _defect_risk(defect_rate: float) -> float:
    """0% defects = 0 risk; >= 8% defects = 100 risk."""
    return max(0.0, min(100.0, defect_rate / 0.08 * 100))


def _geo_risk(geo_risk_score: float) -> float:
    """Country risk score already on 0-100 scale."""
    return max(0.0, min(100.0, float(geo_risk_score)))


def _concentration_risk(concentration_pct: float) -> float:
    """
    Single-supplier concentration:
    <4% = low risk; >=20% = maximum risk.
    """
    return max(0.0, min(100.0, (concentration_pct - 4.0) / 16.0 * 100))


def _assign_tier(score: float) -> str:
    # Sort descending by lower bound so the first match wins correctly
    # for float scores that fall in the gaps between integer config boundaries.
    ordered = sorted(RISK_TIERS.items(), key=lambda kv: kv[1][0], reverse=True)
    for tier, (lo, _) in ordered:
        if score >= lo:
            return tier
    return "low"


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def compute_risk_scores(
    kpis: pd.DataFrame,
    sentiment: pd.DataFrame,
    country_risk_map: dict[str, float],
) -> pd.DataFrame:
    """
    Parameters
    ----------
    kpis             : output of features.kpi_engine.compute_kpis
    sentiment        : output of features.sentiment_engine.score_headlines
    country_risk_map : {country: geo_risk_score} from ingestion.country_risk_loader

    Returns
    -------
    DataFrame with one row per supplier containing all risk dimensions,
    composite_score, and tier — matching the RiskScore Pydantic schema.
    """
    df = kpis.merge(
        sentiment[["supplier_name", "sentiment_risk_score"]],
        on="supplier_name",
        how="left",
    )
    df["sentiment_risk_score"] = df["sentiment_risk_score"].fillna(50.0)

    df["geo_risk_raw"] = df["country"].map(country_risk_map).fillna(50.0)

    df["otd_risk"]          = df["otd_rate"].apply(_otd_risk)
    df["ltv_risk"]          = df.apply(
        lambda r: _ltv_risk(r["lead_time_std"], r["avg_lead_time_days"]), axis=1
    )
    df["defect_risk"]       = df["defect_rate"].apply(_defect_risk)
    df["sentiment_risk"]    = df["sentiment_risk_score"]
    df["geo_risk"]          = df["geo_risk_raw"].apply(_geo_risk)
    df["concentration_risk"]= df["concentration_pct"].apply(_concentration_risk)

    w = RISK_WEIGHTS
    df["composite_score"] = (
        df["otd_risk"]           * w["otd"]
        + df["ltv_risk"]         * w["ltv"]
        + df["defect_risk"]      * w["defect"]
        + df["sentiment_risk"]   * w["sentiment"]
        + df["geo_risk"]         * w["geo"]
        + df["concentration_risk"] * w["concentration"]
    ).round(2)

    df["tier"] = df["composite_score"].apply(_assign_tier)

    return df[[
        "supplier_name",
        "country",
        "otd_risk",
        "ltv_risk",
        "defect_risk",
        "sentiment_risk",
        "geo_risk",
        "concentration_risk",
        "composite_score",
        "tier",
    ]]
