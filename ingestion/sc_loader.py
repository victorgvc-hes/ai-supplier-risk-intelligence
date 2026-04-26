"""
Load and clean the raw supply chain CSV into a typed DataFrame.
"""

import pandas as pd

SC_PATH = "data/raw/supply_chain.csv"

DTYPES = {
    "order_id":        str,
    "supplier_name":   str,
    "country":         str,
    "on_time":         int,
    "lead_time_days":  int,
    "quantity":        int,
    "unit_price":      float,
    "order_value":     float,
    "defective_units": int,
}

DATE_COLS = ["order_date", "promised_delivery", "actual_delivery"]


def load_supply_chain(path: str = SC_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=DTYPES, parse_dates=DATE_COLS)
    df = df.dropna(subset=["supplier_name", "country", "order_date"])
    df = df[df["quantity"] > 0]
    df = df[df["order_value"] > 0]
    return df.reset_index(drop=True)
