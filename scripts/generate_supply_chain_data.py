"""
Generate synthetic supply chain transaction data.
Output: data/raw/supply_chain.csv
  - 5,000 orders
  - 25 suppliers
  - 12 countries
  - 2022-01-01 to 2024-12-31
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import date, timedelta

random.seed(42)
np.random.seed(42)

OUTPUT_PATH = "data/raw/supply_chain.csv"

# ---------------------------------------------------------------------------
# Supplier master — 25 suppliers across 12 countries with tiered risk profiles
# Fields: name, country, otd_rate, avg_lead_days, lead_std, defect_rate,
#         avg_unit_price, order_weight  (relative share of 5,000 orders)
# ---------------------------------------------------------------------------
SUPPLIERS = [
    # --- LOW risk (6) ---
    {"name": "Alpine Precision GmbH",      "country": "Germany",     "otd_rate": 0.97, "avg_lead": 14, "lead_std": 1.5, "defect_rate": 0.003, "avg_price": 210, "weight": 6},
    {"name": "Bavarian Supply AG",          "country": "Germany",     "otd_rate": 0.96, "avg_lead": 13, "lead_std": 1.5, "defect_rate": 0.003, "avg_price": 195, "weight": 5},
    {"name": "KoreTech Manufacturing",      "country": "South Korea", "otd_rate": 0.96, "avg_lead": 18, "lead_std": 2.0, "defect_rate": 0.004, "avg_price": 185, "weight": 5},
    {"name": "TaipeiParts Co.",             "country": "Taiwan",      "otd_rate": 0.95, "avg_lead": 16, "lead_std": 2.5, "defect_rate": 0.005, "avg_price": 170, "weight": 5},
    {"name": "PolStar Industries",          "country": "Poland",      "otd_rate": 0.94, "avg_lead": 12, "lead_std": 1.8, "defect_rate": 0.004, "avg_price": 155, "weight": 4},
    {"name": "Monterrey Components SA",     "country": "Mexico",      "otd_rate": 0.93, "avg_lead": 10, "lead_std": 2.0, "defect_rate": 0.006, "avg_price": 145, "weight": 4},

    # --- MEDIUM risk (8) ---
    {"name": "Seoul Parts Ltd",             "country": "South Korea", "otd_rate": 0.88, "avg_lead": 20, "lead_std": 3.5, "defect_rate": 0.016, "avg_price": 165, "weight": 5},
    {"name": "Warsaw Precision Sp.",        "country": "Poland",      "otd_rate": 0.89, "avg_lead": 14, "lead_std": 3.0, "defect_rate": 0.015, "avg_price": 140, "weight": 4},
    {"name": "Hanoi Industrial Ltd",        "country": "Vietnam",     "otd_rate": 0.88, "avg_lead": 22, "lead_std": 4.0, "defect_rate": 0.018, "avg_price": 95,  "weight": 5},
    {"name": "Bangkok Parts Co.",           "country": "Thailand",    "otd_rate": 0.86, "avg_lead": 20, "lead_std": 4.5, "defect_rate": 0.020, "avg_price": 90,  "weight": 4},
    {"name": "Istanbul Fabrications",       "country": "Turkey",      "otd_rate": 0.85, "avg_lead": 19, "lead_std": 5.0, "defect_rate": 0.022, "avg_price": 120, "weight": 4},
    {"name": "Guadalajara Parts MX",        "country": "Mexico",      "otd_rate": 0.87, "avg_lead": 15, "lead_std": 3.5, "defect_rate": 0.019, "avg_price": 110, "weight": 4},
    {"name": "Kraków Components Sp.",       "country": "Poland",      "otd_rate": 0.86, "avg_lead": 16, "lead_std": 4.0, "defect_rate": 0.020, "avg_price": 135, "weight": 3},
    {"name": "São Paulo Supplies Ltda",     "country": "Brazil",      "otd_rate": 0.84, "avg_lead": 24, "lead_std": 5.5, "defect_rate": 0.025, "avg_price": 105, "weight": 3},

    # --- HIGH risk (7) ---
    {"name": "Shenzhen Global Supply",      "country": "China",       "otd_rate": 0.78, "avg_lead": 28, "lead_std": 8.0, "defect_rate": 0.042, "avg_price": 75,  "weight": 6},
    {"name": "Guangzhou Fabricators",       "country": "China",       "otd_rate": 0.75, "avg_lead": 32, "lead_std": 10.0,"defect_rate": 0.050, "avg_price": 70,  "weight": 5},
    {"name": "Chengdu Parts Factory",       "country": "China",       "otd_rate": 0.76, "avg_lead": 31, "lead_std": 9.0, "defect_rate": 0.048, "avg_price": 68,  "weight": 4},
    {"name": "Mumbai Parts Pvt Ltd",        "country": "India",       "otd_rate": 0.76, "avg_lead": 30, "lead_std": 9.0, "defect_rate": 0.048, "avg_price": 80,  "weight": 4},
    {"name": "Delhi Manufacturing Co.",     "country": "India",       "otd_rate": 0.77, "avg_lead": 29, "lead_std": 8.5, "defect_rate": 0.045, "avg_price": 82,  "weight": 4},
    {"name": "Ho Chi Minh Suppliers",       "country": "Vietnam",     "otd_rate": 0.74, "avg_lead": 33, "lead_std": 9.5, "defect_rate": 0.052, "avg_price": 72,  "weight": 3},
    {"name": "Dhaka Textile Exports",       "country": "Bangladesh",  "otd_rate": 0.73, "avg_lead": 35, "lead_std": 10.5,"defect_rate": 0.055, "avg_price": 55,  "weight": 3},

    # --- CRITICAL risk (4) ---
    {"name": "Wuhan Industrial Corp",       "country": "China",       "otd_rate": 0.63, "avg_lead": 38, "lead_std": 13.0,"defect_rate": 0.070, "avg_price": 60,  "weight": 3},
    {"name": "Chittagong Export Ltd",       "country": "Bangladesh",  "otd_rate": 0.62, "avg_lead": 40, "lead_std": 14.0,"defect_rate": 0.072, "avg_price": 48,  "weight": 2},
    {"name": "Kolkata Bulk Traders",        "country": "India",       "otd_rate": 0.60, "avg_lead": 42, "lead_std": 15.0,"defect_rate": 0.078, "avg_price": 52,  "weight": 2},
    {"name": "Lagos Components Ltd",        "country": "Bangladesh",  "otd_rate": 0.58, "avg_lead": 45, "lead_std": 16.0,"defect_rate": 0.075, "avg_price": 45,  "weight": 2},
]

N_ORDERS = 5_000
START_DATE = date(2022, 1, 1)
END_DATE   = date(2024, 12, 31)
DATE_RANGE_DAYS = (END_DATE - START_DATE).days


def random_order_date() -> date:
    return START_DATE + timedelta(days=random.randint(0, DATE_RANGE_DAYS))


def generate_orders(supplier: dict, n: int) -> list[dict]:
    rows = []
    for _ in range(n):
        order_date = random_order_date()

        # Promised lead time: draw from supplier's avg ± small buffer
        promised_days = max(5, int(np.random.normal(supplier["avg_lead"], supplier["lead_std"] * 0.5)))
        promised_delivery = order_date + timedelta(days=promised_days)

        # Actual delivery: on-time draws arrive at or before promised date;
        # late draws add a random delay proportional to lead_std
        on_time = random.random() < supplier["otd_rate"]
        if on_time:
            delay = random.randint(-2, 0)           # up to 2 days early
        else:
            delay = random.randint(1, max(2, int(supplier["lead_std"] * 2)))

        actual_delivery = promised_delivery + timedelta(days=delay)
        lead_time_days  = (actual_delivery - order_date).days

        quantity    = random.randint(50, 500)
        unit_price  = round(max(10.0, np.random.normal(supplier["avg_price"], supplier["avg_price"] * 0.10)), 2)
        order_value = round(quantity * unit_price, 2)

        # Defective units drawn from a binomial
        defective_units = int(np.random.binomial(quantity, supplier["defect_rate"]))

        rows.append({
            "order_id":            f"ORD-{len(rows):05d}",
            "supplier_name":       supplier["name"],
            "country":             supplier["country"],
            "order_date":          order_date.isoformat(),
            "promised_delivery":   promised_delivery.isoformat(),
            "actual_delivery":     actual_delivery.isoformat(),
            "on_time":             int(on_time),
            "lead_time_days":      lead_time_days,
            "quantity":            quantity,
            "unit_price":          unit_price,
            "order_value":         order_value,
            "defective_units":     defective_units,
        })
    return rows


def main() -> None:
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    total_weight = sum(s["weight"] for s in SUPPLIERS)
    all_rows: list[dict] = []

    for supplier in SUPPLIERS:
        n = round(N_ORDERS * supplier["weight"] / total_weight)
        all_rows.extend(generate_orders(supplier, n))

    # Shuffle and assign globally unique order IDs
    random.shuffle(all_rows)
    for i, row in enumerate(all_rows):
        row["order_id"] = f"ORD-{i+1:05d}"

    df = pd.DataFrame(all_rows)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Generated {len(df):,} orders across {df['supplier_name'].nunique()} suppliers "
          f"in {df['country'].nunique()} countries -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
