# Atlanta Symphony Orchestra Ticketing Analysis Project

## 📊 PROJECT OVERVIEW

### The Three Strategic Questions:

1. **How do we get single ticket buyers to return?** (Currently 80% attend once and never return)
2. **How do we attract new subscribers and retain them?** (50% of new subscribers renew vs 85% of 3+ year subscribers)
3. **How do we engage younger audiences?** (Average subscriber age is 63, single ticket buyer age is 49)

### Context:

- ASO averages 88% hall occupancy (best among major orchestras)
- Budget is 51% contributed, 49% earned
- Season runs September-June (FY23 = Sept 2022-June 2023)
- We have 2 years of ticket data (FY23 and FY24)
- ~200 price codes need to be simplified for analysis

---

## 🗂️ DATA FILES AVAILABLE

**Raw Data:**

- FY23 Regular Tickets.csv
- FY24 Regular Tickets.csv
- FY23 Regular Tickets Demographics.csv
- FY24 Regular Tickets Demographics.csv
- College Pass Concert Tickets.csv
- College Pass Demographics.csv
- Price Codes Updated.xlsx (price decoder)
- 23 and 24 Season Events List.xlsx (event dates and types)
- ASO Classical Seating Chart.xlsx
- ASO Holiday and Specials Seating Chart.xlsx
- 23 and 24 Expenses.xlsx

**Clean Data (will be created in Phase 0):**

- master_tickets.csv (all tickets with demographics and event info merged)
- patron_summary.csv (one row per patron with aggregated metrics)
- event_summary.csv (one row per event with attendance/revenue metrics)
- data_dictionary.txt (explains all columns)

---

## 🔧 PHASE 0: DATA PREPARATION

### **Assigned to: Gaby**

**Status:** Must be completed BEFORE team can start their work packages

### Your Tasks:

#### Task 0.1: Run Data Merging Pipeline

Use the Cursor prompt provided to complete Steps 3-5:

1. **Merge demographics** to master_tickets on acct_id
2. **Merge price decoder** on price_code
   - Create simplified buyer_category from "Price Code Type Description"
   - Create price_tier based on paid_amount
   - Extract subscription_size
3. **Merge event information** on event_name
   - Add event dates, types, series info
   - Calculate days_before_event
   - Add season_period categories
4. **Create patron_summary.csv** with patron-level metrics
5. **Create event_summary.csv** with event-level metrics
6. **Create data_dictionary.txt** explaining all fields
7. **Generate data_prep_report.txt** with quality checks

#### Task 0.2: Data Quality Validation

Before sharing with team, verify:

- [ ] No critical missing data (age available for >70% of patrons)
- [ ] Price codes successfully categorized
- [ ] Event dates merged correctly
- [ ] Patron summary totals match master_tickets totals
- [ ] All derived fields calculated correctly

## 📦 WORK PACKAGE 1: POPULARITY & DEMAND ANALYSIS

### **Assigned to:**

**Difficulty:** ⭐⭐ Moderate
**Skills Needed:** Basic Python/Excel, data aggregation
**Primary Files:** event_summary.csv, master_tickets.csv

### Your Mission:

Understand what drives ticket demand - which concerts are popular, when do people buy, what patterns exist?

### Detailed Tasks:

#### 1.1: Event Popularity Rankings (2-3 hours)

Create summary tables showing:

**A. Overall Rankings:**

- Top 20 events by total_tickets_sold
- Top 20 events by unique_patrons
- Top 20 events by total_revenue
- Compare FY23 vs FY24: which events grew? Which declined?

**B. Popularity by Buyer Type:**
Filter master_tickets for each buyer category and find:

- Top 10 events for Single Ticket buyers (hint: group by event_name, count tickets where buyer_category = "Single Ticket")
- Top 10 events for Subscribers (all subscriber categories combined)
- Top 10 events for 6-concert subscribers specifically
- Top 10 events for 12-concert subscribers
- Top 10 events for College Pass users

**C. Event Type Comparison:**
Group by event_type (from event_summary):

- Average attendance by type: Delta Series vs Holiday vs Special
- Which type has highest % of single ticket buyers?
- Which type has highest subscriber attendance?

#### 1.2: Temporal Patterns (2-3 hours)

Analyze when tickets sell best:

**A. Monthly Trends:**

- Aggregate event_summary by month_name
- Calculate: total tickets sold per month, average tickets per event in that month
- Create line chart showing monthly patterns across FY23 and FY24
- Identify: Which months are peak season? (March-May as expected?)

**B. Season Period Analysis:**

- Group by season_period (Opening, Mid-Season, Peak, Finale)
- Average attendance per period
- Do Opening and Finale concerts outperform as expected?

**C. Weekend Effects:**

- Using weekend column from event_summary
- Compare attendance: weekend vs weekday concerts

