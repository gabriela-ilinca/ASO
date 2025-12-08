# ASO Ticketing Analysis Project - Context

## Project Overview

This project analyzes Atlanta Symphony Orchestra (ASO) ticketing data to answer three strategic questions:

1. **How do we get single ticket buyers to return?** (Currently 80% attend once and never return)
2. **How do we attract new subscribers and retain them?** (50% of new subscribers renew vs 85% of 3+ year subscribers)
3. **How do we engage younger audiences?** (Average subscriber age is 63, single ticket buyer age is 49)

### Key Context
- ASO averages 88% hall occupancy (best among major orchestras)
- Budget: 51% contributed, 49% earned revenue
- Season: September-June
- Data scope: FY23 (Sept 2022-June 2023) and FY24 (Sept 2023-June 2024)
- ~68,000 paid ticket records across both seasons

---

## Data Files

### Source Data
| File | Description |
|------|-------------|
| `master_tickets.csv` | Core dataset - all tickets with demographics, pricing, and event info merged |
| `FY23 Regular Tickets.csv` | Raw FY23 ticket transactions |
| `FY24 Regular Tickets Demographics.csv` | FY24 tickets with patron demographics |
| `College Pass Concert Tickets.csv` | College student program tickets |
| `Price Codes Updated.xlsx` | Price code decoder (~200 codes) |
| `23 and 24 Season Events List.xlsx` | Event dates, types, series info |

### Output Data (demand_curve_findings/)
| File | Description |
|------|-------------|
| `price_sensitivity_summary.csv` | Elasticity estimates by segment |
| `inverse_demand_*.csv` | Demand curves by segment |
| `fixed_plus_*.csv` | Fixed Plus program analysis outputs |
| `classical_addon_*.csv` | Classical Add-On product analysis outputs |

---

## Key Findings

### 1. Pricing & Demand Analysis

**Ticket Pricing Summary:**
- Average purchase price: $55.26
- Single tickets average: $59.86 (higher than subscriptions)
- Subscription tickets average: $51.02
- Premium sections (Orchestra, Loge): $62-85 average
- Balcony: $32 average

**Price Elasticity Findings:**
- Most segments show **inelastic demand** (elasticity between -0.2 and -0.8)
- Single Ticket Special Events: elasticity of -0.18 (very inelastic - 10% price decrease = 1.8% quantity increase)
- Single Ticket buyers aged 55+: elasticity of -0.80 (moderately inelastic)
- Young balcony buyers (<35): more price-sensitive than other segments

**Implication:** Price increases can generally boost revenue without significant demand loss, especially for premium seats and special events.

---

### 2. Fixed Plus Premium Program Analysis

**Target:** Fixed 6 subscribers (1,643 accounts, 70% of all Fixed subscribers)

**Key Behavioral Insights:**
- 57.8% of Fixed 6 subscribers already purchase additional single tickets
- Average single ticket spend per buyer: $355 total (across ~2.5 events)
- 45% purchase tickets 2+ months in advance
- 83% of Fixed 6 seats are in premium sections

**Single Ticket Purchases by Event Type (Fixed 6 buyers):**
| Event Type | Unique Buyers | Total Seats | Revenue |
|------------|---------------|-------------|---------|
| Classical | 709 | 3,274 | $208,590 |
| Special | 381 | 951 | $82,806 |
| Holiday | 196 | 708 | $41,980 |

**Proposed Product:**
- Fixed Plus Bronze: +1 Holiday ticket at 10% premium ($62.61)
- Fixed Plus Gold: +2 tickets (Holiday + Special) at 10% premium ($150.53 total)

**Projected Revenue:**
- 354 Fixed Plus subscribers
- $40,741 in premium-priced revenue
- $3,704 pure premium captured

---

### 3. Classical Add-On Product Analysis

**Target:** Special/Holiday single ticket buyers (7,008 accounts, 30% of all single ticket accounts)

**Key Insight:** 80.6% of Special/Holiday single ticket buyers have NEVER purchased a Classical ticket - massive untapped opportunity.

**Discount Structure:**
- +1 Classical ticket: 5% off
- +2 Classical tickets: 10% off each
- +3 Classical tickets: 15% off each

**Gateway Classical Events (highest crossover appeal):**
| Event | Crossover Buyers | Revenue |
|-------|------------------|---------|
| Beethoven Symphony No 9 | 188 | $29,067 |
| Opening Weekend | 164 | $21,503 |
| Orff: Carmina Burana | 139 | $22,903 |
| Beethoven and Bolero | 119 | $22,351 |

**Projected Impact:**
- 1,324 responders (20% response rate assumption)
- 1,926 new Classical tickets sold
- $102,099 incremental revenue
- 50 projected new CYO subscribers (24.6% historical conversion rate from 3+ Classical buyers)

