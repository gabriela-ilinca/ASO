#!/usr/bin/env python3
"""
Scenario modeling for special-event single tickets.
Splits demand between subscriber accounts (buyers with any subscription history)
and non-subscriber accounts, then simulates price changes using inverse-demand
elasticity estimates. Outputs CSV grids into demand_curve_findings/.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "master_tickets.csv"
OUTPUT_DIR = BASE_DIR / "demand_curve_findings"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df[df["purchase_price"] > 0].copy()
    df["num_seats"] = df["num_seats"].fillna(1)
    df["acct_id"] = df["acct_id"].astype(str)
    return df


def build_inverse_demand(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    if df.empty:
        return None
    agg = (
        df.groupby("purchase_price")
        .agg(
            seats_sold=("num_seats", "sum"),
            transactions=("acct_id", "count"),
            unique_events=("event_name", pd.Series.nunique),
            total_revenue=("paid_amount", "sum"),
        )
        .reset_index()
        .sort_values("purchase_price", ascending=False)
    )
    agg = agg[agg["seats_sold"] > 0].copy()
    if agg.empty:
        return None
    agg["cumulative_quantity"] = agg["seats_sold"].cumsum()
    total_qty = agg["seats_sold"].sum()
    agg["cumulative_share"] = agg["cumulative_quantity"] / total_qty
    agg["avg_price"] = (df["purchase_price"] * df["num_seats"]).sum() / total_qty
    return agg


def estimate_elasticity(curve: pd.DataFrame) -> Optional[Dict[str, float]]:
    if curve is None or curve["purchase_price"].nunique() < 3:
        return None
    valid = curve[(curve["purchase_price"] > 0) & (curve["seats_sold"] > 0)]
    if valid.shape[0] < 3:
        return None
    X = np.log(valid["purchase_price"]).values.reshape(-1, 1)
    y = np.log(valid["seats_sold"]).values
    model = LinearRegression()
    model.fit(X, y)
    return {"elasticity": float(model.coef_[0]), "r_squared": float(model.score(X, y))}


def simulate_price_shift(elasticity: float, pct_change: float) -> Dict[str, float]:
    qty_multiplier = (1 + pct_change) ** elasticity
    rev_multiplier = (1 + pct_change) * qty_multiplier
    return {
        "delta_qty_pct": qty_multiplier - 1,
        "delta_revenue_pct": rev_multiplier - 1,
    }


def main() -> None:
    df = load_data()
    subscriber_accounts = set(df.loc[df["ticket_type"] == "Subscription", "acct_id"])
    special_single = df[(df["ticket_type"] == "Single Ticket") & (df["Type"] == "Special")]

    segments = {
        "special_single_subscriber_accounts": special_single[
            special_single["acct_id"].isin(subscriber_accounts)
        ],
        "special_single_non_subscriber_accounts": special_single[
            ~special_single["acct_id"].isin(subscriber_accounts)
        ],
    }

    price_changes = [-0.10, -0.07, -0.05, 0.05, 0.07, 0.10]
    grid_rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []

    for label, subset in segments.items():
        curve = build_inverse_demand(subset)
        elasticity_meta = estimate_elasticity(curve) if curve is not None else None

        summary_rows.append(
            {
                "segment": label,
                "seats_observed": int(subset["num_seats"].sum()),
                "avg_price": round(curve["avg_price"].iloc[0], 2) if curve is not None else np.nan,
                "elasticity": round(elasticity_meta["elasticity"], 3)
                if elasticity_meta
                else np.nan,
                "r_squared": round(elasticity_meta["r_squared"], 3)
                if elasticity_meta
                else np.nan,
                "notes": "Special-event single tickets",
            }
        )

        if curve is None or elasticity_meta is None:
            continue

        avg_price = curve["avg_price"].iloc[0]
        elasticity = elasticity_meta["elasticity"]

        for pct in price_changes:
            deltas = simulate_price_shift(elasticity, pct)
            grid_rows.append(
                {
                    "segment": label,
                    "price_change_pct": pct * 100,
                    "new_price_est": round(avg_price * (1 + pct), 2),
                    "elasticity": round(elasticity, 3),
                    "delta_quantity_pct": round(deltas["delta_qty_pct"] * 100, 2),
                    "delta_revenue_pct": round(deltas["delta_revenue_pct"] * 100, 2),
                }
            )

    summary_df = pd.DataFrame(summary_rows)
    grid_df = pd.DataFrame(grid_rows)

    summary_path = OUTPUT_DIR / "special_event_single_ticket_simulation_summary.csv"
    grid_path = OUTPUT_DIR / "special_event_single_ticket_simulation_grid.csv"
    summary_df.to_csv(summary_path, index=False)
    grid_df.to_csv(grid_path, index=False)

    print(f"Saved {summary_path}")
    print(f"Saved {grid_path}")

    if not grid_df.empty:
        top_positive = (
            grid_df[grid_df["price_change_pct"] > 0]
            .sort_values("delta_revenue_pct", ascending=False)
            .head(5)
        )
        print("\nTop revenue scenarios (positive price moves):")
        print(top_positive.to_string(index=False))

        top_negative = (
            grid_df[grid_df["price_change_pct"] < 0]
            .sort_values("delta_revenue_pct", ascending=False)
            .head(5)
        )
        print("\nBest markdown scenarios (revenue impact):")
        print(top_negative.to_string(index=False))


if __name__ == "__main__":
    main()

