RISK_WEIGHTS = {
    "otd": 0.25,
    "ltv": 0.20,
    "defect": 0.20,
    "sentiment": 0.15,
    "geo": 0.10,
    "concentration": 0.10,
}

RISK_TIERS = {
    "low": (0, 30),
    "medium": (31, 60),
    "high": (61, 80),
    "critical": (81, 100),
}

ALERT_THRESHOLD = 61

DB_PATH = "data/processed/supplier_risk.duckdb"

USE_MOCK_BRIEF = True

MODEL_NAME = "claude-sonnet-4-20250514"
