"""
Intelligence orchestrator: generates risk briefs and alerts for all suppliers.

Prerequisites:
    data/processed/risk_scores.csv   (from scripts/run_pipeline.py)
    data/processed/supplier_kpis.csv (from scripts/run_pipeline.py)

Outputs:
    data/processed/supplier_briefs.csv
    data/processed/supplier_alerts.csv
    DuckDB tables: supplier_briefs, supplier_alerts
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from config import USE_MOCK_BRIEF
from intelligence.alert_engine import generate_alerts
from intelligence.mock_brief_generator import get_mock_brief
from database.db_writer import write_alerts, write_briefs

RISK_PATH    = "data/processed/risk_scores.csv"
KPI_PATH     = "data/processed/supplier_kpis.csv"
BRIEFS_PATH  = "data/processed/supplier_briefs.csv"
ALERTS_PATH  = "data/processed/supplier_alerts.csv"


def _get_brief_for_row(row: pd.Series, kpi_row: pd.Series) -> str:
    if USE_MOCK_BRIEF:
        return get_mock_brief(row["supplier_name"], row["tier"], row["composite_score"])

    from intelligence.brief_generator import get_brief
    return get_brief(
        supplier_name      = row["supplier_name"],
        country            = row["country"],
        composite_score    = row["composite_score"],
        tier               = row["tier"],
        otd_risk           = row["otd_risk"],
        ltv_risk           = row["ltv_risk"],
        defect_risk        = row["defect_risk"],
        sentiment_risk     = row["sentiment_risk"],
        geo_risk           = row["geo_risk"],
        concentration_risk = row["concentration_risk"],
        otd_rate           = kpi_row["otd_rate"],
        defect_rate        = kpi_row["defect_rate"],
        avg_lead_time_days = kpi_row["avg_lead_time_days"],
        concentration_pct  = kpi_row["concentration_pct"],
    )


def main() -> None:
    os.makedirs("data/processed", exist_ok=True)

    if not os.path.exists(RISK_PATH) or not os.path.exists(KPI_PATH):
        print("[intelligence] ERROR: run scripts/run_pipeline.py first.")
        sys.exit(1)

    risk = pd.read_csv(RISK_PATH)
    kpis = pd.read_csv(KPI_PATH)
    kpi_index = kpis.set_index("supplier_name")

    mode = "MOCK" if USE_MOCK_BRIEF else "CLAUDE API"
    print(f"[intelligence] Generating briefs for {len(risk)} suppliers [{mode}]...")

    brief_rows = []
    now = datetime.now(timezone.utc).isoformat()

    for _, row in risk.iterrows():
        kpi_row    = kpi_index.loc[row["supplier_name"]]
        brief_text = _get_brief_for_row(row, kpi_row)
        brief_rows.append({
            "supplier_name":   row["supplier_name"],
            "composite_score": row["composite_score"],
            "tier":            row["tier"],
            "brief_text":      brief_text,
            "generated_at":    now,
        })
        print(f"  [{row['tier'].upper():8s}] {row['supplier_name']}")

    briefs_df = pd.DataFrame(brief_rows)
    briefs_df.to_csv(BRIEFS_PATH, index=False)
    write_briefs(briefs_df)

    print(f"\n[intelligence] Generating alerts...")
    alerts_df = generate_alerts(risk, kpis)
    alerts_df.to_csv(ALERTS_PATH, index=False)
    write_alerts(alerts_df)

    print(f"\n[intelligence] Complete.")
    print(f"  Briefs : {len(briefs_df)} -> {BRIEFS_PATH}")
    print(f"  Alerts : {len(alerts_df)} -> {ALERTS_PATH}")

    if len(alerts_df):
        sev_counts = alerts_df["severity"].value_counts().to_dict()
        print(f"  Alert severity breakdown: {sev_counts}")


if __name__ == "__main__":
    main()
