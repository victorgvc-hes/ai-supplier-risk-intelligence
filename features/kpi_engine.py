"""
Compute six KPI dimensions per supplier from raw order-level data.
Output columns match the SupplierKPI Pydantic schema.
"""

import pandas as pd


def compute_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parameters
    ----------
    df : raw supply chain DataFrame from ingestion.sc_loader

    Returns
    -------
    DataFrame with one row per supplier containing all KPI fields.
    """
    total_order_volume = df["order_value"].sum()

    agg = (
        df.groupby(["supplier_name", "country"])
        .agg(
            total_orders    =("order_id",        "count"),
            otd_rate        =("on_time",          "mean"),
            avg_lead_time_days=("lead_time_days", "mean"),
            lead_time_std   =("lead_time_days",   "std"),
            total_defective =("defective_units",  "sum"),
            total_quantity  =("quantity",         "sum"),
            order_volume    =("order_value",      "sum"),
        )
        .reset_index()
    )

    agg["defect_rate"]       = agg["total_defective"] / agg["total_quantity"]
    agg["concentration_pct"] = agg["order_volume"] / total_order_volume * 100
    agg["lead_time_std"]     = agg["lead_time_std"].fillna(0.0)

    return agg[[
        "supplier_name",
        "country",
        "total_orders",
        "otd_rate",
        "avg_lead_time_days",
        "lead_time_std",
        "defect_rate",
        "total_quantity",
        "order_volume",
        "concentration_pct",
    ]]
