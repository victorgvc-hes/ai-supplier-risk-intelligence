"""
Generate country risk lookup table derived from World Bank governance indicators.
Scores are mapped to a 0-100 scale where higher = more risky.
Output: data/raw/country_risk.csv
"""

import os
import pandas as pd

OUTPUT_PATH = "data/raw/country_risk.csv"

# Country risk scores (0-100, higher = riskier) based on World Bank
# Worldwide Governance Indicators: rule of law, political stability,
# control of corruption, government effectiveness — inverted and normalised.
COUNTRY_RISK = [
    # country,          geo_risk_score, region,           notes
    ("Germany",         5,  "Europe",        "Strong institutions, rule of law"),
    ("South Korea",     12, "Asia-Pacific",  "High governance, minor geopolitical tension"),
    ("Taiwan",          18, "Asia-Pacific",  "Cross-strait tension risk"),
    ("Poland",          15, "Europe",        "Solid EU governance, moderate political risk"),
    ("Mexico",          42, "Latin America", "Organised crime, regulatory volatility"),
    ("South Korea",     12, "Asia-Pacific",  "High governance, minor geopolitical tension"),
    ("Vietnam",         35, "Southeast Asia","Single-party state, improving governance"),
    ("Thailand",        38, "Southeast Asia","Political instability, military influence"),
    ("Turkey",          48, "Middle East",   "Currency volatility, rule-of-law concerns"),
    ("Brazil",          45, "Latin America", "Corruption risk, regulatory uncertainty"),
    ("China",           55, "Asia-Pacific",  "Geopolitical tensions, regulatory opacity"),
    ("India",           40, "South Asia",    "Bureaucratic risk, improving but uneven"),
    ("Bangladesh",      62, "South Asia",    "Labour rights, political instability, flooding risk"),
]

# Deduplicate by country (keep first occurrence)
seen = set()
unique_rows = []
for row in COUNTRY_RISK:
    if row[0] not in seen:
        seen.add(row[0])
        unique_rows.append(row)


def main() -> None:
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    df = pd.DataFrame(unique_rows, columns=["country", "geo_risk_score", "region", "notes"])
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Country risk lookup written: {len(df)} countries -> {OUTPUT_PATH}")
    print(df[["country", "geo_risk_score", "region"]].to_string(index=False))


if __name__ == "__main__":
    main()