---

### 4. Subscription Tier Comparison

| Fixed Tier | Total Accounts | % Buying Single Tickets | Avg ST Events | Avg ST Revenue |
|------------|----------------|-------------------------|---------------|----------------|
| Fixed 6 | 1,643 | 57.8% | 2.5 | $355 |
| Fixed 12 | 199 | 70.9% | 2.6 | $427 |
| Fixed 18 | 62 | 69.4% | 2.9 | $428 |
| Fixed 24 | 137 | 70.8% | 2.6 | $346 |

**Insight:** Fixed 6 is the largest tier but has the lowest single-ticket purchasing rate - room for growth via Fixed Plus upsell.

---

## Analysis Scripts

| Script | Purpose |
|--------|---------|
| `demand_curve_refresh.py` | Generates inverse demand curves, elasticity estimates, and visualizations |
| `fixed_plus_analysis.py` | Analyzes Fixed 6 subscriber behavior for premium upsell product design |
| `classical_addon_analysis.py` | Analyzes Special/Holiday → Classical crossover opportunity |
| `special_event_simulations.py` | Simulates pricing scenarios for special events |
| `subscription_utilization.py` | Analyzes how well subscribers use their packages |

---

## Notebooks

| Notebook | Description |
|----------|-------------|
| `01_Data_Loading_and_Exploration.ipynb` | Initial data loading, cleaning, and exploratory analysis |
| `02_Revenue_and_Pricing_Analysis_final.ipynb` | Revenue breakdown, pricing patterns, buyer segment analysis |
| `03_Demand_Curve_Analysis.ipynb` | Demand curve methodology and initial elasticity estimates |
| `04_Demand_Curve_Findings.ipynb` | Final demand curve findings, scenario modeling, and recommendations |
| `05_Subscription_Utilization.ipynb` | Subscription package utilization rates |

---

## Key Metrics Reference

### Overall Statistics
- Total paid ticket records: 67,974
- Average tickets per transaction: 1.92 seats
- Median days before event for purchase: 62 days
- Single ticket records: 34,340
- Subscription records: 33,199

### Seat Sections (by average price)
| Section | Avg Price | Count |
|---------|-----------|-------|
| GA1 (Pit) | $100.89 | 46 |
| LOGER | $84.57 | 4,545 |
| LOGEL | $77.91 | 5,201 |
| ORCHL | $62.11 | 22,409 |
| ORCHR | $49.52 | 20,582 |
| BALCR | $32.14 | 5,138 |

### Subscription Types
- **Fixed Subscriptions:** Pre-set concert packages (6, 12, 18, or 24 concerts)
  - Tenure levels: Freshman (1st year), Sophomore (2nd year), Established (3+ years)
- **CYO (Create Your Own):** Flexible subscription with customer-selected concerts

---

## Strategic Recommendations Summary

### 1. Fixed Plus Program (Immediate Opportunity)
- Target Fixed 6 subscribers at renewal time
- Emphasize "advance access" and "guaranteed seating" benefits
- Start with email campaign to current single-ticket buyers within Fixed 6

### 2. Classical Add-On Product (Near-term)
- Offer same-day discounts to Special/Holiday attendees
- Use gateway events (Beethoven 9th, Carmina Burana) in marketing
- Track CYO conversion funnel from 3+ Classical buyers

### 3. Pricing Optimization (Ongoing)
- Premium Fixed peak-season seats: can support 5-7% increase
- Young balcony buyers: consider 5% discount to boost occupancy
- Special events for 55+: room for premium pricing

---

## Technical Notes

### Data Quality
- Age available for majority of patrons
- ~200 price codes simplified into buyer categories
- Event types: Classical, Holiday, Special
- Season periods: Opening, Mid-Season, Peak, Finale

### Running the Analysis
```bash
# Generate demand curves and elasticity estimates
python demand_curve_refresh.py

# Run Fixed Plus analysis
python fixed_plus_analysis.py

# Run Classical Add-On analysis
python classical_addon_analysis.py
```

### Key Columns in master_tickets.csv
- `acct_id`: Unique patron identifier
- `purchase_price`: Per-ticket price
- `paid_amount`: Total transaction amount
- `num_seats`: Tickets in transaction
- `ticket_type`: Single Ticket or Subscription
- `price_code_type`: Detailed price code description
- `Type`: Event type (Classical, Holiday, Special)
- `section_name`: Seating section
- `days_before_event`: Purchase lead time
- `age`: Patron age
- `season_period`: Opening, Mid-Season, Peak, Finale

---

*Last updated: December 2024*
*Data scope: FY23 + FY24 combined*
