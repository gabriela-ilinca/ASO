#!/usr/bin/env python3
"""
Classical Add-On Product Analysis

Analyzes the potential impact of offering discounted Classical concert tickets
to single ticket buyers who attend Special/Holiday events.

Discount structure (cumulative):
- +1 Classical ticket: 5% off
- +2 Classical tickets: 10% off each
- +3 Classical tickets: 15% off each

Offer validity: 60 days from attending Special/Holiday event
"""

from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "master_tickets.csv"
OUTPUT_DIR = BASE_DIR / "demand_curve_findings"

def load_and_prepare_data():
    """Load and prepare the master tickets data."""
    df = pd.read_csv(DATA_PATH)
    df["num_seats"] = df["num_seats"].fillna(1)
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["add_datetime"] = pd.to_datetime(df["add_datetime"], errors="coerce")

    # Filter to paid tickets only
    df = df[df["purchase_price"] > 0].copy()

    return df


def identify_single_ticket_buyers(df):
    """Identify single ticket buyers and their event type attendance."""
    # Filter to single ticket purchases only
    single_tickets = df[df["ticket_type"] == "Single Ticket"].copy()

    return single_tickets


def segment_by_event_attendance(single_tickets):
    """
    Segment single ticket buyers by their attendance patterns.

    Returns a dictionary with account-level summaries.
    """
    # Get unique accounts and their event type attendance
    account_events = single_tickets.groupby("acct_id").agg({
        "Type": lambda x: list(x.unique()),
        "event_name": "nunique",
        "num_seats": "sum",
        "paid_amount": "sum",
        "purchase_price": "mean"
    }).reset_index()

    # Determine which event types each account attended
    account_events["attended_special"] = account_events["Type"].apply(
        lambda x: "Special" in x if isinstance(x, list) else False
    )
    account_events["attended_holiday"] = account_events["Type"].apply(
        lambda x: "Holiday" in x if isinstance(x, list) else False
    )
    account_events["attended_classical"] = account_events["Type"].apply(
        lambda x: "Classical" in x if isinstance(x, list) else False
    )
    account_events["attended_special_or_holiday"] = (
        account_events["attended_special"] | account_events["attended_holiday"]
    )

    return account_events


def count_classical_purchases_by_account(single_tickets):
    """Count how many Classical tickets each account purchased."""
    classical_only = single_tickets[single_tickets["Type"] == "Classical"]

    classical_counts = classical_only.groupby("acct_id").agg({
        "event_name": "nunique",  # Number of unique Classical events
        "num_seats": "sum",       # Total Classical seats
        "paid_amount": "sum",     # Total Classical revenue
        "purchase_price": "mean"  # Average price paid
    }).reset_index()

    classical_counts.columns = [
        "acct_id", "classical_events", "classical_seats",
        "classical_revenue", "classical_avg_price"
    ]

    return classical_counts


def create_target_segments(single_tickets):
    """
    Create segments of Special/Holiday single ticket buyers based on
    their Classical purchasing behavior.
    """
    # Get account-level event attendance
    account_events = segment_by_event_attendance(single_tickets)

    # Get Classical purchase counts per account
    classical_counts = count_classical_purchases_by_account(single_tickets)

    # Merge the data
    account_summary = account_events.merge(
        classical_counts, on="acct_id", how="left"
    )

    # Fill NaN for accounts with no Classical purchases
    account_summary["classical_events"] = account_summary["classical_events"].fillna(0).astype(int)
    account_summary["classical_seats"] = account_summary["classical_seats"].fillna(0).astype(int)
    account_summary["classical_revenue"] = account_summary["classical_revenue"].fillna(0)

    # Filter to only Special/Holiday attendees
    target_accounts = account_summary[
        account_summary["attended_special_or_holiday"]
    ].copy()

    # Create segments based on Classical purchase count
    def assign_segment(row):
        n = row["classical_events"]
        if n == 0:
            return "Group A: 0 Classical"
        elif n == 1:
            return "Group B: 1 Classical"
        elif n == 2:
            return "Group C: 2 Classical"
        else:
            return "Group D: 3+ Classical"

    target_accounts["segment"] = target_accounts.apply(assign_segment, axis=1)

    return target_accounts