#### 1.3: Purchase Timing Behavior (2 hours)

Understand WHEN people buy tickets:

**A. Lead Time Analysis:**
Using master_tickets.csv:

- Calculate average days_before_event overall
- Break down by buyer_category (do subscribers plan further ahead?)
- Break down by event_type (do Holiday concerts sell closer to date?)

**B. Last-Minute vs Early Bird:**

- % of tickets purchased within 7 days of event (last-minute)
- % purchased 30+ days before (early bird)
- Compare by buyer category and event type

**C. Best-Selling Events Timing:**

- For the top 10 attended events, when did they sell out?
- Plot: Days before event vs tickets sold (cumulative)

#### 1.4: Special Program Analysis (1-2 hours)

If you can identify Delta Series events (from series column or event_type):

**A. Delta Series Performance:**

- Average attendance vs other program types
- Single ticket participation rate (what % of audience is single ticket buyers?)
- Subscriber participation rate

**B. Holiday/Special Events:**

- Do these attract different audiences?
- Higher % of single ticket buyers?
- Younger average age?

### Your Deliverables:

1. **Excel workbook: "WP1_Popularity_Analysis.xlsx"** with tabs:

   - Event_Rankings
   - Monthly_Trends
   - Purchase_Timing
   - Event_Type_Comparison
2. **Visualizations folder** with:

   - Top 20 events bar chart
   - Monthly trend line chart (FY23 vs FY24)
   - Purchase timing distributions
   - Season period comparison
3. **Summary document: "WP1_Key_Findings.pdf"** (2-3 pages):

   - What are our most popular concerts?
   - When do people buy tickets?
   - Are there clear seasonal patterns?
   - Do different buyer types attend different events?
   - 3-5 actionable insights

### Success Criteria:

- [ ] All top 20 rankings created with correct numbers
- [ ] Temporal patterns clearly visualized
- [ ] Findings are specific (not vague statements like "events are popular")
- [ ] Clear comparison between buyer types
- [ ] Insights directly answer: What drives demand?

---

## 💰 WORK PACKAGE 2: REVENUE & PRICING ANALYSIS

### **Assigned to: Jiwon**

**Difficulty:** ⭐⭐⭐ Moderate-Hard

Your Mission:

Follow the money - understand what generates revenue and whether our pricing strategy is working.

### Detailed Tasks:

#### 2.1: Revenue Generators by Event (2-3 hours)

Identify our financial winners:

**A. Revenue Rankings:**

- Top 20 events by total_revenue
- Compare to Top 20 by attendance (are they the same?)
- Calculate revenue_per_seat for each event
- Which events have highest price realization?

**B. Event Type Revenue:**

- Total revenue by event_type (Delta Series, Holiday, Special)
- Average revenue per event by type
- Which type is most profitable per event?

**C. Revenue Concentration:**

- What % of total revenue comes from top 10 events?
- What % comes from top 20%?
- Is revenue concentrated or distributed?

#### 2.2: Revenue by Time Period (2 hours)

Understand seasonality of revenue:

**A. Monthly Revenue:**

- Group event_summary by month
- Total revenue per month (FY23 vs FY24)
- Does revenue follow attendance patterns?

**B. Season Period Revenue:**

- Revenue by season_period (Opening, Peak, Finale)
- Average revenue per event in each period

**C. Year-over-Year Growth:**

- Compare FY23 vs FY24 total revenue
- Which months showed biggest growth?
- Overall revenue growth rate

#### 2.3: Revenue by Customer Segment (3-4 hours)

**This is your most important analysis!**

**A. Buyer Category Revenue:**
Using master_tickets.csv (exclude comps: comp=FALSE):

- Total revenue from Single Ticket buyers
- Total revenue from each Subscriber tier (Freshman, Sophomore, Established)
- Total revenue from College Pass
- Create pie chart of revenue contribution

**B. Patron Lifetime Value:**
Using patron_summary.csv:

- Average total_spend by primary_buyer_category
- Average spend for returners vs one-time buyers
- Average spend by subscriber tenure

**C. Revenue per Patron:**

- Single ticket buyers: avg spend per person
- Subscribers: avg spend per person
- Compare: Do subscribers spend more over 2 years despite discounts?

#### 2.4: Pricing Effectiveness (3-4 hours)

**Critical for understanding if discounts are working:**

**A. Discount Analysis:**
For each event in master_tickets:

- Identify "full price" tickets (highest paid_amount for that event, excluding outliers)
- Calculate % sold at full price vs discounted
- Calculate revenue from full-price vs discounted

**B. Subscriber Discount ROI:**

- Average ticket price: Subscribers vs Single Ticket buyers
- Discount % (difference from full price)
- But: Do subscribers attend more events? Calculate total spend.
- Compare:
  - Single buyer: $85 × 1 event = $85
  - Subscriber: $65 × 4 events = $260
  - Conclusion: Subscribers generate more total revenue!

