_TEMPLATES = {
    "low": (
        "{supplier} is currently a low-risk supplier with a composite risk score of {score}/100. "
        "Operational metrics are within acceptable thresholds, and no significant geopolitical or "
        "sentiment concerns have been identified. Continued monitoring is advised to ensure "
        "performance remains stable across lead time and quality dimensions."
    ),
    "medium": (
        "{supplier} presents a medium risk profile with a composite score of {score}/100, indicating "
        "some areas that warrant closer attention. Minor deviations in on-time delivery or lead time "
        "variability have been observed, alongside mixed sentiment signals from recent news coverage. "
        "Procurement teams should schedule a performance review and consider contingency sourcing "
        "for non-critical categories."
    ),
    "high": (
        "{supplier} has been flagged as a high-risk supplier with a composite score of {score}/100, "
        "driven by elevated defect rates, delivery instability, or adverse geopolitical exposure. "
        "Recent news sentiment is predominantly negative, suggesting reputational or operational "
        "pressures. Immediate engagement with the supplier is recommended, and dual-sourcing "
        "strategies should be activated for critical components."
    ),
    "critical": (
        "{supplier} has reached a critical risk level with a composite score of {score}/100, "
        "representing a severe threat to supply chain continuity. Multiple risk dimensions — "
        "including quality failures, significant delivery delays, high geographic concentration, "
        "and strongly negative media sentiment — are contributing to this assessment. "
        "Escalation to senior procurement leadership is required, and contingency supply "
        "plans should be enacted immediately to mitigate disruption exposure."
    ),
}


def get_mock_brief(supplier_name: str, tier: str, score: float) -> str:
    template = _TEMPLATES.get(tier, _TEMPLATES["medium"])
    return template.format(supplier=supplier_name, score=round(score, 1))
