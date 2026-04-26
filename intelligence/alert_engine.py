"""
Threshold-based alert rule engine.
Evaluates risk scores and KPIs against configurable rules and
returns a DataFrame of SupplierAlert records.
"""

from datetime import datetime, timezone
import pandas as pd
from config import ALERT_THRESHOLD


# ---------------------------------------------------------------------------
# Alert rules — each rule is a (condition_fn, alert_type, severity, message_fn)
# ---------------------------------------------------------------------------

def _rules(row: pd.Series, kpi_row: pd.Series) -> list[dict]:
    alerts = []
    now    = datetime.now(timezone.utc).isoformat()

    def add(alert_type: str, severity: str, message: str) -> None:
        alerts.append({
            "supplier_name": row["supplier_name"],
            "alert_type":    alert_type,
            "severity":      severity,
            "message":       message,
            "triggered_at":  now,
        })

    # --- Composite score breach ---
    if row["composite_score"] >= ALERT_THRESHOLD:
        add(
            "composite_score_breach",
            "critical" if row["composite_score"] >= 81 else "high",
            f"Composite risk score {row['composite_score']:.1f} exceeds threshold "
            f"{ALERT_THRESHOLD} (tier: {row['tier'].upper()}).",
        )

    # --- On-time delivery ---
    otd = 1.0 - row["otd_risk"] / 200          # reverse of _otd_risk()
    if otd < 0.70:
        add(
            "low_otd",
            "critical",
            f"On-time delivery rate {otd:.1%} is critically low (below 70%).",
        )
    elif otd < 0.80:
        add(
            "low_otd",
            "high",
            f"On-time delivery rate {otd:.1%} is below acceptable threshold (80%).",
        )

    # --- Defect rate ---
    defect_rate = kpi_row["defect_rate"]
    if defect_rate > 0.06:
        add(
            "high_defect_rate",
            "critical",
            f"Defect rate {defect_rate:.2%} exceeds critical threshold (6%).",
        )
    elif defect_rate > 0.03:
        add(
            "high_defect_rate",
            "high",
            f"Defect rate {defect_rate:.2%} exceeds warning threshold (3%).",
        )

    # --- Sentiment ---
    if row["sentiment_risk"] >= 60:
        add(
            "negative_sentiment",
            "high",
            f"Sentiment risk score {row['sentiment_risk']:.1f}/100 — "
            "predominantly negative news coverage detected.",
        )

    # --- Geopolitical ---
    if row["geo_risk"] >= 55:
        add(
            "geopolitical_exposure",
            "medium",
            f"Country risk score {row['geo_risk']:.0f}/100 — "
            f"elevated geopolitical exposure for {row['country']}.",
        )

    # --- Concentration ---
    conc = kpi_row["concentration_pct"]
    if conc >= 15:
        add(
            "high_concentration",
            "high",
            f"Supplier represents {conc:.1f}% of total portfolio spend — "
            "exceeds 15% concentration risk threshold.",
        )
    elif conc >= 8:
        add(
            "high_concentration",
            "medium",
            f"Supplier represents {conc:.1f}% of total portfolio spend — "
            "approaching 8% concentration warning level.",
        )

    return alerts


def generate_alerts(
    risk_df: pd.DataFrame,
    kpi_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    risk_df : output of features.risk_scorer.compute_risk_scores
    kpi_df  : output of features.kpi_engine.compute_kpis

    Returns
    -------
    DataFrame of alert records matching the SupplierAlert Pydantic schema.
    """
    kpi_index = kpi_df.set_index("supplier_name")
    all_alerts: list[dict] = []

    for _, row in risk_df.iterrows():
        kpi_row = kpi_index.loc[row["supplier_name"]]
        all_alerts.extend(_rules(row, kpi_row))

    if not all_alerts:
        return pd.DataFrame(columns=[
            "supplier_name", "alert_type", "severity", "message", "triggered_at"
        ])

    return pd.DataFrame(all_alerts)