**C. Price Code Effectiveness:**
Using master_tickets with Price Code Type Description:

- How many unique price codes exist?
- Revenue by price code (top 20)
- Identify price codes with <1% of total tickets sold
- Which codes generated <$5,000 total? (potentially obsolete)

**D. Revenue by Section/Price Tier:**

- Revenue from Premium vs Mid-tier vs Value sections
- Which sections generate most revenue per seat?
- Is Premium pricing working?

#### 2.5: Price Code Simplification Recommendations (2 hours)

**Goal: Can we reduce from ~200 codes to ~50?**

**Analysis:**

1. Group price codes by function:

   - How many codes are for single tickets? (could be consolidated)
   - How many for subscriptions? (by size: 6, 12, 18, 24)
   - How many are section-specific?
2. Identify redundancy:

   - Codes with <100 tickets sold across 2 years
   - Codes with nearly identical pricing
   - Codes that can be merged
3. Propose simplified structure:

   - Buyer Type (4 categories) × Section Tier (4 tiers) × Special Promotions (3-4) = ~50-60 codes
   - Document which current codes would map to new simplified codes

#### 2.6: Demand Curves (2-3 hours)

**This is advanced - if you're comfortable with scatter plots:**

Create three demand curve visualizations:

**A. Overall Demand Curve:**

- X-axis: paid_amount (price)
- Y-axis: num_seats (quantity sold at that price)
- Use master_tickets data, group by price point
- Add trendline

**B. By Event Type:**

- Separate curves for: Delta Series, Holiday, Special
- Do different event types have different price sensitivity?

**C. By Buyer Type:**

- Separate curves for: Single Ticket vs Subscribers
- Are subscribers less price-sensitive?

### Your Deliverables:

1. **Excel workbook: "WP2_Revenue_Analysis.xlsx"** with tabs:

   - Event_Revenue_Rankings
   - Monthly_Revenue
   - Revenue_by_Buyer_Category
   - Pricing_Effectiveness
   - Price_Code_Analysis
   - Simplification_Recommendations
2. **Visualizations folder** with:

   - Revenue contribution pie chart (by buyer category)
   - Top 20 revenue-generating events
   - Demand curves (3 charts)
   - Price code usage analysis
3. **Report: "WP2_Pricing_Strategy_Report.pdf"** (3-4 pages):

   - What generates the most revenue?
   - Are subscriber discounts paying off? (YES/NO with evidence)
   - Price code simplification recommendations
   - Pricing effectiveness by section
   - 5-7 actionable insights about pricing strategy

### Success Criteria:

- [ ] Revenue calculations verified (totals match data_prep_report)
- [ ] Clear answer: Are discounts working?
- [ ] Specific price code recommendations (which to keep, which to eliminate)
- [ ] Demand curves created with clear insights
- [ ] Financial analysis is rigorous and detailed

---

## 👥 WORK PACKAGE 3: DEMOGRAPHICS & ATTENDEE CHARACTERISTICS

### **Assigned to:**

**Difficulty:** ⭐ Easy-Moderate

Your Mission:

Understand WHO attends ASO concerts - their demographics, behaviors, and preferences.

### Detailed Tasks:

#### 3.1: Demographic Distributions (2 hours)

Create comprehensive demographic profiles:

**A. Overall Demographics:**
Using patron_summary.csv, calculate for ALL patrons:

- **Age:** mean, median, min, max, standard deviation
- **Age histogram:** Show distribution (bins: <25, 25-34, 35-49, 50-64, 65+)
- **Gender:** % breakdown (if available)
- **Geography:** Top 10 zip codes by patron count
- **Education:** Distribution (if available)
- **Marital Status:** Distribution (if available)

**B. Demographics by Buyer Type:**
Separate profiles for:

- Single Ticket buyers
- Subscribers (all)
- College Pass users

For each group, show:

- Average age
- Age distribution
- Gender breakdown
- Geographic concentration

#### 3.2: Single Ticket Buyer Behavior (2-3 hours)

**Focus only on patrons where primary_buyer_category = "Single Ticket"**

**A. Purchase Patterns:**

- How many tickets do they typically buy per transaction? (distribution of num_seats)
- Do they come alone or in groups?
  - % who always buy 1 ticket (alone)
  - % who buy 2 tickets (couples)
  - % who buy 3-4 tickets (small groups)
  - % who buy 5+ tickets (large groups)

**B. Frequency:**
Using patron_summary:

- % who attended only 1 event (across both FY23 and FY24)
- % who attended 2 events
- % who attended 3-4 events
- % who attended 5+ events
- Average events attended per single ticket buyer

**C. Seat/Section Preferences:**
Using master_tickets filtered for single ticket buyers:

