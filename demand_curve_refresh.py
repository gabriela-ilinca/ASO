#!/usr/bin/env python3
"""
Generate demand curves and price sensitivity analysis for ASO ticketing data.
Outputs are saved into demand_curve_findings/.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.linear_model import LinearRegression  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "master_tickets.csv"
OUTPUT_DIR = BASE_DIR / "demand_curve_findings"
OUTPUT_DIR.mkdir(exist_ok=True)

# Seat group definitions
PREMIUM_SECTIONS = {"ORCHL", "ORCHR", "LOGEL", "LOGER"}
SECTION_GROUP_MAP = {
    "ORCHL": "Premium Orchestra",
    "ORCHR": "Premium Orchestra",
    "LOGEL": "Front Loge",
    "LOGER": "Front Loge",
    "DRESSL": "Dress Circle",
    "DRESSR": "Dress Circle",
    "BALCL": "Balcony",
    "BALCR": "Balcony",
    "PITL": "Pit / GA",
    "PITR": "Pit / GA",
    "GA1": "Pit / GA",
    "GA2": "Pit / GA",
    "GA3": "Pit / GA",
}


def classify_fixed_detail(label: str) -> Optional[str]:
    """Return the more granular fixed subscription label, if applicable."""
    if not isinstance(label, str):
        return None

    lowered = label.lower()
    mapping = {
        "established": "Fixed - Established",
        "freshman": "Fixed - Freshman",
        "sophomore": "Fixed - Sophomore",
        "lapsed": "Fixed - Lapsed",
        "upgrade": "Fixed - Upgrade",
        "musician": "Fixed - Musician",
        "chorus": "Fixed - Chorus",
        "wheelchair": "Fixed - Wheelchair",
    }
    for keyword, friendly in mapping.items():
        if keyword in lowered:
            return friendly
    if "fixed" in lowered:
        return "Fixed - Other"
    return None


def classify_subscription_bucket(row: pd.Series) -> str:
    """Assign each record to a broader subscription bucket."""
    price_label = str(row.get("price_code_type", "")).lower()
    ticket_label = str(row.get("ticket_type", "")).lower()

    if "single ticket" in price_label or ticket_label == "single ticket":
        return "Single Ticket"
    if "cyo" in price_label:
        return "CYO Subscription"
    if "fixed" in price_label:
        return "Fixed Subscription"
    return "Other / Multi"


def build_inverse_demand(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Aggregate seats sold at each price point and compute cumulative quantities."""
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
    agg["share_of_total"] = agg["seats_sold"] / total_qty

    # Seat-weighted average price
    agg["avg_price"] = (
        df["purchase_price"] * df["num_seats"]
    ).sum() / total_qty

    # Add price dispersion metrics
    agg["price_std"] = df["purchase_price"].std()
    agg["price_cv"] = df["purchase_price"].std() / df["purchase_price"].mean() if df["purchase_price"].mean() > 0 else 0

    return agg


def save_curve(curve: pd.DataFrame, slug: str) -> Path:
    """Save the aggregated curve as CSV."""
    path = OUTPUT_DIR / f"{slug}.csv"
    curve.to_csv(path, index=False)
    return path


