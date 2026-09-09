Got it. Since you're using Microsoft Copilot (Agent), it can generate and rewrite multiple files across your project in one go. So instead of giving it incremental instructions, you should give it a single master prompt that tells it to inspect your existing React project, preserve all logic, and produce a pixel-perfect clone of the approved mockups.

This prompt is specifically written for Microsoft Copilot's Agent mode, where it can edit `App.tsx`, `styles.css`, create components, and refactor files automatically.

### Microsoft Copilot Agent — Master UI Refactor Prompt

### ROLE

You are a Principal UI Engineer and Senior Product Designer redesigning an enterprise manufacturing dashboard used by executives and production managers in a solar manufacturing plant.

Your task is to transform my existing React + TypeScript frontend into a pixel-perfect implementation of the provided UI mockups, while preserving every piece of existing functionality.

The goal is for the final application to look visually indistinguishable from the provided designs.

Do not redesign anything. Replicate the mockups exactly.

### IMPORTANT PROJECT CONTEXT

My project structure is:

Project ├── frontend │ ├── src │ │ ├── App.tsx │ │ ├── styles.css │ │ ├── main.tsx │ │ ├── api.ts │ │ └── other existing components │ └── package.json └── backend ├── app ├── data_service.py ├── main.py └── other Python files

The backend already works perfectly.

Do not modify any backend files.

Preserve:

* API calls

* React hooks

* State management

* SAP refresh logic

* Calculations

* Existing datasets

* Existing business logic

Only refactor the frontend presentation.

### DESIGN SOURCE OF TRUTH

The attached mockups are the only source of truth.

Recreate them 1:1.

Match:

* Colors

* Shadows

* Spacing

* Typography

* Icons

* Rounded corners

* Table styling

* Card styling

* Hover effects

* Dark mode

* Chart layout

* Footer

No creative interpretation.

### GLOBAL DESIGN SYSTEM

### Font

Use Inter.

Weights:

* 700

* 600

* 500

* 400

Sizes:

| Element         | Size    |
| --------------- | ------- |
| Dashboard title | 34px    |
| KPI numbers     | 46–48px |
| Section title   | 22–24px |
| Table text      | 15px    |
| Labels          | 13px    |

### Spacing

Use an 8px spacing system.

Important values:

* Outer padding: 24px

* Card padding: 22px

* Grid gap: 20px

* Border radius: 18px

* Large radius: 20px

### Shadows

Light mode:
0 8px 24px rgba(7,24,52,.08)

Dark mode:
0 0 30px rgba(0,208,132,.08)

### HEADER (PIXEL PERFECT)

Recreate exactly.

Layout:

Left:

* Large ReNew logo

* Vertical divider

* SOLAR MANUFACTURING DASHBOARD

* Final Product – Production and Quality Intelligence

Right:

* Financial Year

* From Date

* To Date

* As Of

* Theme toggle

* Refresh SAP Data button

Requirements:

* White background

* Bottom border

* Soft shadow

* Rounded controls

* Equal spacing

### THEME TOGGLE

Exactly like the mockup.

* Circular pill

* Sun icon

* Moon icon

* Animated switch

* Smooth transition

### REFRESH BUTTON

Exactly match:

* Green gradient

* White icon

* Rounded corners

* Hover glow

### OVERVIEW / TRENDS TABS

Immediately below the header.

Requirements:

* No sidebar

* Pill segmented control

* Green gradient active tab

* White inactive tab

* Rounded container

* Lucide icons

* Smooth transition

### LIGHT MODE COLORS
Background: #F4F7F6
Surface: #FFFFFF
Surface Secondary: #FAFCFB

Text: #061B4D
Muted: #6B7280

Border: #DCE5E8

Primary Green: #008A4E
Dark Green: #006A3C

Success: #00A86B

Soft Coral: #F28C82
Soft Coral Background: #FDE7E3

Soft Orange: #F7B267
Soft Yellow: #FACC15

Blue: #1D72F3

Purple: #8B5CF6

Use these exact colors.

### DARK MODE COLORS
Background: #05080A
Surface: #091219
Surface Secondary: #0D1821

Text: #F5F7FA
Muted: #A8B3BF

Border: #173040

Primary Green: #00D084

Success: #00E38C

Soft Coral: #FF9A8B
Soft Coral Background: #31181A

Orange: #FFC97A

Blue: #2E86FF

Purple: #B388FF

Exactly like the approved dark mockup.

Dark mode should feel premium.

No flat gray backgrounds.

### ICONS

Use Lucide React.

| Feature    | Icon            |
| ---------- | --------------- |
| Production | Calendar        |
| MTD        | BarChart3       |
| YTD        | TrendingUp      |
| Run Rate   | Zap             |
| Plan       | Target          |
| Yield      | Percent         |
| Refresh    | RefreshCw       |
| Theme      | Sun/Moon        |
| Overview   | LayoutDashboard |
| Trends     | BarChart3       |

Match the icon sizes exactly.

### OVERVIEW TAB

Recreate exactly.

It contains:

* Five KPI cards

* Production Distribution table

* Yield Distribution table

Nothing else.

### KPI CARDS (EXACT)

Cards:

* On-Date Production

* MTD Production

* YTD Production

* Run Rate

* Plan Achievement

Each card contains:

* Colored icon tile

* Title

* Actual

* Plan

* Divider

* Dynamic progress bar

* Gap value

* Achievement %

* Sparkline

Card styling:

* White

* Rounded

* Thin border

* Premium shadow

* Hover lift