- Top 5 sections by ticket count
- Most common price_tier
- Do they prefer Premium, Mid-tier, or Value seats?

**D. Program Preferences:**

- Top 10 events attended by single ticket buyers
- Do they prefer Holiday/Special events over Delta Series?
- Compare to overall event popularity (from WP1)

**E. Return Behavior:**
From patron_summary:

- How many single ticket buyers are returners (is_returner = TRUE)?
- Of those who returned, average time between visits
- What did returners see on their first visit vs second visit?

#### 3.3: Subscriber Behavior (2-3 hours)

**Filter to has_subscription = TRUE**

**A. Package Utilization:**
For each subscription size (6, 12, 18, 24):

- Average # of unique events actually attended
- Utilization rate (attended / allowed)
- Example: 6-concert subscribers attend avg 4.5 events = 75% utilization

**B. Group Attendance:**

- Do subscribers bring guests?
- Average num_seats per transaction for subscribers
- Compare to single ticket buyers

**C. Seat Consistency:**

- Do subscribers sit in the same section repeatedly?
- Calculate: For each subscriber, what % of their tickets are in their preferred_section?

**D. Cross-Buying Behavior:**
**Important question:** Do subscribers ALSO buy single tickets?

- Filter subscribers who have BOTH subscription tickets AND single tickets
- How many do this?
- For Delta Series events: What % of audience are subscribers buying single tickets (not using their package)?

**E. Preferred Programs:**

- Which events do subscribers attend most?
- Do they prefer certain series or composers?

#### 3.4: Seat Occupancy & Timing (2 hours)

**Understand how venues fill up:**

**A. Section Popularity:**
Using master_tickets, for all events combined:

- Rank sections by total tickets sold
- Which sections fill fastest? (earliest avg add_datetime)
- Which sections have lowest occupancy?

**B. By Event Type:**

- Do Holiday concerts fill different sections than Classical?
- Premium seat usage: Holiday vs Delta Series

**C. Purchase Timing by Section:**

- Premium seats: average days_before_event
- Value seats: average days_before_event
- Do premium buyers plan further ahead?

**D. Heat Map (if time permits):**
Create visualization showing:

- Rows: Different sections
- Columns: Buyer types
- Color: Ticket count
- This shows which buyer types prefer which sections

#### 3.5: Demographic Comparison Table (1 hour)

Create a comprehensive comparison table:

| Metric                   | Single Ticket | Subscriber | College Pass | Overall |
| ------------------------ | ------------- | ---------- | ------------ | ------- |
| Count of patrons         |               |            |              |         |
| Average age              |               |            |              |         |
| % Female                 |               |            |              |         |
| Avg tickets purchased    |               |            |              |         |
| Avg total spend          |               |            |              |         |
| % Returners              |               |            |              |         |
| Avg events attended      |               |            |              |         |
| Most common section      |               |            |              |         |
| Avg days before purchase |               |            |              |         |

This table should tell the complete story of each audience segment.

### Your Deliverables:

1. **Excel workbook: "WP3_Demographics_Analysis.xlsx"** with tabs:

   - Overall_Demographics
   - Single_Ticket_Behavior
   - Subscriber_Behavior
   - Seat_Occupancy
   - Demographic_Comparison_Table
2. **Visualizations folder** with:

   - Age distribution histograms (overall + by buyer type)
   - Top 10 zip codes bar chart
   - Group size distributions
   - Section popularity charts
   - Subscription utilization charts
3. **Report: "WP3_Audience_Profiles.pdf"** (2-3 pages):

   - Who attends ASO? (demographic summary)
   - How do single ticket buyers behave differently from subscribers?
   - Do subscribers maximize their packages?
   - Which seats are most popular?
   - 4-6 insights about audience behavior

### Success Criteria:

- [ ] Clear demographic profiles for each buyer type
- [ ] Specific findings (not vague: use numbers!)
- [ ] Subscription utilization rates calculated
- [ ] Cross-buying behavior identified
- [ ] Section preferences mapped to buyer types

---

## 🔄 WORK PACKAGE 4: SUBSCRIBER RETENTION & PROGRESSION

### **Assigned to:**

**Primary Files:** patron_summary.csv

### Your Mission:

Track subscriber journey - who moves from Freshman to Sophomore to Established? What keeps them coming back?

### Detailed Tasks:

#### 4.1: Subscriber Tenure Classification (1 hour)

**Set up your analysis:**

**A. Count Subscribers by Tenure:**
Filter patron_summary where has_subscription = TRUE:

- Count of Freshman subscribers (subscriber_tenure = "Freshman")
- Count of Sophomore subscribers
- Count of Established subscribers
- Total subscribers

**B. Tenure Distribution:**

