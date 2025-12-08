#!/usr/bin/env python3
"""
Fixed Plus Premium Program Analysis

Analyzes Fixed 6 subscriber behavior to design a premium "Fixed Plus" bundle
that offers advance access to Holiday and Special events at a 10% premium.
"""

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "master_tickets.csv"
OUTPUT_DIR = BASE_DIR / "demand_curve_findings"


def load_and_prepare_data():
    """Load and prepare the master tickets data."""
    df = pd.read_csv(DATA_PATH)
    df["num_seats"] = df["num_seats"].fillna(1)
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["add_datetime"] = pd.to_datetime(df["add_datetime"], errors="coerce")
    df = df[df["purchase_price"] > 0].copy()
    return df


def identify_fixed_subscribers(df):
    """Identify Fixed subscription accounts, focusing on Fixed 6."""
    # Identify Fixed subscription records
    fixed_mask = df["price_code_type"].str.lower().str.contains("fixed", na=False)
    fixed_records = df[fixed_mask].copy()

    # Categorize by subscription size
    def get_fixed_tier(label):
        if not isinstance(label, str):
            return "Unknown"
        label_lower = label.lower()
        if "6 concert" in label_lower:
            return "Fixed 6"
        elif "12 concert" in label_lower:
            return "Fixed 12"
        elif "18 concert" in label_lower:
            return "Fixed 18"
        elif "24 concert" in label_lower:
            return "Fixed 24"
        else:
            return "Fixed Other"

    fixed_records["fixed_tier"] = fixed_records["price_code_type"].apply(get_fixed_tier)

    return fixed_records


def analyze_fixed_subscriber_single_ticket_behavior(df, fixed_records):
    """
    Analyze how many Fixed subscribers also purchase single tickets
    and what types of events they attend.
    """
    # Get unique Fixed subscriber accounts
    fixed_accounts = fixed_records["acct_id"].unique()

    # Get all single ticket purchases
    single_tickets = df[df["ticket_type"] == "Single Ticket"].copy()

    # Find single ticket purchases by Fixed subscribers
    fixed_single_tickets = single_tickets[single_tickets["acct_id"].isin(fixed_accounts)]

    # Summary by Fixed tier
    fixed_tiers = fixed_records.groupby(["acct_id", "fixed_tier"]).size().reset_index()
    fixed_tiers = fixed_tiers.drop(columns=[0])
    fixed_tiers = fixed_tiers.drop_duplicates()

    # Merge with single ticket behavior
    single_ticket_summary = fixed_single_tickets.groupby("acct_id").agg({
        "event_name": "nunique",
        "num_seats": "sum",
        "paid_amount": "sum",
        "Type": lambda x: list(x.unique())
    }).reset_index()
    single_ticket_summary.columns = [
        "acct_id", "st_events", "st_seats", "st_revenue", "st_event_types"
    ]

    # Merge
    fixed_with_st = fixed_tiers.merge(single_ticket_summary, on="acct_id", how="left")
    fixed_with_st["st_events"] = fixed_with_st["st_events"].fillna(0).astype(int)
    fixed_with_st["st_seats"] = fixed_with_st["st_seats"].fillna(0).astype(int)
    fixed_with_st["st_revenue"] = fixed_with_st["st_revenue"].fillna(0)
    fixed_with_st["bought_single_tickets"] = fixed_with_st["st_events"] > 0

    return fixed_with_st