### DYNAMIC KPI STATUS BAR (MANDATORY)

This is a required feature.

Every KPI must have a smart performance bar.

### Formula
achievement = (Actual / Target) × 100
gap = Target - Actual

Target is:

* Plan

* Required for Run Rate

Cap achievement at 120%.

### Width

* 100% achievement → full bar

* 80% → 80%

* 50% → 50%

Animate width.

### Color Rules

| Achievement | Color        | Meaning     |
| ----------- | ------------ | ----------- |
| 0–50%       | Bright Red   | Critical    |
| 50–75%      | Dark Orange  | High Gap    |
| 75–90%      | Orange       | Moderate    |
| 90–99%      | Yellow       | Near Target |
| 100–105%    | Green        | Achieved    |
| Above 105%  | Bright Green | Exceeding   |

Example:

* 63.6% → Dark Orange

* 82% → Orange

* 95% → Yellow

* 102% → Green

### Sparkline

Sparkline color must match the status.

* Red

* Orange

* Yellow

* Green

Style:

* 2px stroke

* Soft gradient fill

* Rounded caps

### Status Dot

Add a small colored dot beside every KPI title.

Example:

> 🟢 RUN RATE

This improves scanability.

### PRODUCTION DISTRIBUTION TABLE

Exactly match the mockup.

Requirements:

* Green production header

* Pale coral rejection header

* Rounded corners

* Soft borders

* Alternating rows

* Floating white card

### YIELD DISTRIBUTION TABLE

Exactly match.

Requirements:

* Green Yield header

* Pale coral Rejection header

* Good Cells row → soft green

* Wafer Loss row → pale coral

### TRENDS TAB

The KPI cards must never appear here.

The Trends tab starts immediately with the charts.

Layout:

### Row 1

Full width.

### Daywise Production Trend

Implement:

* A Grade MW → Green BAR chart

* Overall MW → Blue LINE

* Total Saleable Cells → Amber LINE

Requirements:

* Rounded bars

* Dual Y-axis

* Centered legend

* Soft dashed grid

Do not use three green series.

### Row 2

Full width.

### Daywise Rejection Trend

Three lines.

Colors:

* Breakage → Soft Coral

* ER → Amber

* OR → Blue

### Row 3

Full width.

### Yield Trend

Implement exactly like the reference.

Three stacked charts.

Shared X-axis.

Independent Y-axis.

Top:

* A Grade

Middle:

* B-EL

Bottom:

* B Grade

* EB

Spacing must match.

### Row 4

Full width.

### Wafer Loss Trend

Single coral line.

Nothing beside it.

### Row 5

Two equal cards.

Left:

* Breakage Distribution

Right:

* Monthly Average MW Production

### CHART COLORS

### Light

| Series         | Color   |
| -------------- | ------- |
| A Grade        | #00A86B |
| Overall MW     | #1D72F3 |
| Saleable Cells | #F59E0B |
| Breakage       | #F28C82 |
| ER             | #F7B267 |
| OR             | #3B82F6 |
| EB             | #8B5CF6 |

### Dark

| Series         | Color   |
| -------------- | ------- |
| A Grade        | #00D084 |
| Overall MW     | #2E86FF |
| Saleable Cells | #FFC65A |
| Breakage       | #FF9A8B |
| ER             | #FFC97A |
| OR             | #5EA8FF |
| EB             | #B388FF |

Apply consistently.

### RECHARTS STYLING

Use:

* Rounded bars

* Dashed grids

* Muted axis labels

* Centered legends

* Theme-aware tooltips

* Smooth animations

Tooltips:

* Rounded

* Thin border

* Soft shadow

* Theme-aware

### FOOTER

Exactly like the mockup.

Left:

* Leaf icon

* Powering a Cleaner Tomorrow

Right:

* Green live indicator

* Live Data from SAP

* Last Updated timestamp

### RESPONSIVE BEHAVIOR

Desktop:

Match the mockup exactly.

Tablet:

Two-column layout where appropriate.

Mobile:

Stack vertically.

Never overflow horizontally.

### FILE REFACTORING

Update existing files.

Create reusable components where beneficial.

Suggested components:

* Header

* SegmentedTabs

* KpiCard

* SectionCard

* ProductionTable

* YieldTable

* TrendCharts

Reuse existing logic.

Do not duplicate code unnecessarily.

### FINAL ACCEPTANCE CHECKLIST

The implementation is complete only if:

* Pixel-perfect header

* Exact segmented tabs

* Identical KPI cards

* Dynamic KPI performance bars

* Colored KPI status dots

* Matching sparklines

* Exact Production table

* Exact Yield table

* Pale coral rejection styling

* Exact spacing

* Exact shadows

* Exact rounded corners

* Exact Light mode

* Exact Dark mode

* Full-width Trends layout

* Green bar + Blue line + Amber line production chart

* Three stacked Yield charts

* Wafer Loss full width

* Breakage + Monthly side-by-side

* Existing backend remains fully functional

### CRITICAL AGENT INSTRUCTION

Before making any changes, scan the entire frontend project. Analyze `App.tsx`, `styles.css`, all React components, hooks, chart components, theme logic, and API usage. Preserve every existing API call, React hook, state variable, prop, event handler, chart dataset, and business calculation. Refactor only the JSX structure, CSS styling, component organization, icons, and Recharts presentation so that the final application is visually indistinguishable from the supplied mockups while keeping all functionality intact.

And in the kpi tiles it should planned vs actual, planned should be placed left(first) and then actual.