- What % of all subscribers are Freshman?
- What % are Sophomore?
- What % are Established?
- Create pie chart

**C. By Subscription Size:**
For each tenure level, show breakdown by typical_subscription_size:

- How many Freshman have 6-concert packages?
- How many have 12-concert?
- Etc.

**Code hint:**

```python
patrons = pd.read_csv('patron_summary.csv')
subscribers = patrons[patrons['has_subscription'] == True].copy()

# Count by tenure
tenure_counts = subscribers['subscriber_tenure'].value_counts()
print("Subscriber Tenure Distribution:")
print(tenure_counts)
print("\nPercentages:")
print(tenure_counts / tenure_counts.sum() * 100)

# Tenure by package size
tenure_package = pd.crosstab(
    subscribers['subscriber_tenure'], 
    subscribers['typical_subscription_size']
)
print("\nTenure × Package Size:")
print(tenure_package)
```

#### 4.2: Subscriber Progression Analysis (2-3 hours)

**Track movement between tenure levels:**

**A. Identify Progressors:**
You need to track individual patrons between FY23 and FY24.

**Challenge:** Our data may not perfectly identify tenure progression because we only have 2 years of data. Do your best estimation:

**Approach 1 - Simple:**

- Patrons who were subscribers in FY23 AND FY24 (subscriber_fy23 = TRUE and subscriber_fy24 = TRUE)
- Of these, count how many stayed subscribed = "renewed"
- Calculate renewal rate = renewed / total_fy23_subscribers

**Approach 2 - More detailed (if tenure field is reliable):**

- Filter to subscribers present in BOTH years
- Try to identify:
  - How many were Freshman in FY23?
  - Of those, how many are still subscribers in FY24? (progressed to Sophomore)
  - How many were Sophomore in FY23?
  - Of those, how many are in FY24? (progressed to Established)

**Note:** You may need to work with Project Lead if the data doesn't clearly show this. Document your assumptions.

**B. Progression Rates:**
Calculate:

- Freshman → Sophomore progression rate (if identifiable)
- Sophomore → Established progression rate
- Overall retention rate (subscribed FY23 → subscribed FY24)

**C. Attrition Analysis:**

- How many FY23 subscribers did NOT return in FY24?
- What were their characteristics?
  - Average age
  - Typical package size
  - Average events attended in FY23 (did low attendance predict dropout?)

#### 4.3: Profile of "Newly Established" Subscribers (1-2 hours)

**Focus on patrons who became Established in 2024:**

Filter to: subscriber_tenure = "Established" (or however this is identified)

**Characteristics to analyze:**

- Count of patrons
- Average age
- Education level distribution (if available)
- Average # of concerts attended in FY23
- Average # attended in FY24
- Preferred subscription package size (6, 12, 18, 24)
- Average total spend over 2 years
- Most common sections they sit in
- Geographic concentration (top 5 zips)

**Create a persona:**
"The typical Established subscriber is a [age] year old from [zip codes], who attends [X] concerts per year, sits in [section], and spends [$X] annually."

#### 4.4: Discount Impact on Retention (2 hours)

**Does pricing affect renewal?**

**A. Discount Levels by Tenure:**
Using master_tickets:

- Average paid_amount for Freshman subscribers
- Average paid_amount for Sophomore subscribers
- Average paid_amount for Established subscribers
- Calculate average discount % compared to single ticket price

**B. Subscription Size vs Retention:**
Compare renewal rates by package size:

- 6-concert package: renewal rate
- 12-concert package: renewal rate
- 18-concert package: renewal rate
- 24-concert package: renewal rate

Hypothesis: Do larger packages have better retention? (more commitment)

**C. Utilization vs Retention:**
Compare subscribers who renewed vs didn't renew:

- Renewers: Average subscription utilization rate in FY23
- Non-renewers: Average utilization rate in FY23
- Hypothesis: People who attended more concerts in Year 1 are more likely to renew?

**Analysis:**

```python
# Renewers vs non-renewers
renewers = subscribers[(subscribers['subscriber_fy23'] == True) & (subscribers['subscriber_fy24'] == True)]
non_renewers = subscribers[(subscribers['subscriber_fy23'] == True) & (subscribers['subscriber_fy24'] == False)]

print("Renewers:")
print(f"  Count: {len(renewers)}")
print(f"  Avg age: {renewers['age'].mean():.1f}")
print(f"  Avg events attended FY23: {renewers['unique_events_fy23'].mean():.1f}")
print(f"  Avg spend: ${renewers['total_spend'].mean():.2f}")

print("\nNon-Renewers:")
print(f"  Count: {len(non_renewers)}")
print(f"  Avg age: {non_renewers['age'].mean():.1f}")
print(f"  Avg events attended FY23: {non_renewers['unique_events_fy23'].mean():.1f}")
print(f"  Avg spend: ${non_renewers['total_spend'].mean():.2f}")
```