def get_special_holiday_details(single_tickets, target_accounts):
    """Get details about Special/Holiday attendance for target accounts."""
    special_holiday = single_tickets[
        single_tickets["Type"].isin(["Special", "Holiday"])
    ]

    sh_summary = special_holiday.groupby("acct_id").agg({
        "Type": lambda x: list(x),
        "event_name": list,
        "num_seats": "sum",
        "paid_amount": "sum",
        "purchase_price": "mean"
    }).reset_index()

    sh_summary.columns = [
        "acct_id", "sh_event_types", "sh_events",
        "sh_seats", "sh_revenue", "sh_avg_price"
    ]

    return target_accounts.merge(sh_summary, on="acct_id", how="left")


def estimate_classical_elasticity(single_tickets):
    """
    Estimate price elasticity for Classical single ticket demand.
    """
    classical = single_tickets[single_tickets["Type"] == "Classical"]

    # Aggregate by price point
    demand = classical.groupby("purchase_price").agg({
        "num_seats": "sum",
        "acct_id": "count"
    }).reset_index()
    demand.columns = ["price", "seats_sold", "transactions"]

    # Filter valid data points
    valid = demand[(demand["price"] > 0) & (demand["seats_sold"] > 0)]

    if valid.shape[0] < 3:
        return None, None

    # Log-log regression for elasticity
    X = np.log(valid["price"]).values.reshape(-1, 1)
    y = np.log(valid["seats_sold"]).values

    model = LinearRegression()
    model.fit(X, y)

    elasticity = float(model.coef_[0])
    r_squared = float(model.score(X, y))

    return elasticity, r_squared


def calculate_uptake_projections(elasticity, target_accounts, response_rate=0.20):
    """
    Project uptake based on elasticity and discount levels.

    Discount structure:
    - +1: 5% off
    - +2: 10% off each
    - +3: 15% off each

    response_rate: % of target accounts who will engage with the offer
    """
    discounts = {
        "+1": 0.05,
        "+2": 0.10,
        "+3": 0.15
    }

    # Calculate expected quantity multiplier for each discount level
    # Using elasticity: %ΔQ = elasticity × %ΔP
    quantity_multipliers = {}
    for level, discount in discounts.items():
        # Price decreases, so quantity should increase (for negative elasticity)
        # %ΔQ = elasticity × (-discount)
        pct_qty_change = elasticity * (-discount)
        quantity_multipliers[level] = 1 + pct_qty_change

    return quantity_multipliers, discounts, response_rate


def analyze_cyo_conversion_potential(df, target_accounts):
    """
    Analyze historical conversion from single ticket to CYO subscription.

    Look at accounts that bought 3+ Classical single tickets and later
    became CYO subscribers.
    """
    # Get all CYO subscription records
    cyo_records = df[
        df["price_code_type"].str.lower().str.contains("cyo", na=False)
    ]["acct_id"].unique()

    # Check which of our target accounts (3+ Classical) became CYO
    group_d = target_accounts[target_accounts["segment"] == "Group D: 3+ Classical"]

    if len(group_d) == 0:
        return 0, 0, 0

    converted_to_cyo = group_d["acct_id"].isin(cyo_records).sum()
    conversion_rate = converted_to_cyo / len(group_d)

    return len(group_d), converted_to_cyo, conversion_rate