def analyze_fixed6_detailed(df, fixed_records, fixed_with_st):
    """Deep dive into Fixed 6 subscribers."""
    # Filter to Fixed 6
    fixed6_accounts = fixed_with_st[fixed_with_st["fixed_tier"] == "Fixed 6"]["acct_id"].unique()
    fixed6_with_st = fixed_with_st[fixed_with_st["fixed_tier"] == "Fixed 6"]

    # Basic stats
    total_fixed6 = len(fixed6_accounts)
    fixed6_with_single = fixed6_with_st[fixed6_with_st["bought_single_tickets"]]["acct_id"].nunique()
    pct_buying_single = fixed6_with_single / total_fixed6 * 100 if total_fixed6 > 0 else 0

    # Average single tickets among those who buy
    buyers_only = fixed6_with_st[fixed6_with_st["bought_single_tickets"]]
    avg_st_events = buyers_only["st_events"].mean() if len(buyers_only) > 0 else 0
    avg_st_seats = buyers_only["st_seats"].mean() if len(buyers_only) > 0 else 0
    avg_st_revenue = buyers_only["st_revenue"].mean() if len(buyers_only) > 0 else 0

    # What event types do they buy single tickets for?
    single_tickets = df[df["ticket_type"] == "Single Ticket"]
    fixed6_st = single_tickets[single_tickets["acct_id"].isin(fixed6_accounts)]

    event_type_breakdown = fixed6_st.groupby("Type").agg({
        "acct_id": "nunique",
        "num_seats": "sum",
        "paid_amount": "sum"
    }).reset_index()
    event_type_breakdown.columns = ["Event Type", "Unique Buyers", "Total Seats", "Total Revenue"]

    return {
        "total_fixed6_accounts": total_fixed6,
        "fixed6_buying_single_tickets": fixed6_with_single,
        "pct_buying_single_tickets": pct_buying_single,
        "avg_st_events_per_buyer": avg_st_events,
        "avg_st_seats_per_buyer": avg_st_seats,
        "avg_st_revenue_per_buyer": avg_st_revenue,
        "event_type_breakdown": event_type_breakdown,
        "fixed6_st_data": fixed6_st
    }


def analyze_fixed_tier_comparison(fixed_with_st):
    """Compare single ticket behavior across Fixed tiers."""
    comparison = fixed_with_st.groupby("fixed_tier").agg({
        "acct_id": "count",
        "bought_single_tickets": "sum",
        "st_events": "mean",
        "st_seats": "mean",
        "st_revenue": "mean"
    }).reset_index()

    comparison.columns = [
        "Fixed Tier", "Total Accounts", "Accounts Buying ST",
        "Avg ST Events", "Avg ST Seats", "Avg ST Revenue"
    ]

    comparison["% Buying ST"] = (
        comparison["Accounts Buying ST"] / comparison["Total Accounts"] * 100
    ).round(1)

    # Reorder columns
    comparison = comparison[[
        "Fixed Tier", "Total Accounts", "Accounts Buying ST", "% Buying ST",
        "Avg ST Events", "Avg ST Seats", "Avg ST Revenue"
    ]]

    return comparison


def analyze_holiday_special_demand(df, fixed6_accounts):
    """
    Analyze Fixed 6 subscriber demand for Holiday and Special events.
    """
    # Get all Holiday and Special purchases by Fixed 6 accounts
    hs_events = df[
        (df["acct_id"].isin(fixed6_accounts)) &
        (df["Type"].isin(["Holiday", "Special"]))
    ]

    # By ticket type (subscription vs single ticket)
    by_ticket_type = hs_events.groupby(["Type", "ticket_type"]).agg({
        "acct_id": "nunique",
        "num_seats": "sum",
        "paid_amount": "sum",
        "purchase_price": "mean"
    }).reset_index()

    return by_ticket_type


