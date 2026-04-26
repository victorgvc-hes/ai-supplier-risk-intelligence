"""
Load the country risk lookup table and return a country -> geo_risk_score mapping.
"""

import pandas as pd

CR_PATH = "data/raw/country_risk.csv"


def load_country_risk(path: str = CR_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"country": str, "geo_risk_score": float})
    df = df.dropna(subset=["country", "geo_risk_score"])
    return df.reset_index(drop=True)


def get_risk_map(path: str = CR_PATH) -> dict[str, float]:
    """Return {country: geo_risk_score} for fast lookup."""
    df = load_country_risk(path)
    return dict(zip(df["country"], df["geo_risk_score"]))
