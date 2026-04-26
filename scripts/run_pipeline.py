"""
End-to-end pipeline orchestrator: ingest -> KPI -> sentiment -> score -> persist.

Steps
-----
1. Load raw supply chain and country risk data
2. Compute KPIs
3. Load sentiment scores (from data/processed/sentiment_scores.csv if available,
   otherwise generate and score headlines inline — slower, downloads FinBERT)
4. Compute composite risk scores
5. Write KPIs, sentiment, and risk scores to CSV and DuckDB
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd

from ingestion.sc_loader import load_supply_chain
from ingestion.country_risk_loader import get_risk_map
from features.kpi_engine import compute_kpis
from features.news_generator import generate_headlines
from features.sentiment_engine import score_headlines
from features.risk_scorer import compute_risk_scores
from database.db_writer import write_kpis, write_sentiment, write_risk_scores

KPI_PATH       = "data/processed/supplier_kpis.csv"
SENTIMENT_PATH = "data/processed/sentiment_scores.csv"
HEADLINES_PATH = "data/processed/supplier_headlines.csv"
RISK_PATH      = "data/processed/risk_scores.csv"


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

    # ------------------------------------------------------------------
    # 1. Ingest
    # ------------------------------------------------------------------
    print("[pipeline] Loading raw data...")
    sc_df        = load_supply_chain()
    country_risk = get_risk_map()
    print(f"[pipeline] {len(sc_df):,} orders loaded, {len(country_risk)} countries")

    # ------------------------------------------------------------------
    # 2. KPIs
    # ------------------------------------------------------------------
    print("[pipeline] Computing KPIs...")
    kpis = compute_kpis(sc_df)
    kpis.to_csv(KPI_PATH, index=False)
    write_kpis(kpis)

    # ------------------------------------------------------------------
    # 3. Sentiment  (use cached CSV if already generated)
    # ------------------------------------------------------------------
    if os.path.exists(SENTIMENT_PATH):
        print(f"[pipeline] Loading cached sentiment scores from {SENTIMENT_PATH}")
        sentiment = pd.read_csv(SENTIMENT_PATH)
    else:
        print("[pipeline] Generating headlines and running FinBERT...")
        tier_map = {r["supplier_name"]: _otd_tier(r["otd_rate"]) for _, r in kpis.iterrows()}
        headlines_df = generate_headlines(list(tier_map.keys()), tier_map)
        headlines_df.to_csv(HEADLINES_PATH, index=False)
        sentiment = score_headlines(headlines_df)
        sentiment.to_csv(SENTIMENT_PATH, index=False)
    write_sentiment(sentiment)

    # ------------------------------------------------------------------
    # 4. Risk scoring
    # ------------------------------------------------------------------
    print("[pipeline] Computing composite risk scores...")
    risk = compute_risk_scores(kpis, sentiment, country_risk)
    risk.to_csv(RISK_PATH, index=False)
    write_risk_scores(risk)

    # ------------------------------------------------------------------
    # 5. Summary
    # ------------------------------------------------------------------
    print("\n[pipeline] Complete. Risk score summary:")
    summary = (
        risk[["supplier_name", "composite_score", "tier"]]
        .sort_values("composite_score", ascending=False)
    )
    print(summary.to_string(index=False))

    tier_counts = risk["tier"].value_counts()
    print(f"\nTier distribution: {tier_counts.to_dict()}")


if __name__ == "__main__":
    main()