def generate_before_after_tables(target_accounts, single_tickets, elasticity,
                                  quantity_multipliers, discounts, response_rate):
    """Generate before/after analysis tables."""

    # BEFORE: Current state
    before_summary = target_accounts.groupby("segment").agg({
        "acct_id": "count",
        "classical_events": "sum",
        "classical_seats": "sum",
        "classical_revenue": "sum",
        "classical_avg_price": "mean"
    }).reset_index()

    before_summary.columns = [
        "Segment", "Accounts", "Total Classical Events",
        "Total Classical Seats", "Total Classical Revenue", "Avg Price Paid"
    ]

    # Get average Classical single ticket price for discount calculations
    classical_st = single_tickets[single_tickets["Type"] == "Classical"]
    avg_classical_price = classical_st["purchase_price"].mean()

    # AFTER: Projected state
    # Group A (0 Classical) - potential new buyers
    group_a = target_accounts[target_accounts["segment"] == "Group A: 0 Classical"]
    group_a_count = len(group_a)

    # Group B (1 Classical) - potential upsell to +2 or +3
    group_b = target_accounts[target_accounts["segment"] == "Group B: 1 Classical"]
    group_b_count = len(group_b)

    # Group C (2 Classical) - potential upsell to +3
    group_c = target_accounts[target_accounts["segment"] == "Group C: 2 Classical"]
    group_c_count = len(group_c)

    # Project uptake for Group A (0 -> +1, +2, or +3)
    # Assume distribution: 60% buy +1, 30% buy +2, 10% buy +3
    group_a_responders = int(group_a_count * response_rate)
    group_a_plus1 = int(group_a_responders * 0.60)
    group_a_plus2 = int(group_a_responders * 0.30)
    group_a_plus3 = int(group_a_responders * 0.10)

    # Project uptake for Group B (1 -> +1 more, or +2 more)
    group_b_responders = int(group_b_count * response_rate)
    group_b_plus1 = int(group_b_responders * 0.70)  # Buy 1 more (total 2)
    group_b_plus2 = int(group_b_responders * 0.30)  # Buy 2 more (total 3)

    # Project uptake for Group C (2 -> +1 more)
    group_c_responders = int(group_c_count * response_rate)
    group_c_plus1 = group_c_responders  # Buy 1 more (total 3)

    # Calculate incremental tickets and revenue
    # Group A new tickets
    group_a_new_tickets = (group_a_plus1 * 1) + (group_a_plus2 * 2) + (group_a_plus3 * 3)
    group_a_revenue = (
        group_a_plus1 * 1 * avg_classical_price * (1 - discounts["+1"]) +
        group_a_plus2 * 2 * avg_classical_price * (1 - discounts["+2"]) +
        group_a_plus3 * 3 * avg_classical_price * (1 - discounts["+3"])
    )
    group_a_full_price_revenue = (
        group_a_plus1 * 1 * avg_classical_price +
        group_a_plus2 * 2 * avg_classical_price +
        group_a_plus3 * 3 * avg_classical_price
    )

    # Group B new tickets (they already have 1, buying more)
    group_b_new_tickets = (group_b_plus1 * 1) + (group_b_plus2 * 2)
    # For Group B buying +1 more, they get +2 tier discount (since total = 2)
    # For Group B buying +2 more, they get +3 tier discount (since total = 3)
    group_b_revenue = (
        group_b_plus1 * 1 * avg_classical_price * (1 - discounts["+2"]) +
        group_b_plus2 * 2 * avg_classical_price * (1 - discounts["+3"])
    )
    group_b_full_price_revenue = (
        group_b_plus1 * 1 * avg_classical_price +
        group_b_plus2 * 2 * avg_classical_price
    )

    # Group C new tickets (they have 2, buying 1 more for total of 3)
    group_c_new_tickets = group_c_plus1 * 1
    group_c_revenue = group_c_plus1 * 1 * avg_classical_price * (1 - discounts["+3"])
    group_c_full_price_revenue = group_c_plus1 * 1 * avg_classical_price

    # Total projections
    total_new_tickets = group_a_new_tickets + group_b_new_tickets + group_c_new_tickets
    total_discounted_revenue = group_a_revenue + group_b_revenue + group_c_revenue
    total_full_price_revenue = group_a_full_price_revenue + group_b_full_price_revenue + group_c_full_price_revenue
    discount_cost = total_full_price_revenue - total_discounted_revenue

    after_projections = {
        "Group A (0 Classical)": {
            "target_accounts": group_a_count,
            "responders": group_a_responders,
            "buy_1": group_a_plus1,
            "buy_2": group_a_plus2,
            "buy_3": group_a_plus3,
            "new_tickets": group_a_new_tickets,
            "discounted_revenue": group_a_revenue,
            "full_price_revenue": group_a_full_price_revenue,
        },
        "Group B (1 Classical)": {
            "target_accounts": group_b_count,
            "responders": group_b_responders,
            "buy_1_more": group_b_plus1,
            "buy_2_more": group_b_plus2,
            "new_tickets": group_b_new_tickets,
            "discounted_revenue": group_b_revenue,
            "full_price_revenue": group_b_full_price_revenue,
        },
        "Group C (2 Classical)": {
            "target_accounts": group_c_count,
            "responders": group_c_responders,
            "buy_1_more": group_c_plus1,
            "new_tickets": group_c_new_tickets,
            "discounted_revenue": group_c_revenue,
            "full_price_revenue": group_c_full_price_revenue,
        },
        "Totals": {
            "total_new_tickets": total_new_tickets,
            "total_discounted_revenue": total_discounted_revenue,
            "total_full_price_revenue": total_full_price_revenue,
            "discount_cost": discount_cost,
        }
    }

    return before_summary, after_projections, avg_classical_price


