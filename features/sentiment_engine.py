"""
FinBERT sentiment scoring pipeline.
Scores each headline as positive / neutral / negative using ProsusAI/finbert,
then aggregates to supplier-level sentiment risk score (0-100).
"""

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_ID = "ProsusAI/finbert"
LABELS   = ["positive", "negative", "neutral"]   # FinBERT output order


def _load_model(device: str):
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model     = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
    model.to(device)
    model.eval()
    return tokenizer, model


def _score_batch(
    headlines: list[str],
    tokenizer,
    model,
    device: str,
) -> list[dict]:
    inputs = tokenizer(
        headlines,
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors="pt",
    ).to(device)

    with torch.no_grad():
        logits = model(**inputs).logits
        probs  = torch.softmax(logits, dim=-1).cpu().numpy()

    # FinBERT id2label: {0: positive, 1: negative, 2: neutral}
    results = []
    for p in probs:
        results.append({
            "positive": float(p[0]),
            "negative": float(p[1]),
            "neutral":  float(p[2]),
        })
    return results


def score_headlines(
    headlines_df: pd.DataFrame,
    batch_size: int = 16,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    headlines_df : DataFrame with columns [supplier_name, headline]
    batch_size   : number of headlines per inference batch

    Returns
    -------
    DataFrame with one row per supplier:
        supplier_name, headline_count,
        positive_pct, neutral_pct, negative_pct,
        sentiment_risk_score
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[sentiment] Loading FinBERT on {device}...")
    tokenizer, model = _load_model(device)

    all_headlines = headlines_df["headline"].tolist()
    scored_rows: list[dict] = []

    for i in range(0, len(all_headlines), batch_size):
        batch  = all_headlines[i: i + batch_size]
        scores = _score_batch(batch, tokenizer, model, device)
        scored_rows.extend(scores)

    scored_df = headlines_df.copy().reset_index(drop=True)
    scored_df["positive"] = [r["positive"] for r in scored_rows]
    scored_df["negative"] = [r["negative"] for r in scored_rows]
    scored_df["neutral"]  = [r["neutral"]  for r in scored_rows]

    agg = (
        scored_df.groupby("supplier_name")
        .agg(
            headline_count=("headline",  "count"),
            positive_pct  =("positive",  "mean"),
            neutral_pct   =("neutral",   "mean"),
            negative_pct  =("negative",  "mean"),
        )
        .reset_index()
    )

    # Sentiment risk score: negative share on 0-100 scale
    agg["sentiment_risk_score"] = (agg["negative_pct"] * 100).round(2)

    return agg[[
        "supplier_name",
        "headline_count",
        "positive_pct",
        "neutral_pct",
        "negative_pct",
        "sentiment_risk_score",
    ]]
