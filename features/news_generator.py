"""
Generate synthetic news headlines per supplier using tier-weighted templates.
Headline language is intentionally realistic so FinBERT produces meaningful scores.
Each supplier receives 8-15 headlines drawn from templates matching its expected tier.
"""

import random
import pandas as pd

random.seed(42)

N_HEADLINES_MIN = 8
N_HEADLINES_MAX = 15

# ---------------------------------------------------------------------------
# Headline template pools — keyed by risk tier.
# Placeholders: {supplier} = supplier name.
# ---------------------------------------------------------------------------
TEMPLATES = {
    "low": [
        "{supplier} achieves record on-time delivery rate in Q3, exceeding customer expectations",
        "{supplier} wins supplier excellence award for third consecutive year",
        "{supplier} expands production capacity with new automated assembly line",
        "{supplier} reports zero quality escapes across all shipments in H1",
        "{supplier} signs long-term contract extension with major automotive OEM",
        "{supplier} certified to new ISO 9001:2025 quality management standard",
        "{supplier} completes lean manufacturing programme, reducing lead times by 12%",
        "{supplier} recognised as preferred supplier by industry association",
        "{supplier} posts strongest quarterly revenue since founding",
        "{supplier} implements digital traceability system across full supply chain",
        "{supplier} announces investment in renewable energy for manufacturing operations",
        "{supplier} reports zero labour disputes following new workforce agreement",
    ],
    "medium": [
        "{supplier} faces minor logistics delays linked to regional port congestion",
        "{supplier} reports slight increase in defect returns, investigation under way",
        "{supplier} navigating raw material cost pressures amid market volatility",
        "{supplier} delivery performance dips in Q2, management issues corrective action plan",
        "{supplier} reviewing supplier base after subcomponent quality concerns emerge",
        "{supplier} financial results mixed as revenue grows but margins narrow",
        "{supplier} under review following two late shipments to key accounts",
        "{supplier} investing in quality systems after customer audit findings",
        "{supplier} adjusting production schedule following equipment downtime",
        "{supplier} reports moderate increase in lead time variability due to labour shortage",
        "{supplier} faces currency headwinds impacting export competitiveness",
        "{supplier} customer satisfaction scores decline slightly in annual survey",
    ],
    "high": [
        "{supplier} hit with significant quality recall affecting three product lines",
        "{supplier} delivery failures surge as logistics infrastructure struggles",
        "{supplier} faces regulatory investigation over export compliance violations",
        "{supplier} workers strike for second week, halting production at main plant",
        "{supplier} reports major financial losses as orders decline sharply",
        "{supplier} loses key account after repeated shipment delays",
        "{supplier} under scrutiny following failed third-party quality audit",
        "{supplier} management shakeup after board cites operational failures",
        "{supplier} forced to idle capacity as input shortages worsen",
        "{supplier} credit rating downgraded by rating agency amid financial stress",
        "{supplier} investigated for labour practice violations at overseas facility",
        "{supplier} customers accelerating dual-sourcing strategies amid reliability concerns",
        "{supplier} production suspended at primary plant following safety inspection",
    ],
    "critical": [
        "{supplier} on verge of insolvency as creditors demand immediate repayment",
        "{supplier} operations halted following government sanctions announcement",
        "{supplier} massive quality failure triggers multi-million dollar liability claim",
        "{supplier} plant shut down indefinitely after catastrophic safety incident",
        "{supplier} executives arrested on fraud charges related to financial reporting",
        "{supplier} faces class-action lawsuit over systemic product defects",
        "{supplier} fails to deliver on critical orders for fourth consecutive quarter",
        "{supplier} supply chain completely disrupted as key logistics partner exits",
        "{supplier} blacklisted by major retailer following repeated non-compliance",
        "{supplier} emergency audit reveals widespread falsification of quality records",
        "{supplier} workers walk out indefinitely, threatening complete production collapse",
        "{supplier} under investigation by multiple government agencies simultaneously",
        "{supplier} rating withdrawn as financial transparency collapses",
        "{supplier} customers issue force majeure notices following delivery failures",
    ],
}

# Map expected tier to template weights so a high-risk supplier gets mostly
# high/critical headlines but still a few neutral ones (realistic signal noise).
TIER_WEIGHTS = {
    "low":      {"low": 0.70, "medium": 0.25, "high": 0.05, "critical": 0.00},
    "medium":   {"low": 0.15, "medium": 0.60, "high": 0.22, "critical": 0.03},
    "high":     {"low": 0.05, "medium": 0.20, "high": 0.55, "critical": 0.20},
    "critical": {"low": 0.02, "medium": 0.10, "high": 0.35, "critical": 0.53},
}


def _tier_for_supplier(supplier_name: str, tier_map: dict[str, str]) -> str:
    return tier_map.get(supplier_name, "medium")


def generate_headlines(
    suppliers: list[str],
    tier_map: dict[str, str],
) -> pd.DataFrame:
    """
    Parameters
    ----------
    suppliers : list of supplier names
    tier_map  : {supplier_name: tier} from a preliminary scoring or known mapping

    Returns
    -------
    DataFrame with columns: supplier_name, headline
    """
    rows = []
    for supplier in suppliers:
        tier = _tier_for_supplier(supplier, tier_map)
        weights = TIER_WEIGHTS[tier]
        tiers   = list(weights.keys())
        probs   = list(weights.values())

        n = random.randint(N_HEADLINES_MIN, N_HEADLINES_MAX)
        for _ in range(n):
            chosen_tier = random.choices(tiers, weights=probs, k=1)[0]
            template    = random.choice(TEMPLATES[chosen_tier])
            headline    = template.format(supplier=supplier)
            rows.append({"supplier_name": supplier, "headline": headline})

    return pd.DataFrame(rows)
