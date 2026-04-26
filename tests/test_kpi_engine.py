import pandas as pd
import pytest
from features.kpi_engine import compute_kpis


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "order_id":        ["O1", "O2", "O3", "O4"],
        "supplier_name":   ["SupA", "SupA", "SupB", "SupB"],
        "country":         ["Germany", "Germany", "China", "China"],
        "on_time":         [1, 0, 1, 1],
        "lead_time_days":  [10, 14, 20, 22],
        "quantity":        [100, 200, 150, 50],
        "unit_price":      [10.0, 10.0, 5.0, 5.0],
        "order_value":     [1000.0, 2000.0, 750.0, 250.0],
        "defective_units": [1, 4, 3, 0],
    })


def test_row_count(sample_df):
    kpis = compute_kpis(sample_df)
    assert len(kpis) == 2


def test_otd_rate(sample_df):
    kpis = compute_kpis(sample_df).set_index("supplier_name")
    assert kpis.loc["SupA", "otd_rate"] == pytest.approx(0.5)
    assert kpis.loc["SupB", "otd_rate"] == pytest.approx(1.0)


def test_defect_rate(sample_df):
    kpis = compute_kpis(sample_df).set_index("supplier_name")
    # SupA: 5 defective / 300 quantity
    assert kpis.loc["SupA", "defect_rate"] == pytest.approx(5 / 300)


def test_concentration_sums_to_100(sample_df):
    kpis = compute_kpis(sample_df)
    assert kpis["concentration_pct"].sum() == pytest.approx(100.0)


def test_avg_lead_time(sample_df):
    kpis = compute_kpis(sample_df).set_index("supplier_name")
    assert kpis.loc["SupA", "avg_lead_time_days"] == pytest.approx(12.0)


def test_output_columns(sample_df):
    expected = {
        "supplier_name", "country", "total_orders", "otd_rate",
        "avg_lead_time_days", "lead_time_std", "defect_rate",
        "total_quantity", "order_volume", "concentration_pct",
    }
    kpis = compute_kpis(sample_df)
    assert set(kpis.columns) == expected