def analyze_purchase_timing(df, fixed6_accounts):
    """
    Analyze when Fixed 6 subscribers buy their single tickets.
    This helps understand if "advance access" is a valuable benefit.
    """
    single_tickets = df[
        (df["ticket_type"] == "Single Ticket") &
        (df["acct_id"].isin(fixed6_accounts))
    ]

    # Distribution of days before event
    timing_stats = single_tickets["days_before_event"].describe()

    # What % buy within different windows
    total_st = len(single_tickets)
    if total_st == 0:
        return None, None

    timing_buckets = {
        "Same week (0-7 days)": (single_tickets["days_before_event"] <= 7).sum() / total_st * 100,
        "2-4 weeks (8-28 days)": ((single_tickets["days_before_event"] > 7) &
                                   (single_tickets["days_before_event"] <= 28)).sum() / total_st * 100,
        "1-2 months (29-60 days)": ((single_tickets["days_before_event"] > 28) &
                                     (single_tickets["days_before_event"] <= 60)).sum() / total_st * 100,
        "2+ months (61+ days)": (single_tickets["days_before_event"] > 60).sum() / total_st * 100,
    }

    return timing_stats, timing_buckets


def analyze_seat_preferences(df, fixed6_accounts):
    """
    Analyze seat section preferences for Fixed 6 subscribers.
    Do they prefer premium seats? This informs "premium seating" benefit.
    """
    # Subscription seats
    sub_seats = df[
        (df["acct_id"].isin(fixed6_accounts)) &
        (df["ticket_type"] == "Subscription")
    ]

    # Single ticket seats
    st_seats = df[
        (df["acct_id"].isin(fixed6_accounts)) &
        (df["ticket_type"] == "Single Ticket")
    ]

    # Compare section distribution
    sub_sections = sub_seats.groupby("section_name")["num_seats"].sum()
    st_sections = st_seats.groupby("section_name")["num_seats"].sum()

    # Premium sections
    premium = {"ORCHL", "ORCHR", "LOGEL", "LOGER"}

    sub_premium_pct = sub_sections[sub_sections.index.isin(premium)].sum() / sub_sections.sum() * 100 if sub_sections.sum() > 0 else 0
    st_premium_pct = st_sections[st_sections.index.isin(premium)].sum() / st_sections.sum() * 100 if st_sections.sum() > 0 else 0

    return {
        "subscription_premium_pct": sub_premium_pct,
        "single_ticket_premium_pct": st_premium_pct,
        "sub_sections": sub_sections,
        "st_sections": st_sections
    }


def calculate_fixed_plus_projections(fixed6_stats, df, fixed6_accounts):
    """
    Project revenue from Fixed Plus program.

    Fixed Plus includes:
    - Bronze: +1 Special ticket
    - Gold: +2 tickets (Holiday + Special)
    - 10% premium on the additional tickets
    """
    # Get average prices for Holiday and Special events
    holiday_prices = df[df["Type"] == "Holiday"]["purchase_price"]
    special_prices = df[df["Type"] == "Special"]["purchase_price"]

    avg_holiday_price = holiday_prices.mean()
    avg_special_price = special_prices.mean()

    # Fixed Plus pricing (10% premium)
    premium_rate = 0.10
    holiday_plus_price = avg_holiday_price * (1 + premium_rate)
    special_plus_price = avg_special_price * (1 + premium_rate)

    # Target: Fixed 6 subscribers who already buy single tickets
    # These are proven "upgraders" - most likely to want Fixed Plus
    current_st_buyers = fixed6_stats["fixed6_buying_single_tickets"]

    # Also target: Fixed 6 subscribers who DON'T buy single tickets
    # but might with the right incentive/convenience
    non_st_buyers = fixed6_stats["total_fixed6_accounts"] - current_st_buyers

    # Uptake assumptions
    # Current ST buyers: 30% uptake (they already show behavior)
    # Non-ST buyers: 10% uptake (need more convincing)
    st_buyer_uptake = 0.30
    non_st_buyer_uptake = 0.10

    projected_st_buyer_converts = int(current_st_buyers * st_buyer_uptake)
    projected_non_st_converts = int(non_st_buyers * non_st_buyer_uptake)
    total_converts = projected_st_buyer_converts + projected_non_st_converts

    # Revenue calculation
    # Option 1 (Bronze): +1 Special (assume 40% choose this)
    # Option 2 (Gold): +2 Holiday/Special (assume 60% choose this)
    opt1_pct = 0.40
    opt2_pct = 0.60

    opt1_converts = int(total_converts * opt1_pct)
    opt2_converts = int(total_converts * opt2_pct)

    # Revenue from Option 1 (Bronze): 1 Special ticket at premium
    opt1_revenue = opt1_converts * 1 * special_plus_price

    # Revenue from Option 2 (Gold): 2 tickets (1 Holiday + 1 Special)
    opt2_revenue = opt2_converts * (holiday_plus_price + special_plus_price)

    total_premium_revenue = opt1_revenue + opt2_revenue

    # Calculate what they would have paid at regular price (for comparison)
    opt1_regular = opt1_converts * 1 * avg_special_price
    opt2_regular = opt2_converts * (avg_holiday_price + avg_special_price)
    total_regular_equiv = opt1_regular + opt2_regular

    # Premium captured
    premium_captured = total_premium_revenue - total_regular_equiv

    return {
        "avg_holiday_price": avg_holiday_price,
        "avg_special_price": avg_special_price,
        "holiday_plus_price": holiday_plus_price,
        "special_plus_price": special_plus_price,
        "current_st_buyers": current_st_buyers,
        "non_st_buyers": non_st_buyers,
        "projected_st_buyer_converts": projected_st_buyer_converts,
        "projected_non_st_converts": projected_non_st_converts,
        "total_converts": total_converts,
        "opt1_converts": opt1_converts,
        "opt2_converts": opt2_converts,
        "opt1_revenue": opt1_revenue,
        "opt2_revenue": opt2_revenue,
        "total_premium_revenue": total_premium_revenue,
        "total_regular_equiv": total_regular_equiv,
        "premium_captured": premium_captured
    }


