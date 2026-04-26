"""
Claude API risk narrative generator.
Builds a structured prompt from supplier KPIs and risk scores,
then calls the Anthropic API to produce a 3-4 sentence risk brief.

Requires ANTHROPIC_API_KEY in environment (loaded from .env).
Only called when config.USE_MOCK_BRIEF = False.
"""

import os
import anthropic
from dotenv import load_dotenv
from config import MODEL_NAME

load_dotenv()


def _build_prompt(
    supplier_name: str,
    country: str,
    composite_score: float,
    tier: str,
    otd_risk: float,
    ltv_risk: float,
    defect_risk: float,
    sentiment_risk: float,
    geo_risk: float,
    concentration_risk: float,
    otd_rate: float,
    defect_rate: float,
    avg_lead_time_days: float,
    concentration_pct: float,
) -> str:
    return f"""You are a senior procurement risk analyst. Write a concise 3-4 sentence supplier risk brief for use in an executive risk dashboard.

Supplier: {supplier_name}
Country: {country}
Risk Tier: {tier.upper()}
Composite Risk Score: {composite_score:.1f} / 100

Risk Dimension Scores (0-100, higher = riskier):
- On-time delivery risk:     {otd_risk:.1f}  (actual OTD rate: {otd_rate:.1%})
- Lead time variability:     {ltv_risk:.1f}
- Defect / quality risk:     {defect_risk:.1f}  (actual defect rate: {defect_rate:.2%})
- News sentiment risk:       {sentiment_risk:.1f}
- Geopolitical risk:         {geo_risk:.1f}
- Concentration risk:        {concentration_risk:.1f}  (portfolio share: {concentration_pct:.1f}%)
- Average lead time:         {avg_lead_time_days:.1f} days

Instructions:
- Summarise the supplier's overall risk posture in one sentence.
- Identify the one or two most significant risk drivers with specific values.
- Recommend one concrete procurement action appropriate to the risk tier.
- Tone: professional, direct, data-grounded. No bullet points. Plain prose only."""


def get_brief(
    supplier_name: str,
    country: str,
    composite_score: float,
    tier: str,
    otd_risk: float,
    ltv_risk: float,
    defect_risk: float,
    sentiment_risk: float,
    geo_risk: float,
    concentration_risk: float,
    otd_rate: float,
    defect_rate: float,
    avg_lead_time_days: float,
    concentration_pct: float,
) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = _build_prompt(
        supplier_name, country, composite_score, tier,
        otd_risk, ltv_risk, defect_risk, sentiment_risk, geo_risk, concentration_risk,
        otd_rate, defect_rate, avg_lead_time_days, concentration_pct,
    )

    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text.strip()