def plot_inverse_demand(
    curve: pd.DataFrame,
    title: str,
    slug: str,
    subtitle: Optional[str] = None,
    use_log_scale: bool = False,
) -> Path:
    """Plot a demand curve showing price vs cumulative quantity."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.step(
        curve["cumulative_quantity"],
        curve["purchase_price"],
        where="post",
        linewidth=2.0,
        color="#116A7B",
    )
    ax.scatter(
        curve["cumulative_quantity"],
        curve["purchase_price"],
        color="#1AC8ED",
        s=20,
        alpha=0.9,
    )
    if use_log_scale:
        ax.set_xscale("log")
        ax.set_xlabel("Cumulative Quantity (log scale)")
    else:
        ax.set_xlabel("Cumulative Quantity")
    ax.set_ylabel("Price (USD)")
    ax.set_title(title, fontsize=13, fontweight="bold")
    if subtitle:
        ax.text(
            0.02,
            0.02,
            subtitle,
            ha="left",
            va="bottom",
            transform=ax.transAxes,
            fontsize=9,
            color="#444444",
        )
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    fig.tight_layout()
    output_path = OUTPUT_DIR / f"{slug}.png"
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    return output_path


def plot_multi_curve(
    curves: Dict[str, pd.DataFrame],
    title: str,
    slug: str,
    use_log_scale: bool = False,
) -> Optional[Path]:
    """Plot multiple demand curves on the same chart for comparison."""
    if not curves:
        return None
    fig, ax = plt.subplots(figsize=(8.5, 6))
    palette = plt.cm.viridis(np.linspace(0.1, 0.9, len(curves)))
    for idx, (label, curve) in enumerate(curves.items()):
        if curve is None or curve.empty:
            continue
        ax.step(
            curve["cumulative_quantity"],
            curve["purchase_price"],
            where="post",
            linewidth=2.0,
            label=label,
            color=palette[idx],
        )
    if use_log_scale:
        ax.set_xscale("log")
        ax.set_xlabel("Cumulative Quantity (log scale)")
    else:
        ax.set_xlabel("Cumulative Quantity")
    ax.set_ylabel("Price (USD)")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(frameon=True)
    ax.grid(True, which="both", linestyle="--", alpha=0.35)
    fig.tight_layout()
    output_path = OUTPUT_DIR / f"{slug}.png"
    fig.savefig(output_path, dpi=220)
    plt.close(fig)
    return output_path


def estimate_price_elasticity(curve: pd.DataFrame) -> Optional[Dict[str, float]]:
    """Fit a log-log model to estimate price elasticity from the demand curve."""
    if curve is None or curve["purchase_price"].nunique() < 3:
        return None

    valid = curve[["purchase_price", "seats_sold"]].copy()
    valid = valid[(valid["purchase_price"] > 0) & (valid["seats_sold"] > 0)]
    if valid.shape[0] < 3:
        return None

    X = np.log(valid["purchase_price"]).values.reshape(-1, 1)
    y = np.log(valid["seats_sold"]).values

    model = LinearRegression()
    model.fit(X, y)
    elasticity = float(model.coef_[0])
    r_sq = float(model.score(X, y))

    # Compute robust standard error (heteroskedasticity-consistent)
    y_pred = model.predict(X)
    residuals = y - y_pred
    n = len(y)
    k = 1  # one regressor
    mse = np.sum(residuals**2) / (n - k - 1)

    # Simple standard error (not fully robust, but indicative)
    X_centered = X - X.mean()
    se_beta = np.sqrt(mse / np.sum(X_centered**2)) if np.sum(X_centered**2) > 0 else np.nan

    return {
        "elasticity": elasticity,
        "r_squared": r_sq,
        "std_error": float(se_beta),
        "n_price_points": int(len(valid)),
    }


def simulate_price_shift(
    elasticity: float,
    pct_change: float,
) -> Tuple[float, float]:
    """Return expected % change in quantity and revenue for a price shift."""
    qty_multiplier = (1 + pct_change) ** elasticity
    rev_multiplier = (1 + pct_change) * qty_multiplier
    return qty_multiplier - 1, rev_multiplier - 1


def summarize_segment(
    label: str,
    curve: Optional[pd.DataFrame],
    notes: str,
) -> Optional[Dict[str, object]]:
    """Build a summary row for price sensitivity with uncertainty quantification."""
    if curve is None or curve.empty:
        return None

    elasticity_meta = estimate_price_elasticity(curve)
    if elasticity_meta is None:
        return {
            "segment": label,
            "avg_price": round(float(curve["avg_price"].iloc[0]), 2),
            "total_seats": int(curve["seats_sold"].sum()),
            "n_price_points": int(len(curve)),
            "elasticity": math.nan,
            "r_squared": math.nan,
            "if_price_+10pct_qty_change": "N/A",
            "if_price_+10pct_rev_change": "N/A",
            "if_price_-10pct_qty_change": "N/A",
            "if_price_-10pct_rev_change": "N/A",
            "notes": f"Insufficient price variance. {notes}".strip(),
        }

    elasticity = elasticity_meta["elasticity"]
    r_sq = elasticity_meta["r_squared"]
    n_points = elasticity_meta["n_price_points"]

    delta_q_up, delta_rev_up = simulate_price_shift(elasticity, 0.10)
    delta_q_down, delta_rev_down = simulate_price_shift(elasticity, -0.10)

    return {
        "segment": label,
        "avg_price": round(float(curve["avg_price"].iloc[0]), 2),
        "total_seats": int(curve["seats_sold"].sum()),
        "n_price_points": n_points,
        "elasticity": round(elasticity, 3),
        "r_squared": round(r_sq, 3),
        "if_price_+10pct_qty_change": f"{round(delta_q_up * 100, 1)}%",
        "if_price_+10pct_rev_change": f"{round(delta_rev_up * 100, 1)}%",
        "if_price_-10pct_qty_change": f"{round(delta_q_down * 100, 1)}%",
        "if_price_-10pct_rev_change": f"{round(delta_rev_down * 100, 1)}%",
        "notes": notes,
    }


def build_subscriber_demand(df_sub: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Build demand curve at subscriber level (unique accounts per price)."""
    if df_sub.empty:
        return None
    # Get each subscriber's average price paid
    sub_prices = df_sub.groupby("acct_id").agg(
        avg_price=("purchase_price", "mean"),
        total_seats=("num_seats", "sum"),
    ).reset_index()
    # Round prices to nearest $5 for cleaner buckets
    sub_prices["price_bucket"] = (sub_prices["avg_price"] / 5).round() * 5
    # Count subscribers at each price bucket
    agg = sub_prices.groupby("price_bucket").agg(
        subscribers=("acct_id", "count"),
        total_seats=("total_seats", "sum"),
    ).reset_index()
    agg = agg.sort_values("price_bucket", ascending=False)
    agg["cumulative_subscribers"] = agg["subscribers"].cumsum()
    agg["cumulative_quantity"] = agg["cumulative_subscribers"]  # for plotting compatibility
    agg["purchase_price"] = agg["price_bucket"]
    agg["seats_sold"] = agg["subscribers"]
    # Add avg_price for summary compatibility
    total_subs = agg["subscribers"].sum()
    agg["avg_price"] = (sub_prices["avg_price"] * 1).mean()  # simple average across subscribers
    return agg


