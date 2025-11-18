#!/usr/bin/env python3
"""
Generate inverse demand curves, charts, and price sensitivity simulations
for ASO ticketing data. Outputs are saved into demand_curve_findings/.
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
    """Aggregate seats sold at each price and compute cumulative quantities."""
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
    agg["avg_price"] = (
        df["purchase_price"] * df["num_seats"]
    ).sum() / total_qty
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
) -> Path:
    """Plot a single inverse demand curve."""
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
        s=12,
        alpha=0.9,
    )
    ax.set_xlabel("Cumulative Seats (Quantity)")
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
    x_field: str = "cumulative_share",
) -> Optional[Path]:
    """Plot multiple inverse demand curves in a single figure."""
    if not curves:
        return None
    fig, ax = plt.subplots(figsize=(8.5, 6))
    palette = plt.cm.viridis(np.linspace(0.1, 0.9, len(curves)))
    for idx, (label, curve) in enumerate(curves.items()):
        if curve is None or curve.empty:
            continue
        ax.step(
            curve[x_field],
            curve["purchase_price"],
            where="post",
            linewidth=2.0,
            label=label,
            color=palette[idx],
        )
    ax.set_xlabel(
        "Cumulative Share of Seats" if x_field == "cumulative_share" else "Cumulative Seats"
    )
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
    """
    Fit a log-log model to approximate price elasticity.
    Returns None when not enough unique price points exist.
    """
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
    return {"elasticity": elasticity, "r_squared": r_sq}


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
    """Build a summary row for price sensitivity."""
    if curve is None or curve.empty:
        return None

    elasticity_meta = estimate_price_elasticity(curve)
    if elasticity_meta is None:
        return {
            "segment": label,
            "price_weighted_avg": round(float(curve["avg_price"].iloc[0]), 2),
            "observations": int(len(curve)),
            "elasticity": math.nan,
            "r_squared": math.nan,
            "delta_q_+10pct": math.nan,
            "delta_rev_+10pct": math.nan,
            "delta_q_-10pct": math.nan,
            "delta_rev_-10pct": math.nan,
            "notes": f"Insufficient variance. {notes}".strip(),
        }

    elasticity = elasticity_meta["elasticity"]
    delta_q_up, delta_rev_up = simulate_price_shift(elasticity, 0.10)
    delta_q_down, delta_rev_down = simulate_price_shift(elasticity, -0.10)

    return {
        "segment": label,
        "price_weighted_avg": round(float(curve["avg_price"].iloc[0]), 2),
        "observations": int(len(curve)),
        "elasticity": round(elasticity, 3),
        "r_squared": round(elasticity_meta["r_squared"], 3),
        "delta_q_+10pct": round(delta_q_up, 3),
        "delta_rev_+10pct": round(delta_rev_up, 3),
        "delta_q_-10pct": round(delta_q_down, 3),
        "delta_rev_-10pct": round(delta_rev_down, 3),
        "notes": notes,
    }


def main() -> None:
    plt.style.use("seaborn-v0_8-darkgrid")
    df = pd.read_csv(DATA_PATH)
    df["num_seats"] = df["num_seats"].fillna(1)
    df = df[df["purchase_price"] > 0].copy()
    df["seat_group"] = df["section_name"].map(SECTION_GROUP_MAP).fillna("Other Seating")
    df["is_premium_seat"] = df["section_name"].isin(PREMIUM_SECTIONS | {"LOGEL", "LOGER"})
    df["premium_bucket"] = np.where(
        df["is_premium_seat"], "Premium Orchestra + Front Loge", "Standard / Other Seats"
    )
    df["subscription_bucket"] = df.apply(classify_subscription_bucket, axis=1)
    df["fixed_detail"] = df["price_code_type"].apply(classify_fixed_detail)
    df["event_type"] = df["Type"]

    generated_curves: Dict[str, pd.DataFrame] = {}
    summary_rows: list[Dict[str, object]] = []
    warnings: list[str] = []

    # Fixed subscription detail curves
    fixed_details = [
        "Fixed - Established",
        "Fixed - Freshman",
        "Fixed - Sophomore",
        "Fixed - Lapsed",
        "Fixed - Upgrade",
        "Fixed - Musician",
        "Fixed - Chorus",
        "Fixed - Other",
    ]

    for detail in fixed_details:
        subset = df[df["fixed_detail"] == detail]
        curve = build_inverse_demand(subset)
        if curve is None:
            warnings.append(f"No sufficient data for {detail}.")
            continue
        slug = f"inverse_demand_{detail.lower().replace(' ', '_').replace('-', '').replace('/', '')}"
        save_curve(curve, slug)
        plot_inverse_demand(curve, f"{detail} Inverse Demand", slug)
        generated_curves[detail] = curve
        summary_rows.append(
            summarize_segment(
                f"{detail} (All seats)",
                curve,
                "Fixed subscription detail.",
            )
        )

    # Aggregated buckets
    bucket_filters = {
        "Fixed Subscription (All)": df["subscription_bucket"] == "Fixed Subscription",
        "CYO Subscription": df["subscription_bucket"] == "CYO Subscription",
        "Single Ticket (All)": df["subscription_bucket"] == "Single Ticket",
        "Single Ticket - Special Events": (
            (df["subscription_bucket"] == "Single Ticket") & (df["event_type"] == "Special")
        ),
    }

    for label, mask in bucket_filters.items():
        subset = df[mask]
        curve = build_inverse_demand(subset)
        if curve is None:
            warnings.append(f"No sufficient data for {label}.")
            continue
        slug = f"inverse_demand_{label.lower().replace(' ', '_').replace('-', '_')}"
        save_curve(curve, slug)
        title = f"{label} Inverse Demand Curve"
        subtitle = (
            f"Total seats: {subset['num_seats'].sum():,.0f} | "
            f"Avg price: ${subset['purchase_price'].mean():.2f}"
        )
        plot_inverse_demand(curve, title, slug, subtitle=subtitle)
        generated_curves[label] = curve
        summary_rows.append(
            summarize_segment(
                f"{label} (All seats)",
                curve,
                "Bucket-level view.",
            )
        )

    # Premium seat focus
    premium_focus = {
        "Premium Fixed (All)": df["is_premium_seat"] & (df["subscription_bucket"] == "Fixed Subscription"),
        "Premium Fixed - Sophomore": df["is_premium_seat"] & (df["fixed_detail"] == "Fixed - Sophomore"),
        "Premium CYO": df["is_premium_seat"] & (df["subscription_bucket"] == "CYO Subscription"),
        "Premium Single Ticket - Special": df["is_premium_seat"]
        & (df["subscription_bucket"] == "Single Ticket")
        & (df["event_type"] == "Special"),
    }
    premium_curves: Dict[str, pd.DataFrame] = {}
    for label, mask in premium_focus.items():
        subset = df[mask]
        curve = build_inverse_demand(subset)
        if curve is None:
            warnings.append(f"Premium view skipped for {label} (not enough data).")
            continue
        slug = f"inverse_demand_{label.lower().replace(' ', '_').replace('-', '_')}"
        save_curve(curve, slug)
        plot_inverse_demand(curve, f"{label} Inverse Demand", slug)
        premium_curves[label] = curve
        summary_rows.append(
            summarize_segment(
                f"{label}",
                curve,
                "Premium seat focus.",
            )
        )

    # Multi-curve visualizations
    plot_multi_curve(
        {
            key: generated_curves[key]
            for key in ["Fixed Subscription (All)", "CYO Subscription", "Single Ticket (All)"]
            if key in generated_curves
        },
        "Inverse Demand by Subscription Bucket",
        "inverse_demand_subscription_bucket_overlay",
    )

    plot_multi_curve(
        premium_curves,
        "Premium Seats: Fixed vs Sophomore vs CYO vs Single Ticket (Special)",
        "inverse_demand_premium_focus",
    )

    # Seat group sensitivity
    seat_group_curves: Dict[str, pd.DataFrame] = {}
    for group, group_df in df.groupby("seat_group"):
        curve = build_inverse_demand(group_df)
        if curve is None or curve["purchase_price"].nunique() < 3:
            warnings.append(f"Seat group '{group}' lacks enough distinct price points.")
            continue
        slug = f"inverse_demand_seatgroup_{group.lower().replace(' ', '_').replace('/', '').replace('-', '')}"
        save_curve(curve, slug)
        plot_inverse_demand(curve, f"{group} Inverse Demand", slug)
        seat_group_curves[group] = curve
        summary_rows.append(
            summarize_segment(
                f"{group} (All buyers)",
                curve,
                "Seat-specific sensitivity.",
            )
        )

    plot_multi_curve(
        {
            key: seat_group_curves[key]
            for key in ["Premium Orchestra", "Front Loge", "Dress Circle", "Balcony", "Pit / GA"]
            if key in seat_group_curves
        },
        "Inverse Demand by Seat Group",
        "inverse_demand_by_seat_group",
    )

    # Price sensitivity summary
    summary_df = pd.DataFrame([row for row in summary_rows if row is not None])
    summary_df.sort_values("segment", inplace=True)
    summary_path = OUTPUT_DIR / "price_sensitivity_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    notes_path = OUTPUT_DIR / "generation_notes.txt"
    with open(notes_path, "w", encoding="utf-8") as handle:
        if warnings:
            handle.write("Warnings / Notes:\n")
            for note in warnings:
                handle.write(f"- {note}\n")
        else:
            handle.write("All segments processed without warnings.\n")


if __name__ == "__main__":
    main()