def find_popular_classical_events(single_tickets, target_accounts):
    """
    Find which Classical events are most popular among Special/Holiday
    single ticket buyers who also attended Classical events.
    """
    # Get accounts that attended both Special/Holiday AND Classical
    crossover_accounts = target_accounts[
        target_accounts["classical_events"] > 0
    ]["acct_id"]

    # Get their Classical event attendance
    classical_by_crossover = single_tickets[
        (single_tickets["acct_id"].isin(crossover_accounts)) &
        (single_tickets["Type"] == "Classical")
    ]

    # Count by event name
    popular_events = classical_by_crossover.groupby("Name").agg({
        "acct_id": "nunique",
        "num_seats": "sum",
        "paid_amount": "sum"
    }).reset_index()

    popular_events.columns = ["Event Name", "Unique Buyers", "Total Seats", "Total Revenue"]
    popular_events = popular_events.sort_values("Unique Buyers", ascending=False)

    return popular_events.head(10)


def main():
    print("=" * 80)
    print("CLASSICAL ADD-ON PRODUCT ANALYSIS")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    df = load_and_prepare_data()
    single_tickets = identify_single_ticket_buyers(df)
    print(f"Total single ticket records: {len(single_tickets):,}")
    print(f"Unique single ticket accounts: {single_tickets['acct_id'].nunique():,}")
    print()

    # Create target segments
    print("Creating target segments...")
    target_accounts = create_target_segments(single_tickets)
    target_accounts = get_special_holiday_details(single_tickets, target_accounts)
    print(f"Special/Holiday single ticket buyers: {len(target_accounts):,}")
    print()

    # Segment distribution
    print("Segment Distribution:")
    print("-" * 40)
    segment_counts = target_accounts["segment"].value_counts().sort_index()
    for segment, count in segment_counts.items():
        pct = count / len(target_accounts) * 100
        print(f"  {segment}: {count:,} accounts ({pct:.1f}%)")
    print()

    # Estimate elasticity
    print("Estimating Classical single ticket price elasticity...")
    elasticity, r_squared = estimate_classical_elasticity(single_tickets)
    print(f"  Elasticity: {elasticity:.3f}")
    print(f"  R-squared: {r_squared:.3f}")
    print()

    # Calculate uptake projections
    print("Calculating uptake projections...")
    response_rate = 0.20  # 20% response rate assumption
    quantity_multipliers, discounts, response_rate = calculate_uptake_projections(
        elasticity, target_accounts, response_rate
    )
    print(f"  Assumed response rate: {response_rate:.0%}")
    print(f"  Discount levels: +1={discounts['+1']:.0%}, +2={discounts['+2']:.0%}, +3={discounts['+3']:.0%}")
    print()

    # Generate before/after tables
    print("Generating before/after analysis...")
    before_summary, after_projections, avg_classical_price = generate_before_after_tables(
        target_accounts, single_tickets, elasticity,
        quantity_multipliers, discounts, response_rate
    )
    print(f"  Average Classical single ticket price: ${avg_classical_price:.2f}")
    print()

    # CYO conversion analysis
    print("Analyzing CYO conversion potential...")
    group_d_count, converted, conversion_rate = analyze_cyo_conversion_potential(
        df, target_accounts
    )
    print(f"  Group D accounts (3+ Classical): {group_d_count:,}")
    print(f"  Already converted to CYO: {converted:,}")
    print(f"  Historical conversion rate: {conversion_rate:.1%}")
    print()

    # Find popular Classical events for marketing
    print("Finding popular 'gateway' Classical events...")
    popular_events = find_popular_classical_events(single_tickets, target_accounts)
    print()

    # Save results
    results = {
        "target_accounts": target_accounts,
        "before_summary": before_summary,
        "after_projections": after_projections,
        "elasticity": elasticity,
        "r_squared": r_squared,
        "avg_classical_price": avg_classical_price,
        "response_rate": response_rate,
        "discounts": discounts,
        "cyo_conversion": {
            "group_d_count": group_d_count,
            "converted": converted,
            "conversion_rate": conversion_rate
        },
        "popular_events": popular_events
    }

    # Export CSV summaries
    before_summary.to_csv(OUTPUT_DIR / "classical_addon_before_state.csv", index=False)
    popular_events.to_csv(OUTPUT_DIR / "classical_addon_gateway_events.csv", index=False)

    # Create detailed after projections dataframe
    after_df = pd.DataFrame([
        {
            "Group": "Group A (0 Classical)",
            "Target Accounts": after_projections["Group A (0 Classical)"]["target_accounts"],
            "Expected Responders": after_projections["Group A (0 Classical)"]["responders"],
            "New Tickets": after_projections["Group A (0 Classical)"]["new_tickets"],
            "Discounted Revenue": after_projections["Group A (0 Classical)"]["discounted_revenue"],
            "Full Price Equivalent": after_projections["Group A (0 Classical)"]["full_price_revenue"],
        },
        {
            "Group": "Group B (1 Classical)",
            "Target Accounts": after_projections["Group B (1 Classical)"]["target_accounts"],
            "Expected Responders": after_projections["Group B (1 Classical)"]["responders"],
            "New Tickets": after_projections["Group B (1 Classical)"]["new_tickets"],
            "Discounted Revenue": after_projections["Group B (1 Classical)"]["discounted_revenue"],
            "Full Price Equivalent": after_projections["Group B (1 Classical)"]["full_price_revenue"],
        },
        {
            "Group": "Group C (2 Classical)",
            "Target Accounts": after_projections["Group C (2 Classical)"]["target_accounts"],
            "Expected Responders": after_projections["Group C (2 Classical)"]["responders"],
            "New Tickets": after_projections["Group C (2 Classical)"]["new_tickets"],
            "Discounted Revenue": after_projections["Group C (2 Classical)"]["discounted_revenue"],
            "Full Price Equivalent": after_projections["Group C (2 Classical)"]["full_price_revenue"],
        },
        {
            "Group": "TOTAL",
            "Target Accounts": (
                after_projections["Group A (0 Classical)"]["target_accounts"] +
                after_projections["Group B (1 Classical)"]["target_accounts"] +
                after_projections["Group C (2 Classical)"]["target_accounts"]
            ),
            "Expected Responders": (
                after_projections["Group A (0 Classical)"]["responders"] +
                after_projections["Group B (1 Classical)"]["responders"] +
                after_projections["Group C (2 Classical)"]["responders"]
            ),
            "New Tickets": after_projections["Totals"]["total_new_tickets"],
            "Discounted Revenue": after_projections["Totals"]["total_discounted_revenue"],
            "Full Price Equivalent": after_projections["Totals"]["total_full_price_revenue"],
        }
    ])
    after_df.to_csv(OUTPUT_DIR / "classical_addon_after_projections.csv", index=False)

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("BEFORE STATE:")
    print(before_summary.to_string(index=False))
    print()
    print("AFTER STATE (Projected):")
    print(after_df.to_string(index=False))
    print()
    print(f"Incremental Revenue: ${after_projections['Totals']['total_discounted_revenue']:,.2f}")
    print(f"Discount Cost: ${after_projections['Totals']['discount_cost']:,.2f}")
    print()
    print("TOP GATEWAY CLASSICAL EVENTS:")
    print(popular_events.head(5).to_string(index=False))
    print()
    print(f"CYO CONVERSION POTENTIAL:")
    # Project new 3+ Classical buyers who might convert
    new_3plus_buyers = (
        after_projections["Group A (0 Classical)"]["buy_3"] +
        after_projections["Group B (1 Classical)"]["buy_2_more"] +
        after_projections["Group C (2 Classical)"]["buy_1_more"]
    )
    projected_cyo_conversions = int(new_3plus_buyers * conversion_rate)
    print(f"  New accounts reaching 3+ Classical: {new_3plus_buyers}")
    print(f"  Projected CYO conversions (at {conversion_rate:.1%} rate): {projected_cyo_conversions}")
    print()

    return results


if __name__ == "__main__":
    results = main()