def main() -> None:
    plt.style.use("seaborn-v0_8-darkgrid")
    df = pd.read_csv(DATA_PATH)
    df["num_seats"] = df["num_seats"].fillna(1)
    df = df[df["purchase_price"] > 0].copy()
    df["seat_group"] = df["section_name"].map(SECTION_GROUP_MAP).fillna("Other Seating")
    df["is_premium_seat"] = df["section_name"].isin(PREMIUM_SECTIONS | {"LOGEL", "LOGER"})
    df["subscription_bucket"] = df.apply(classify_subscription_bucket, axis=1)
    df["event_type"] = df["Type"]

    summary_rows: list[Dict[str, object]] = []
    warnings: list[str] = []

    # =========================================================================
    # 1. SINGLE TICKET DEMAND CURVES (these are valid as-is)
    # =========================================================================
    single_ticket_curves: Dict[str, pd.DataFrame] = {}

    # Overall single ticket
    st_all = df[df["subscription_bucket"] == "Single Ticket"]
    curve = build_inverse_demand(st_all)
    if curve is not None:
        save_curve(curve, "demand_single_ticket_all")
        plot_inverse_demand(
            curve,
            "Single Ticket Demand (All Events)",
            "demand_single_ticket_all",
            subtitle=f"Total seats: {st_all['num_seats'].sum():,.0f} | Avg price: ${st_all['purchase_price'].mean():.2f}"
        )
        single_ticket_curves["Single Ticket (All)"] = curve
        summary_rows.append(summarize_segment("Single Ticket (All)", curve, "All single ticket purchases."))

    # Single ticket by event type
    for event_type in ["Classical", "Special", "Holiday"]:
        subset = df[(df["subscription_bucket"] == "Single Ticket") & (df["event_type"] == event_type)]
        if len(subset) < 100:
            continue
        curve = build_inverse_demand(subset)
        if curve is not None:
            slug = f"demand_single_ticket_{event_type.lower()}"
            save_curve(curve, slug)
            plot_inverse_demand(curve, f"Single Ticket Demand: {event_type} Events", slug)
            single_ticket_curves[f"Single Ticket - {event_type}"] = curve
            summary_rows.append(summarize_segment(f"Single Ticket - {event_type}", curve, f"Single tickets for {event_type} events."))

    # Single ticket by section
    for section in ["Premium Orchestra", "Front Loge", "Dress Circle", "Balcony"]:
        subset = df[(df["subscription_bucket"] == "Single Ticket") & (df["seat_group"] == section)]
        if len(subset) < 100:
            continue
        curve = build_inverse_demand(subset)
        if curve is not None:
            slug = f"demand_single_ticket_{section.lower().replace(' ', '_')}"
            save_curve(curve, slug)
            plot_inverse_demand(curve, f"Single Ticket Demand: {section}", slug)
            summary_rows.append(summarize_segment(f"Single Ticket - {section}", curve, f"Single tickets in {section} section."))

    # Multi-curve: Single ticket by event type
    plot_multi_curve(
        {k: v for k, v in single_ticket_curves.items() if "Single Ticket -" in k},
        "Single Ticket Demand by Event Type",
        "demand_single_ticket_by_event_type",
    )

    # =========================================================================
    # 2. SUBSCRIPTION DEMAND CURVES (subscriber-level, corrected)
    # =========================================================================
    subscriber_curves: Dict[str, pd.DataFrame] = {}

    # Fixed subscription by section (subscriber-level)
    for section in ["Premium Orchestra", "Front Loge", "Dress Circle", "Balcony"]:
        subset = df[
            (df["subscription_bucket"] == "Fixed Subscription") &
            (df["seat_group"] == section)
        ]
        if len(subset) < 100:
            continue
        curve = build_subscriber_demand(subset)
        if curve is not None and len(curve) >= 3:
            label = f"Subscription - {section}"
            slug = f"demand_subscription_{section.lower().replace(' ', '_')}"
            save_curve(curve, slug)
            plot_inverse_demand(curve, f"Subscription Demand: {section}", slug)
            subscriber_curves[label] = curve
            summary_rows.append(summarize_segment(label, curve, f"Subscribers in {section} (subscriber-level)."))

    # CYO subscription by section (subscriber-level)
    for section in ["Premium Orchestra", "Front Loge", "Dress Circle", "Balcony"]:
        subset = df[
            (df["subscription_bucket"] == "CYO Subscription") &
            (df["seat_group"] == section)
        ]
        if len(subset) < 100:
            continue
        curve = build_subscriber_demand(subset)
        if curve is not None and len(curve) >= 3:
            label = f"CYO Subscription - {section}"
            slug = f"demand_cyo_subscription_{section.lower().replace(' ', '_')}"
            save_curve(curve, slug)
            plot_inverse_demand(curve, f"CYO Subscription Demand: {section}", slug)
            subscriber_curves[label] = curve
            summary_rows.append(summarize_segment(label, curve, f"CYO subscribers in {section} (subscriber-level)."))

    # Multi-curve: Subscription by section
    plot_multi_curve(
        {k: v for k, v in subscriber_curves.items() if "Subscription -" in k and "CYO" not in k},
        "Subscription Demand by Section",
        "demand_subscription_by_section",
    )

    # Multi-curve: CYO subscription by section
    cyo_curves = {k: v for k, v in subscriber_curves.items() if "CYO Subscription -" in k}
    if cyo_curves:
        plot_multi_curve(
            cyo_curves,
            "CYO Subscription Demand by Section",
            "demand_cyo_subscription_by_section",
        )

    # =========================================================================
    # 3. COMPARISON CURVES (normalized to percentages for comparability)
    # =========================================================================
    def normalize_curve(curve: pd.DataFrame) -> pd.DataFrame:
        """Normalize cumulative quantity to percentage (0-100%)."""
        curve = curve.copy()
        max_qty = curve["cumulative_quantity"].max()
        curve["cumulative_pct"] = (curve["cumulative_quantity"] / max_qty) * 100
        return curve

    comparison_curves: Dict[str, pd.DataFrame] = {}

    # Single ticket - Premium Orchestra
    st_prem = df[(df["subscription_bucket"] == "Single Ticket") & (df["seat_group"] == "Premium Orchestra")]
    curve = build_inverse_demand(st_prem)
    if curve is not None:
        comparison_curves["Single Ticket"] = normalize_curve(curve)

    # Fixed - Premium Orchestra (subscriber level)
    fixed_prem = df[(df["subscription_bucket"] == "Fixed Subscription") & (df["seat_group"] == "Premium Orchestra")]
    curve = build_subscriber_demand(fixed_prem)
    if curve is not None:
        comparison_curves["Subscription"] = normalize_curve(curve)

    # CYO - Premium Orchestra (subscriber level)
    cyo_prem = df[(df["subscription_bucket"] == "CYO Subscription") & (df["seat_group"] == "Premium Orchestra")]
    curve = build_subscriber_demand(cyo_prem)
    if curve is not None:
        comparison_curves["CYO"] = normalize_curve(curve)

    if comparison_curves:
        # Plot normalized comparison
        fig, ax = plt.subplots(figsize=(9, 6))
        colors = {"Single Ticket": "#7b2cbf", "Subscription": "#2a9d8f", "CYO": "#e9c46a"}
        for label, curve in comparison_curves.items():
            ax.step(
                curve["cumulative_pct"],
                curve["purchase_price"],
                where="post",
                linewidth=2.5,
                label=label,
                color=colors.get(label, "#666666"),
            )
        ax.set_xlabel("Cumulative % of Buyers")
        ax.set_ylabel("Price (USD)")
        ax.set_title("Demand Comparison: Premium Orchestra (Normalized)", fontsize=13, fontweight="bold")
        ax.legend(frameon=True)
        ax.grid(True, which="both", linestyle="--", alpha=0.35)
        ax.set_xlim(0, 100)
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "demand_comparison_premium_orchestra.png", dpi=200)
        plt.close(fig)

    # =========================================================================
    # 4. SAVE SUMMARY
    # =========================================================================
    summary_df = pd.DataFrame([row for row in summary_rows if row is not None])
    summary_df.sort_values("segment", inplace=True)
    summary_path = OUTPUT_DIR / "price_sensitivity_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    notes_path = OUTPUT_DIR / "generation_notes.txt"
    with open(notes_path, "w", encoding="utf-8") as handle:
        handle.write("Demand Curve Generation Notes\n")
        handle.write("=" * 50 + "\n\n")
        handle.write("METHODOLOGY:\n")
        handle.write("- Single Ticket curves: seat-level aggregation (standard demand curve)\n")
        handle.write("- Subscription curves: subscriber-level aggregation (# subscribers at each price)\n")
        handle.write("  This corrects for volume discounts in subscription tiers.\n\n")
        if warnings:
            handle.write("Warnings:\n")
            for note in warnings:
                handle.write(f"- {note}\n")


if __name__ == "__main__":
    main()