#### 4.5: Subscriber Value Analysis (1 hour)

**Show why subscribers matter:**

**A. Lifetime Value:**

- Average total_spend per tenure level
- Freshman average spend over 2 years
- Established average spend over 2 years
- Revenue retention (how much more revenue from retained subscribers)

**B. Attendance Value:**

- Average unique_events_fy24 by tenure
- Do Established subscribers attend more concerts?

**C. Stability:**

- What % of total FY24 revenue came from Established subscribers?
- What % from Freshman?
- Insight: Established subscribers = stable revenue base

### Your Deliverables:

1. **Excel workbook: "WP4_Subscriber_Retention.xlsx"** with tabs:

   - Tenure_Distribution
   - Progression_Analysis
   - Established_Profile
   - Retention_by_Package_Size
   - Discount_Impact
2. **Simple visualizations:**

   - Tenure distribution pie chart
   - Progression flow diagram (if you can create)
   - Retention rates by package size
   - Renewers vs non-renewers comparison
3. **Report: "WP4_Subscriber_Journey.pdf"** (2 pages):

   - How many subscribers progress from Freshman → Established?
   - What characteristics predict retention?
   - Profile of our best subscribers (Established)
   - Does subscription size affect retention?
   - 3-5 recommendations for improving retention

### Success Criteria:

- [ ] Tenure distribution clearly shown
- [ ] Retention/progression rates calculated
- [ ] Clear comparison: renewers vs non-renewers
- [ ] Profile of Established subscribers created
- [ ] Insights are actionable (what drives retention?)

**Note:** This work package is the most straightforward! Focus on clean tables and clear comparisons.

---

## 📈 WORK PACKAGE 5: YEAR-OVER-YEAR TRENDS & GROWTH

### **Assigned to:**

**Your Mission:

Compare FY23 vs FY24 to identify growth trends and changes in audience composition.

### Detailed Tasks:

#### 5.1: Overall Year-over-Year Comparison (1-2 hours)

**High-level metrics - FY23 vs FY24:**

Create a comparison table:

| Metric                       | FY23 | FY24 | Change | % Change |
| ---------------------------- | ---- | ---- | ------ | -------- |
| Total Tickets Sold           |      |      |        |          |
| Total Revenue                |      |      |        |          |
| Unique Patrons               |      |      |        |          |
| Average Ticket Price         |      |      |        |          |
| Number of Events             |      |      |        |          |
| Average Attendance per Event |      |      |        |          |
| Average Patron Age           |      |      |        |          |
| % Premium Seats              |      |      |        |          |
| % Value Seats                |      |      |        |          |

**Code to get started:**

```python
events = pd.read_csv('event_summary.csv')
patrons = pd.read_csv('patron_summary.csv')

# FY23 totals
fy23_events = events[events['fiscal_year'] == 'FY23']
fy23_tickets = fy23_events['total_tickets_sold'].sum()
fy23_revenue = fy23_events['total_revenue'].sum()
fy23_event_count = len(fy23_events)

# FY24 totals
fy24_events = events[events['fiscal_year'] == 'FY24']
fy24_tickets = fy24_events['total_tickets_sold'].sum()
fy24_revenue = fy24_events['total_revenue'].sum()
fy24_event_count = len(fy24_events)

# Calculate changes
ticket_change = fy24_tickets - fy23_tickets
ticket_pct_change = (ticket_change / fy23_tickets) * 100

print(f"FY23: {fy23_tickets:,} tickets, ${fy23_revenue:,.2f} revenue")
print(f"FY24: {fy24_tickets:,} tickets, ${fy24_revenue:,.2f} revenue")
print(f"Change: {ticket_change:,} tickets ({ticket_pct_change:+.1f}%)")
```

**Insights to highlight:**

- Did we grow or decline overall?
- Did revenue grow faster than attendance? (price increase effect)
- Did we hold more or fewer events?

#### 5.2: Growth by Buyer Category (2 hours)

**Which audience segments grew?**

**A. Buyer Type Growth:**
For each buyer_category, compare FY23 vs FY24:

- Single Ticket buyers: count and % change
- Subscribers (each tier): count and % change
- College Pass: count and % change

Use both patron_summary and master_tickets:

```python
# Approach 1: Count unique patrons by year
fy23_patrons = patrons[patrons['fy23_tickets'] > 0]
fy24_patrons = patrons[patrons['fy24_tickets'] > 0]

fy23_single = fy23_patrons[fy23_patrons['has_single_tickets'] == True]
fy24_single = fy24_patrons[fy24_patrons['has_single_tickets'] == True]

print(f"Single Ticket Buyers:")
print(f"  FY23: {len(fy23_single)}")
print(f"  FY24: {len(fy24_single)}")
print(f"  Change: {len(fy24_single) - len(fy23_single)} ({(len(fy24_single)/len(fy23_single)-1)*100:+.1f}%)")
```

