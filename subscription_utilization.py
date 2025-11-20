#!/usr/bin/env python3
"""
Analyze subscription package utilization by comparing expected subscription
events (based on package size) versus actual events recorded in master_tickets.
Outputs:
  - Updated patron_summary.csv with new utilization columns.
  - subscription_utilization_account_year.csv (per account/year/type).
  - subscription_utilization_accounts.csv (per account aggregate).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MASTER_PATH = BASE_DIR / "master_tickets.csv"
PATRON_PATH = BASE_DIR / "patron_summary.csv"
OUTPUT_ACCOUNT_YEAR = BASE_DIR / "subscription_utilization_account_year.csv"
OUTPUT_ACCOUNT = BASE_DIR / "subscription_utilization_accounts.csv"


def extract_package_size(label: str) -> Optional[int]:
    if not isinstance(label, str):
        return None
    match = re.search(r"(\d+)", label)
    if match:
        return int(match.group(1))
    return None


def main() -> None:
    df = pd.read_csv(MASTER_PATH)
    subs = df[
        (df["ticket_type"] == "Subscription") & df["price_code_type"].str.contains("Fixed", na=False)
    ].copy()

    if subs.empty:
        raise SystemExit("No fixed subscription records found.")

    subs["package_size"] = subs["price_code_type"].apply(extract_package_size)

    # Fallback: for labels without explicit size, infer median unique events per account-year.
    missing_types = subs[subs["package_size"].isna()]["price_code_type"].unique()
    if len(missing_types) > 0:
        fallback_sizes: Dict[str, float] = {}
        grouped = (
            subs[subs["price_code_type"].isin(missing_types)]
            .groupby(["price_code_type", "acct_id", "fiscal_year"])["event_name"]
            .nunique()
            .reset_index(name="events")
        )
        inferred = grouped.groupby("price_code_type")["events"].median()
        fallback_sizes = inferred.to_dict()
        subs.loc[subs["package_size"].isna(), "package_size"] = subs.loc[
            subs["package_size"].isna(), "price_code_type"
        ].map(fallback_sizes)

    subs["package_size"] = subs["package_size"].astype(float)

    group_cols = ["acct_id", "fiscal_year", "price_code_type"]
    account_year = (
        subs.groupby(group_cols)
        .agg(
            package_size=("package_size", "first"),
            actual_events=("event_name", "nunique"),
            tickets_sold=("num_seats", "sum"),
            avg_seats_per_event=("num_seats", "mean"),
        )
        .reset_index()
    )

    account_year["expected_events"] = account_year["package_size"]
    account_year["event_gap"] = account_year["expected_events"] - account_year["actual_events"]
    account_year["utilization_pct"] = account_year["actual_events"] / account_year["expected_events"]

    # Aggregate to account level (exclude rows without expected data)
    valid = account_year.dropna(subset=["expected_events"])
    account_summary = (
        valid.groupby("acct_id")
        .agg(
            subscription_expected_events=("expected_events", "sum"),
            subscription_actual_events=("actual_events", "sum"),
            subscription_event_gap=("event_gap", "sum"),
            subscription_utilization_pct=("utilization_pct", "mean"),
            subscription_packages=("price_code_type", "nunique"),
        )
        .reset_index()
    )

    # Update patron_summary.csv with new columns
    patron_df = pd.read_csv(PATRON_PATH)
    merged = patron_df.merge(account_summary, on="acct_id", how="left")
    merged.to_csv(PATRON_PATH, index=False)

    account_year.to_csv(OUTPUT_ACCOUNT_YEAR, index=False)
    account_summary.to_csv(OUTPUT_ACCOUNT, index=False)

    print(f"Updated patron summary with utilization columns ({PATRON_PATH.name}).")
    print(f"Wrote detailed account-year data to {OUTPUT_ACCOUNT_YEAR}.")
    print(f"Wrote aggregate account data to {OUTPUT_ACCOUNT}.")


if __name__ == "__main__":
    main()

