Please update the Solar Cell Manufacturing Dashboard with the following UI and business logic changes.

# OVERALL DESIGN PRINCIPLE

The Overview tab is intended to be an executive summary of the latest available production day.

The Overview tab should NOT be date-range driven.

Instead, it should always display:

AS OF: <Latest Available Production Date>

Example:

AS OF: 15-May-2025

All KPI cards, summaries, and charts on the Overview tab should be calculated relative to this effective dashboard date.

Production and Analytics tabs will continue to support user-selected date ranges.

---

## 1. OVERVIEW HEADER CHANGES

### Remove View Selector from Overview

Current controls:

- FY Selector
- View Selector
- Refresh Timestamp
- Refresh Button
- Filters Button

Required:

Remove the View selector entirely from the Overview tab.

The View selector should only exist on:

- Production tab
- Analytics tab

Overview should not contain a View dropdown or View icon.

---

### Remove Filters Button

Remove the Filters button from all screens.

No Filters icon should appear in the application header.

Filtering should occur only through dedicated controls such as date selectors where applicable.

---

## 2. OVERVIEW DATE CONTEXT

Display a clear dashboard date context.

Example:

Real-Time Production Monitoring — As of 15-May-2025

or

AS OF: 15-May-2025

This date represents the latest available production date and acts as the reference date for all KPI calculations.

All Overview KPIs, summary cards and charts must stay synchronized with this date.

---

## 3. TODAY'S PRODUCTION CARD

Current:

TODAY'S PRODUCTION

Required:

TODAY'S PRODUCTION (15-May-2025)

Rules:

- Date must always match the Overview "As Of" date.
- If latest available production date changes, update automatically.
- Date must never be hardcoded.

Example:

TODAY'S PRODUCTION (15-May-2025)

5.23 MW

▲ 12.65% vs Yesterday (4.64 MW, +0.59 MW)

---

## 4. MTD AND YTD KPI LOGIC

Do NOT determine MTD/YTD from arbitrary date ranges on the Overview page.

Instead:

Use the Overview "As Of" date.

Example:

As Of Date = 15-May-2025

Then:

MTD Production = 01-May-2025 → 15-May-2025

YTD Production = 01-Apr-2025 → 15-May-2025

Financial year start:

01-Apr

---

### MTD Card Format

MTD PRODUCTION

(01-May-2025 → 15-May-2025)

125.80 MW

▲ 8.15% vs Previous MTD (+9.48 MW)

---

### YTD Card Format

YTD PRODUCTION

(01-Apr-2025 → 15-May-2025)

685.42 MW

▲ 15.62% vs Previous FY YTD (+92.46 MW)

---

Rules:

- MTD and YTD should always be displayed simultaneously.
- Never replace MTD with YTD.
- Never hide either KPI.
- Both are calculated relative to the Overview As-Of Date.

---

## 5. KPI COMPARISON ENHANCEMENT

All KPI cards must display:

1. Relative change
2. Comparison period
3. Absolute difference

Format:

[Relative Change] vs [Comparison Period] ([Reference Value], [Absolute Delta])

Examples:

▲ 12.65% vs Yesterday (4.64 MW, +0.59 MW)

▲ 8.15% vs Previous MTD (116.32 MW, +9.48 MW)

▲ 15.62% vs Previous FY YTD (592.96 MW, +92.46 MW)

▲ 1.25% vs Yesterday (92.27%, +1.15%)

▼ 0.32% vs Last Month (1.36%, -0.21%)

▲ 0.28 MW/day vs Required (4.67 MW/day, +0.28 MW/day)

---

### Production Metrics

Display:

▲ 12.65% vs Yesterday (4.64 MW, +0.59 MW)

or

▲ 12.65% vs Yesterday (317,037 Cells, +3 Cells)

depending on the metric unit.

---

### Yield Metrics

Display:

▲ 1.25% vs Yesterday (92.27%, +1.15%)

---

### Reject Metrics

Display:

▼ 0.32% vs Last Month (1.36%, -0.21%)

---

### Run Rate Metrics

Display:

▲ 0.28 MW/day vs Required (4.67 MW/day, +0.28 MW/day)

---

## 6. OVERVIEW CHART SYNCHRONIZATION

All Overview visualizations must use the same As-Of Date context.

Examples:

If As Of = 15-May-2025:

Daily Trend:
- Show days up to 15-May-2025

MTD Summary:
- Show metrics up to 15-May-2025

Monthly Summary:
- Current month values should reflect data up to 15-May-2025

No chart should display data beyond the selected As-Of Date.

---

## 7. PRODUCTION TAB

No functional changes.

Keep:

- Date range picker
- Apply Range button
- View selector

Production charts should continue to respond to selected date ranges.

---

## 8. ANALYTICS TAB

No functional changes.

Keep:

- Date range picker
- Apply Range button
- View selector

Analytics visualizations should continue to respond to selected date ranges.

---

## 9. CONSISTENCY REQUIREMENTS

- Preserve existing layout.
- Preserve existing dark theme.
- Preserve existing colors.
- Preserve KPI card styling.
- Preserve chart styling.
- Remove Filters button globally.
- Remove View selector only from Overview.
- Keep View selector on Production and Analytics.
- Add date to Today's Production title.
- Use latest available production date as Overview reference.
- Show both MTD and YTD KPIs simultaneously.
- Show comparison percentage plus absolute delta value on every KPI.
- Ensure all Overview elements remain synchronized with the Overview As-Of Date.
