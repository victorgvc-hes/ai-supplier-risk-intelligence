"""
Standalone FinBERT sentiment pipeline script.

Run order:
    1. scripts/run_pipeline.py  (produces data/processed/supplier_kpis.csv
                                 and data/processed/risk_scores.csv with
                                 a preliminary OTD-only tier for headline weighting)
    2. python features/run_sentiment.py

Outputs:
    data/processed/supplier_headlines.csv
    data/processed/sentiment_scores.csv
"""

import os
import pandas as pd

from ingestion.sc_loader import load_supply_chain
from features.kpi_engine import compute_kpis
from features.news_generator import generate_headlines
from features.sentiment_engine import score_headlines

HEADLINES_PATH = "data/processed/supplier_headlines.csv"
SENTIMENT_PATH = "data/processed/sentiment_scores.csv"
KPI_PATH       = "data/processed/supplier_kpis.csv"

# Preliminary tier mapping based on OTD rate alone — used to weight
# headline templates before full composite scoring is available.
def _otd_tier(otd_rate: float) -> str:
    if otd_rate >= 0.92:
        return "low"
    elif otd_rate >= 0.83:
        return "medium"
    elif otd_rate >= 0.72:
        return "high"
    return "critical"


def main() -> None:
    os.makedirs("data/processed", exist_ok=True)

    # Load KPIs (written by run_pipeline.py) or recompute from raw data
    if os.path.exists(KPI_PATH):
        kpis = pd.read_csv(KPI_PATH)
    else:
        df   = load_supply_chain()
        kpis = compute_kpis(df)

    tier_map = {
        row["supplier_name"]: _otd_tier(row["otd_rate"])
        for _, row in kpis.iterrows()
    }

    print(f"[sentiment] Generating headlines for {len(tier_map)} suppliers...")
    headlines_df = generate_headlines(list(tier_map.keys()), tier_map)
    headlines_df.to_csv(HEADLINES_PATH, index=False)
    print(f"[sentiment] {len(headlines_df)} headlines -> {HEADLINES_PATH}")

    sentiment_df = score_headlines(headlines_df)
    sentiment_df.to_csv(SENTIMENT_PATH, index=False)
    print(f"[sentiment] Sentiment scores -> {SENTIMENT_PATH}")
    print(sentiment_df[["supplier_name", "sentiment_risk_score"]].to_string(index=False))


if __name__ == "__main__":
    main()
