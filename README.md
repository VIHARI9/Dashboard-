# ReNew Solar Manufacturing Dashboard v2

Professional responsive React + TypeScript frontend with a FastAPI Python backend.

## Dashboard design

- Two tabs only: **Overview** and **Trends**.
- Financial-year selector in the title header.
- For a previous financial year, **On Date** uses the last available day in that FY and **MTD** uses the final available month in that FY.
- Existing Excel files are loaded on startup. SAP is contacted only when **Refresh SAP Data** is clicked.

## Expected Excel workbooks

Copy these files to `backend/data/`:

- `Daywise Data.xlsx`
- `Daywise MW Report.xlsx`
- `Monthwise MW Report.xlsx`
- `Monthwise Report.xlsx`
- `Plan.xlsx`

The current application calculations use the two day-wise files and Plan.xlsx. Month-wise files are retained for SAP refresh compatibility.

## OR mapping

The available source wording previously supplied contains ER, FOR and ER(Q). This project displays **OR** using the configured ER(Q) value. Change `OR_SOURCE_FIELD` in `backend/app/config.py` if your OR field means something else.

## Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

## Frontend

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```
$NodeFolder = "C:\Users\vijaya.kalyani\Downloads\renew-solar-dashboard-v2\node-v24.20.0-win-x64"
$env:Path = "$NodeFolder;$env:Path"

cd "C:\Users\vijaya.kalyani\Downloads\renew-solar-dashboard-v2\frontend"

node.exe --version
npm.cmd --version
npm.cmd install
npm.cmd run dev

Frontend: http://localhost:5173

## Production build

```powershell
cd frontend
npm.cmd run build
```
$NodeFolder = "C:\Users\vijaya.kalyani\Downloads\renew-solar-dashboard-v2\node-v24.20.0-win-x64"

$env:Path = "$NodeFolder;$env:Path"

cd "C:\Users\vijaya.kalyani\Downloads\renew-solar-dashboard-v2\frontend"

node.exe --version
npm.cmd --version

npm.cmd run build

Then start FastAPI without `--reload`. FastAPI serves `frontend/dist` at http://localhost:8000.


##Styles.css
/* =========================================================
   PREMIUM BLACK DARK MODE
   Add this at the very bottom of styles.css
   ========================================================= */

:root[data-theme="dark"] {
  color-scheme: dark;

  --page-bg: #070809;
  --surface: #101214;
  --surface-elevated: #15181b;
  --surface-soft: #191c20;
  --surface-muted: #20242a;

  --theme-text: #f4f6f8;
  --theme-text-muted: #9fa7b2;

  --theme-border: #2b3037;
  --theme-border-strong: #3a414b;

  --theme-accent: #7c6cff;
  --theme-accent-bright: #9487ff;
  --theme-accent-secondary: #20b8e5;

  --theme-grid: #292e35;
  --theme-shadow: rgba(0, 0, 0, 0.48);
}


/* Main page */

:root[data-theme="dark"] body,
:root[data-theme="dark"] .app {
  color: var(--theme-text);

  background:
    radial-gradient(
      circle at 85% -10%,
      rgba(124, 108, 255, 0.14),
      transparent 34rem
    ),
    radial-gradient(
      circle at 5% 100%,
      rgba(32, 184, 229, 0.08),
      transparent 30rem
    ),
    var(--page-bg) !important;
}


/* Header */

:root[data-theme="dark"] header {
  color: var(--theme-text);
  background: rgba(12, 14, 16, 0.96) !important;

  border-bottom:
    1px solid
    var(--theme-border) !important;

  box-shadow:
    0 8px 28px
    rgba(0, 0, 0, 0.42) !important;

  backdrop-filter: blur(16px);
}


:root[data-theme="dark"] .brand h1 {
  color: #f4f6f8 !important;

  background:
    linear-gradient(
      90deg,
      #ffffff,
      #b9c3ff
    );

  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}


:root[data-theme="dark"] .brand p {
  color: #a7afb9 !important;
}


/* If the logo contains a dark background,
   this gives the logo a gentle lift */

:root[data-theme="dark"] header img {
  filter:
    brightness(1.08)
    contrast(1.05);
}


/* FY and date controls */

:root[data-theme="dark"] .controls label {
  color: #adb5c0 !important;
}


:root[data-theme="dark"] .controls select,
:root[data-theme="dark"] .controls input {
  color: #f4f6f8 !important;
  background: #171a1e !important;

  border:
    1px solid
    #343a43 !important;

  box-shadow:
    inset 0 1px 0
    rgba(255, 255, 255, 0.025);
}


:root[data-theme="dark"] .controls select:hover,
:root[data-theme="dark"] .controls input:hover {
  border-color:
    #6259b7 !important;
}


:root[data-theme="dark"] .controls select:focus,
:root[data-theme="dark"] .controls input:focus {
  outline: none;

  border-color:
    var(--theme-accent) !important;

  box-shadow:
    0 0 0 3px
    rgba(124, 108, 255, 0.18);
}


/* As-of card */

:root[data-theme="dark"] .asof {
  color: #aeb6c1 !important;
  background: #171a1e !important;

  border:
    1px solid
    #343a43 !important;
}


:root[data-theme="dark"] .asof b {
  color: #ffffff !important;
}


/* Theme button */

:root[data-theme="dark"] .themeToggle {
  color: #f0d76b !important;
  background: #1b1d21 !important;

  border:
    1px solid
    #3b4048 !important;

  box-shadow:
    0 5px 16px
    rgba(0, 0, 0, 0.28) !important;
}


:root[data-theme="dark"] .themeToggle:hover {
  color: #ffe783 !important;
  background: #25282d !important;

  border-color:
    #555c67 !important;

  transform: translateY(-1px);
}


/* Refresh SAP button */

:root[data-theme="dark"] .controls button:not(.themeToggle) {
  color: #ffffff !important;

  background:
    linear-gradient(
      135deg,
      #6d5dfc,
      #8b5cf6
    ) !important;

  border:
    1px solid
    rgba(255, 255, 255, 0.12) !important;

  box-shadow:
    0 8px 22px
    rgba(109, 93, 252, 0.3) !important;
}


:root[data-theme="dark"]
  .controls button:not(.themeToggle):hover {
  background:
    linear-gradient(
      135deg,
      #7d6eff,
      #9a70ff
    ) !important;

  transform: translateY(-1px);
}


/* Navigation */

:root[data-theme="dark"] nav {
  background: #111315 !important;

  border:
    1px solid
    #2d3239 !important;

  box-shadow:
    0 8px 26px
    rgba(0, 0, 0, 0.32) !important;
}


:root[data-theme="dark"] nav button {
  color: #cbd1d9 !important;
  background: #111315 !important;
}


:root[data-theme="dark"] nav button + button {
  border-left-color:
    #2d3239 !important;
}


:root[data-theme="dark"] nav button:hover {
  color: #ffffff !important;
  background: #181b1f !important;
}


:root[data-theme="dark"] nav button.active {
  color: #ffffff !important;

  background:
    linear-gradient(
      135deg,
      #6558e8,
      #7c6cff
    ) !important;

  box-shadow:
    inset 0 -4px
    #20b8e5 !important;
}


/* KPI cards */

:root[data-theme="dark"] .kpi {
  color: var(--theme-text);
  background: #111416 !important;

  border:
    1px solid
    #2b3037 !important;

  border-top:
    4px solid
    #7c6cff !important;

  box-shadow:
    0 10px 28px
    rgba(0, 0, 0, 0.38) !important;
}


:root[data-theme="dark"] .kpi:hover {
  border-color: #424850 !important;

  box-shadow:
    0 15px 34px
    rgba(0, 0, 0, 0.46) !important;

  transform: translateY(-2px);
}


:root[data-theme="dark"] .kpi.positive {
  border-top-color:
    #27c47d !important;
}


:root[data-theme="dark"] .kpi.negative {
  border-top-color:
    #ff5263 !important;
}


:root[data-theme="dark"] .kpi.neutral {
  border-top-color:
    #7c6cff !important;
}


:root[data-theme="dark"] .kpiTop span {
  color: #dfe4ea !important;
}


:root[data-theme="dark"] .kpiTop svg {
  color: #7d8791 !important;
}


:root[data-theme="dark"] .compare strong {
  color: #ffffff !important;
}


:root[data-theme="dark"]
  .compare > div:last-child strong {
  color: #c7ced7 !important;
}


:root[data-theme="dark"] .compare small,
:root[data-theme="dark"] .compare em {
  color: #9099a5 !important;
}


:root[data-theme="dark"] .compare > i {
  background: #3a4048 !important;
}


:root[data-theme="dark"] .kpi footer {
  border-top-color:
    #31363d !important;
}


:root[data-theme="dark"] .kpi footer b {
  color: #c7ced7 !important;
}


:root[data-theme="dark"] .kpi.positive footer b {
  color: #35d88e !important;
}


:root[data-theme="dark"] .kpi.negative footer b {
  color: #ff6474 !important;
}


:root[data-theme="dark"] .kpi footer span {
  color: #abb3bd !important;
}


/* Panels and floating cards */

:root[data-theme="dark"] .panel,
:root[data-theme="dark"] .floatingTableCard {
  color: var(--theme-text);

  background:
    linear-gradient(
      180deg,
      #121517,
      #0f1113
    ) !important;

  border:
    1px solid
    #2b3037 !important;

  box-shadow:
    0 14px 34px
    rgba(0, 0, 0, 0.42) !important;
}


:root[data-theme="dark"]
  .floatingTableCard::before {
  background:
    linear-gradient(
      90deg,
      #7c6cff,
      #20b8e5
    ) !important;
}


:root[data-theme="dark"]
  .floatingTableCard:hover {
  border-color: #404751 !important;

  box-shadow:
    0 18px 40px
    rgba(0, 0, 0, 0.52) !important;
}


:root[data-theme="dark"] .panel h2,
:root[data-theme="dark"] .chartHeading h2,
:root[data-theme="dark"]
  .floatingTableCard h2 {
  color: #f5f7fa !important;
}


/* Tables */

:root[data-theme="dark"] .tableWrap,
:root[data-theme="dark"]
  .compactTableWrap {
  background: #0e1012 !important;

  border:
    1px solid
    #30353c !important;
}


:root[data-theme="dark"] table,
:root[data-theme="dark"] th,
:root[data-theme="dark"] td,
:root[data-theme="dark"] .floatingTable th,
:root[data-theme="dark"] .floatingTable td,
:root[data-theme="dark"]
  .floatingTable tbody th {
  color: #edf0f3 !important;
  background: #111416 !important;

  border-color:
    #2d3238 !important;
}


:root[data-theme="dark"] thead th,
:root[data-theme="dark"]
  .floatingTable thead th {
  color: #c9c3ff !important;
  background: #1c1f24 !important;
}


/* Production and Yield section headings */

:root[data-theme="dark"] .group th,
:root[data-theme="dark"]
  .floatingTable .group th {
  color: #ffffff !important;

  background:
    linear-gradient(
      90deg,
      #6356de,
      #7668ef
    ) !important;

  border-bottom: 0 !important;
}


/* Rejection section headings */

:root[data-theme="dark"]
  .group.rejectionGroup th,
:root[data-theme="dark"]
  .floatingTable .group.rejectionGroup th {
  color: #ffffff !important;

  background:
    linear-gradient(
      90deg,
      #d14352,
      #a6293a
    ) !important;
}


/* Table hover */

:root[data-theme="dark"]
  tbody tr:hover th,
:root[data-theme="dark"]
  tbody tr:hover td,
:root[data-theme="dark"]
  .floatingTable tbody tr:hover th,
:root[data-theme="dark"]
  .floatingTable tbody tr:hover td {
  background: #1a1e22 !important;
}


/* Good Cells */

:root[data-theme="dark"] .total th,
:root[data-theme="dark"] .total td,
:root[data-theme="dark"]
  .floatingTable .total th,
:root[data-theme="dark"]
  .floatingTable .total td {
  color: #5fe5a2 !important;
  background: #182a23 !important;
}


/* Wafer Loss */

:root[data-theme="dark"]
  .lossTotal th,
:root[data-theme="dark"]
  .lossTotal td,
:root[data-theme="dark"]
  .floatingTable .lossTotal th,
:root[data-theme="dark"]
  .floatingTable .lossTotal td {
  color: #ff7d89 !important;
  background: #311a1f !important;
}


/* Charts */

:root[data-theme="dark"]
  .yieldSubChart,
:root[data-theme="dark"]
  .yieldSubChartPrimary,
:root[data-theme="dark"]
  .yieldSubChartSecondary,
:root[data-theme="dark"]
  .yieldSubChartSmall {
  color: var(--theme-text);
  background: #131619 !important;

  border:
    1px solid
    #2d333a !important;
}


:root[data-theme="dark"]
  .yieldScaleLabel {
  color: #dde2e8 !important;
}


:root[data-theme="dark"]
  .recharts-cartesian-grid line {
  stroke: #2b3037 !important;
}


:root[data-theme="dark"]
  .recharts-cartesian-axis-line,
:root[data-theme="dark"]
  .recharts-cartesian-axis-tick-line {
  stroke: #4b535e !important;
}


:root[data-theme="dark"]
  .recharts-cartesian-axis-tick-value {
  fill: #aeb6c1 !important;
}


:root[data-theme="dark"]
  .recharts-legend-item-text {
  color: #dce1e7 !important;
}


:root[data-theme="dark"] .tooltip {
  color: #edf0f3 !important;
  background: #191c20 !important;

  border:
    1px solid
    #3a414a !important;

  box-shadow:
    0 14px 35px
    rgba(0, 0, 0, 0.55) !important;
}


:root[data-theme="dark"] .tooltip b {
  color: #ffffff !important;
}


/* Scrollbars */

:root[data-theme="dark"] {
  scrollbar-color:
    #555e69
    #111315;
}


:root[data-theme="dark"]
  ::-webkit-scrollbar {
  width: 11px;
  height: 11px;
}


:root[data-theme="dark"]
  ::-webkit-scrollbar-track {
  background: #111315;
}


:root[data-theme="dark"]
  ::-webkit-scrollbar-thumb {
  background: #4b535e;

  border:
    3px solid
    #111315;

  border-radius: 20px;
}


:root[data-theme="dark"]
  ::-webkit-scrollbar-thumb:hover {
  background: #626c78;
}
## SAP refresh

Copy your script to `backend/scripts/sap_refresh.vbs`. The script must accept the output data directory as its first argument. SAP GUI must be open, authenticated, and scripting-enabled. Only one refresh can run at a time.
