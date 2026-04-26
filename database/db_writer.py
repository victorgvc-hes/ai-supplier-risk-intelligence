"""
DuckDB persistence layer.
Each write function is idempotent: it drops and recreates the table on every run.
"""

import duckdb
import pandas as pd
from config import DB_PATH


def _connect() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(DB_PATH)


def _write(df: pd.DataFrame, table: str) -> None:
    con = _connect()
    con.execute(f"DROP TABLE IF EXISTS {table}")
    con.execute(f"CREATE TABLE {table} AS SELECT * FROM df")
    con.close()


def write_kpis(df: pd.DataFrame) -> None:
    _write(df, "supplier_kpis")
    print(f"[db] supplier_kpis written ({len(df)} rows)")


def write_sentiment(df: pd.DataFrame) -> None:
    _write(df, "sentiment_scores")
    print(f"[db] sentiment_scores written ({len(df)} rows)")


def write_risk_scores(df: pd.DataFrame) -> None:
    _write(df, "risk_scores")
    print(f"[db] risk_scores written ({len(df)} rows)")


def write_alerts(df: pd.DataFrame) -> None:
    _write(df, "supplier_alerts")
    print(f"[db] supplier_alerts written ({len(df)} rows)")


def write_briefs(df: pd.DataFrame) -> None:
    _write(df, "supplier_briefs")
    print(f"[db] supplier_briefs written ({len(df)} rows)")


def read_table(table: str) -> pd.DataFrame:
    con = _connect()
    df  = con.execute(f"SELECT * FROM {table}").df()
    con.close()
    return df