**B. Revenue Growth by Category:**

- Which buyer type generated most revenue growth?
- Which declined?
- Create stacked bar chart: FY23 vs FY24 revenue by buyer type

**C. Ticket Volume Growth:**

- Same analysis but for ticket count (not unique patrons)
- Did subscribers buy more tickets per person?

#### 5.3: Event-Level Growth Analysis (2 hours)

**Which concerts improved? Which declined?**

**A. Repeated Events:**
Identify events that happened in BOTH FY23 and FY24 (same event_name or similar):

- For each repeated event, compare:
  - Attendance change
  - Revenue change
  - Average age change
  - Average ticket price change

**B. Top Gainers:**

- Top 10 events with biggest attendance increase
- Top 10 with biggest revenue increase
- What do they have in common?

**C. Top Decliners:**

- Events that lost attendance YoY
- Events that lost revenue YoY
- Why did they decline?

**Note:** Some events may be one-time only. Focus on events that repeated.

#### 5.4: Demographic Shifts (1-2 hours)

**Is our audience changing?**

**A. Age Trends:**
Compare FY23 vs FY24 overall:

- Average patron age
- % under 35
- % 35-49
- % 50-64
- % 65+
- Are we getting younger or older?

**B. By Buyer Type:**

- Single ticket buyer average age: FY23 vs FY24
- Subscriber average age: FY23 vs FY24
- Which segment is getting younger?

**C. Geographic Shifts:**

- Top 10 zip codes in FY23
- Top 10 zip codes in FY24
- Any changes in patron origins?
- Are we attracting from new areas?

#### 5.5: Pricing Trends (1 hour)

**Price changes over time:**

**A. Average Ticket Price:**

- FY23 average paid_amount
- FY24 average paid_amount
- % change
- Did dynamic pricing lead to higher average prices?

**B. By Buyer Type:**

- Average price paid by Single buyers: FY23 vs FY24
- Average price paid by Subscribers: FY23 vs FY24
- Did pricing strategy change by segment?

**C. By Price Tier:**

- % of tickets in Premium tier: FY23 vs FY24
- % in Value tier
- Did audience trade up or down?

#### 5.6: Trend Summary & Projections (1 hour)

**Big picture insights:**

**A. Growth Rate Calculations:**

- Overall CAGR (Compound Annual Growth Rate) for revenue
- Attendance growth rate
- Patron base growth rate

**B. Key Trends:**
Identify and document:

- Fastest growing segment
- Fastest declining segment
- Most improved event type
- Biggest demographic shift

**C. Simple Projections (if time):**
If trends continue:

- Projected FY25 attendance (linear extrapolation)
- Projected FY25 revenue
- Projected patron count

**Note:** These are very simple projections, just illustrative.

### Your Deliverables:

1. **Excel workbook: "WP5_YoY_Trends.xlsx"** with tabs:

   - Overall_Comparison
   - Growth_by_Buyer_Category
   - Event_Level_Changes
   - Demographic_Shifts
   - Pricing_Trends
2. **Visualizations:**

   - Side-by-side bar charts (FY23 vs FY24)
   - Revenue growth by category
   - Age distribution comparison
   - Top gainers/decliners
3. **Report: "WP5_Growth_Trends.pdf"** (2 pages):

   - Are we growing or declining overall?
   - Which segments are growing?
   - Which events improved?
   - Is our audience getting younger?
   - 4-5 trend insights and implications

### Success Criteria:

- [ ] Complete FY23 vs FY24 comparison table
- [ ] Growth rates calculated for all major segments
- [ ] Clear identification of winners and losers
- [ ] Demographic trends documented
- [ ] Insights are forward-looking (what do trends suggest?)

**Note:** This is the most straightforward work package - focus on clean comparisons!

---

## 🎯 PHASE 6: SYNTHESIS & STRATEGIC RECOMMENDATIONS

Gaby

#### 6.1: Returner Deep Dive (4-5 hours)

**The 80/20 problem - your most critical analysis**

**A. Define Cohorts:**
Using patron_summary and master_tickets:

- **One-Time Patrons:** Attended 1 event total across FY23-24, did not return
- **Same-Year Returners:** Attended 2+ events in one FY, but not both years
- **Multi-Year Returners:** Attended events in both FY23 and FY24

**B. First Event Analysis:**
For each cohort, identify what they saw FIRST:

- What event did one-timers attend? (their only event)
- What event did returners see first?
- Compare:
  - Event type distribution (Delta vs Holiday vs Special)
  - Average ticket price of first purchase
  - Section of first purchase
  - Days before event for first purchase
  - Month/season of first attendance