def main():
    print("=" * 80)
    print("FIXED PLUS PREMIUM PROGRAM ANALYSIS")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    df = load_and_prepare_data()
    print(f"Total records: {len(df):,}")
    print()

    # Identify Fixed subscribers
    print("Identifying Fixed subscribers...")
    fixed_records = identify_fixed_subscribers(df)
    print(f"Fixed subscription records: {len(fixed_records):,}")
    print(f"Unique Fixed subscriber accounts: {fixed_records['acct_id'].nunique():,}")
    print()

    # Analyze single ticket behavior
    print("Analyzing Fixed subscriber single ticket behavior...")
    fixed_with_st = analyze_fixed_subscriber_single_ticket_behavior(df, fixed_records)
    print()

    # Compare across tiers
    print("=" * 80)
    print("FIXED TIER COMPARISON: Single Ticket Purchasing Behavior")
    print("=" * 80)
    tier_comparison = analyze_fixed_tier_comparison(fixed_with_st)
    print(tier_comparison.to_string(index=False))
    print()

    # Deep dive on Fixed 6
    print("=" * 80)
    print("FIXED 6 DEEP DIVE")
    print("=" * 80)
    fixed6_accounts = fixed_with_st[fixed_with_st["fixed_tier"] == "Fixed 6"]["acct_id"].unique()
    fixed6_stats = analyze_fixed6_detailed(df, fixed_records, fixed_with_st)

    print(f"Total Fixed 6 accounts: {fixed6_stats['total_fixed6_accounts']:,}")
    print(f"Fixed 6 buying single tickets: {fixed6_stats['fixed6_buying_single_tickets']:,} ({fixed6_stats['pct_buying_single_tickets']:.1f}%)")
    print()
    print("Among those who buy single tickets:")
    print(f"  Avg # of events: {fixed6_stats['avg_st_events_per_buyer']:.1f}")
    print(f"  Avg # of seats: {fixed6_stats['avg_st_seats_per_buyer']:.1f}")
    print(f"  Avg revenue: ${fixed6_stats['avg_st_revenue_per_buyer']:.2f}")
    print()

    print("Event types purchased (single tickets by Fixed 6):")
    print(fixed6_stats["event_type_breakdown"].to_string(index=False))
    print()

    # Holiday/Special demand analysis
    print("=" * 80)
    print("HOLIDAY & SPECIAL EVENT DEMAND (Fixed 6 Subscribers)")
    print("=" * 80)
    hs_demand = analyze_holiday_special_demand(df, fixed6_accounts)
    print(hs_demand.to_string(index=False))
    print()

    # Purchase timing analysis
    print("=" * 80)
    print("PURCHASE TIMING ANALYSIS (Fixed 6 Single Ticket Purchases)")
    print("=" * 80)
    timing_stats, timing_buckets = analyze_purchase_timing(df, fixed6_accounts)
    if timing_buckets:
        print("When do Fixed 6 subscribers buy single tickets?")
        for bucket, pct in timing_buckets.items():
            print(f"  {bucket}: {pct:.1f}%")
        print()
        print(f"Median days before event: {timing_stats['50%']:.0f}")
        print(f"Mean days before event: {timing_stats['mean']:.0f}")
    print()

    # Seat preference analysis
    print("=" * 80)
    print("SEAT PREFERENCE ANALYSIS")
    print("=" * 80)
    seat_prefs = analyze_seat_preferences(df, fixed6_accounts)
    print(f"Premium seat % (Subscription): {seat_prefs['subscription_premium_pct']:.1f}%")
    print(f"Premium seat % (Single Tickets): {seat_prefs['single_ticket_premium_pct']:.1f}%")
    print()

    # Fixed Plus projections
    print("=" * 80)
    print("FIXED PLUS PROGRAM PROJECTIONS")
    print("=" * 80)
    projections = calculate_fixed_plus_projections(fixed6_stats, df, fixed6_accounts)

    print(f"Average Holiday ticket price: ${projections['avg_holiday_price']:.2f}")
    print(f"Average Special ticket price: ${projections['avg_special_price']:.2f}")
    print()
    print("Fixed Plus pricing (10% premium):")
    print(f"  Holiday Plus: ${projections['holiday_plus_price']:.2f}")
    print(f"  Special Plus: ${projections['special_plus_price']:.2f}")
    print()
    print("Target segments:")
    print(f"  Current ST buyers (30% uptake): {projections['current_st_buyers']:,} -> {projections['projected_st_buyer_converts']:,} converts")
    print(f"  Non-ST buyers (10% uptake): {projections['non_st_buyers']:,} -> {projections['projected_non_st_converts']:,} converts")
    print(f"  Total projected converts: {projections['total_converts']:,}")
    print()
    print("Package selection:")
    print(f"  Bronze (+1 Special): {projections['opt1_converts']:,} subscribers")
    print(f"  Gold (+2 Holiday/Special): {projections['opt2_converts']:,} subscribers")
    print()
    print("Revenue projections:")
    print(f"  Bronze revenue: ${projections['opt1_revenue']:,.2f}")
    print(f"  Gold revenue: ${projections['opt2_revenue']:,.2f}")
    print(f"  TOTAL PREMIUM REVENUE: ${projections['total_premium_revenue']:,.2f}")
    print(f"  Regular price equivalent: ${projections['total_regular_equiv']:,.2f}")
    print(f"  Premium captured (10%): ${projections['premium_captured']:,.2f}")
    print()

    # Save results
    results = {
        "tier_comparison": tier_comparison,
        "fixed6_stats": fixed6_stats,
        "timing_buckets": timing_buckets,
        "seat_prefs": seat_prefs,
        "projections": projections,
        "hs_demand": hs_demand
    }

    tier_comparison.to_csv(OUTPUT_DIR / "fixed_plus_tier_comparison.csv", index=False)
    fixed6_stats["event_type_breakdown"].to_csv(OUTPUT_DIR / "fixed_plus_event_breakdown.csv", index=False)

    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

    return results


if __name__ == "__main__":
    results = main()