**Key Question:** Are certain events "gateway" events that lead to returns, while others are "dead ends"?

**C. The Return Journey (Returners Only):**

- Time between first and second purchase (histogram)
- What was their second event?
- Did they upgrade section/price tier?
- Did they move from single ticket to subscriber?

**D. Statistical Analysis:**
Run chi-square or logistic regression:

- Factors predicting return:
  - Age
  - First event type
  - Price tier of first purchase
  - Month of first attendance
  - Section
  - Days before event purchased

**Goal:** Build a model to predict: "This first-time buyer is X% likely to return"

#### 6.2: Subscription Conversion Funnel (3-4 hours)

**Track the journey: Single Ticket → Subscriber**

**A. Define Conversion Path:**

- Patrons who were single ticket buyers in FY23
- Of those, how many became subscribers in FY24?
- Conversion rate

**B. Pre-Subscription Behavior:**
For those who converted:

- How many events did they attend as single ticket buyers before subscribing?
- How long between first single ticket purchase and subscription?
- What events did they attend before subscribing?
- Average total spend as single ticket buyer

**C. Failed Conversions:**
Single ticket buyers who attended 3+ events but didn't subscribe:

- Why not? (can't answer directly, but profile them)
- Age, spend, events attended
- Hypothesis: Price sensitivity? Commitment issues?

**D. Optimize the Funnel:**
Recommendations:

- After how many visits should we push subscription offers?
- Which events attract convertible single ticket buyers?
- What price point encourages conversion?

#### 6.3: Age-Based Engagement Strategy (3 hours)

**How do we engage younger audiences?**

**A. Age Cohort Comparison:**
Create profiles for 4 age groups: <35, 35-49, 50-64, 65+

For each group:

- Current size (% of audience)
- Growth rate (FY23 vs FY24)
- Preferred buyer type (single vs subscription)
- Price sensitivity (average paid_amount)
- Event preferences (which concerts?)
- Purchase behavior (days before, section preference)
- Return rate

**B. The "Young Professional" Segment (Under 40):**
Deep dive on this strategic segment:

- How many exist?
- What brings them to ASO?
- What would make them return?
- Lifetime value potential (if we convert them young)

**C. College Pass to Patron Pipeline:**

- How many college pass users transition to paying patrons?
- What % buy single tickets after aging out?
- What % become subscribers?
- How to improve conversion?

**D. Programming Insights:**

- Which events attract youngest audiences?
- Is there a "young audience" program type?
- Recommendations for age-targeted programming

#### 6.4: Predictive Models (3-4 hours)

**Build simple models to guide decisions:**

**A. Renewal Prediction Model:**
Using subscriber data, predict renewal likelihood:

- Features: age, package size, utilization rate, tenure, total spend
- Target: renewed in FY24 (yes/no)
- Build logistic regression or decision tree
- Output: probability score for each subscriber

**B. Churn Risk Scoring:**
Identify subscribers at risk of not renewing:

- Low utilization in FY24
- Declining attendance trend
- Younger age (less established)
- Create risk tiers: High, Medium, Low

**C. Revenue Optimization:**

- Which patron segments have highest ROI?
- Where should marketing focus?
- Subscriber acquisition cost vs lifetime value

#### 6.5: Integration & Strategic Synthesis (4-5 hours)

**Combine all team findings into coherent strategy:**

**A. Answer the Three Questions:**

**Question 1: How do we get single ticket buyers to return?**
Synthesize findings from:

- Your returner analysis
- WP1 (which events they attend)
- WP3 (their characteristics)
- WP5 (trends over time)

Recommendations:

- Which events to use as "gateway" concerts
- When to reach out (timing)
- What to offer (pricing, programming)
- Segmented approach by age

**Question 2: How do we attract and retain subscribers?**
Synthesize findings from:

- Your conversion funnel analysis
- WP2 (revenue and pricing)
- WP4 (retention patterns)
- Your predictive models

Recommendations:

- Conversion triggers (after X visits, offer Y)
- Package optimization (which sizes to push)
- Retention strategies by tenure
- Pricing adjustments

**Question 3: How do we engage younger audiences?**
Synthesize findings from:

- Your age analysis
- WP3 (demographics)
- WP1 (which events attract younger crowds)
- College pass conversion data

Recommendations:

- Programming that appeals to <40 demographic
- Pricing strategies for young professionals
- Marketing channels
- Partnership opportunities

**B. Prioritization Matrix:**
Rank recommendations by:

- Impact (revenue potential)
- Ease (implementation difficulty)
- Time (quick wins vs long-term)

**C. ROI Projections:**
For top recommendations, estimate:

- If we improve return rate from 20% to 30%, revenue impact = $X
- If we improve renewal rate from 50% to 60%, revenue impact = $Y
- If we attract 500 more patrons under 40, lifetime value = $Z
