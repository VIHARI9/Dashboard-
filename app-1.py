"""
Solar Cell Manufacturing Dashboard
Run with:  streamlit run app.py
"""
import datetime as dt
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import data_utils as du

APP_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="Solar Cell Manufacturing Dashboard", layout="wide")

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
DARK_BG = "#0e1526"
CARD_BG = "#151d33"
PLOT_TEMPLATE = "plotly_dark"
GRADE_COLORS = {"A Grade": "#2f6fed", "B Grade": "#22c55e", "B-EL Grade": "#f59e0b", "EB Grade": "#a855f7"}

st.markdown(f"""
<style>
.stApp {{ background-color: {DARK_BG}; }}
div[data-testid="stMetric"], .kpi-card {{
    background-color: {CARD_BG};
    border-radius: 10px;
    padding: 14px 16px;
}}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar — data source
# ---------------------------------------------------------------------------
st.sidebar.header("📂 Data Source")
data_dir = st.sidebar.text_input(
    "Folder containing your .xlsx files",
    value=APP_DIR,
    help="All .xlsx files in this folder are scanned (e.g. day-wise, month-wise, "
         "MW reports, plan.xlsx). Defaults to the folder app.py is running from.",
)
uploaded = st.sidebar.file_uploader(
    "...or upload file(s) instead", type=["xlsx"], accept_multiple_files=True,
)
use_sample = st.sidebar.checkbox("Use bundled sample data instead", value=False)

if "clean_data" not in st.session_state:
    st.session_state.clean_data = {}


def _ingest(sheets: dict):
    """Given {sheet_name: df}, guess roles, auto-map columns, let user confirm, store clean dfs."""
    role_to_sheet = du.guess_sheet_roles(list(sheets.keys()))
    with st.sidebar.expander("🔧 Confirm sheet & column mapping", expanded=False):
        for role, label in du.ROLE_LABELS.items():
            st.markdown(f"**{label}**")
            options = ["-- none --"] + list(sheets.keys())
            default = role_to_sheet.get(role, "-- none --")
            idx = options.index(default) if default in options else 0
            chosen = st.selectbox(f"Sheet for: {label}", options, index=idx, key=f"sheet_{role}")
            if chosen != "-- none --":
                df = sheets[chosen]
                schema = du.ROLE_SCHEMAS[role]
                mapping = du.auto_map_columns(df, schema)
                cols = ["-- none --"] + list(df.columns)
                new_mapping = {}
                for key, field_label, _ in schema:
                    guess = mapping.get(key)
                    opt_idx = cols.index(guess) if guess in cols else 0
                    sel = st.selectbox(field_label, cols, index=opt_idx, key=f"col_{role}_{key}")
                    new_mapping[key] = None if sel == "-- none --" else sel
                clean = du.build_clean_df(df, new_mapping, "month" in role)
                st.session_state.clean_data[role] = clean
            else:
                st.session_state.clean_data.pop(role, None)
            st.divider()


if use_sample:
    sheets = du.load_all_sheets("sample_data.xlsx")
    _ingest(sheets)
elif uploaded:
    sheets = {}
    for f in uploaded:
        sheets.update({f"{f.name} :: {k}": v for k, v in du.load_all_sheets(f).items()})
    _ingest(sheets)
elif data_dir and os.path.isdir(data_dir):
    sheets = du.load_dir(data_dir)
    if not sheets:
        st.warning(f"No .xlsx files found in `{data_dir}`.")
        st.stop()
    _ingest(sheets)
else:
    st.info(f"`{data_dir}` isn't a valid folder. Fix the path in the sidebar, upload files instead, "
            "or check 'Use bundled sample data' to preview the dashboard.")
    st.stop()

day_nos = st.session_state.clean_data.get("day_nos")
month_nos = st.session_state.clean_data.get("month_nos")
day_mw = st.session_state.clean_data.get("day_mw")
month_mw = st.session_state.clean_data.get("month_mw")
plan_df = st.session_state.clean_data.get("plan")

if day_mw is None or day_mw.empty:
    st.warning("Please map at least the 'Daywise MW report' sheet to see the dashboard.")
    st.stop()


# ---------------------------------------------------------------------------
# Sidebar — filters
# ---------------------------------------------------------------------------
st.sidebar.header("🗓️ Filters")
min_d, max_d = day_mw["period"].min().date(), day_mw["period"].max().date()
date_range = st.sidebar.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_d, max_d

st.sidebar.header("🎯 Monthly Target (Plan)")
if plan_df is not None and not plan_df.empty and "total_target" in plan_df.columns:
    st.sidebar.success(f"Loaded plan.xlsx — {len(plan_df)} month(s) of targets.")
    manual_plan_override = st.sidebar.number_input(
        "Override current month's plan MW (0 = use plan.xlsx)", value=0.0, step=1.0)
else:
    st.sidebar.warning("No plan sheet mapped — enter a plan target manually below.")
    manual_plan_override = st.sidebar.number_input(
        "Plan MW for current month", value=150.0, step=1.0)
required_rate = st.sidebar.number_input("Required run rate override (MW/day, 0=auto)", value=0.0, step=0.1)


def plan_for_month(month_start_ts: pd.Timestamp) -> float | None:
    """Look up total_target MW for the given month from plan.xlsx, if available."""
    if plan_df is None or plan_df.empty or "total_target" not in plan_df.columns:
        return None
    match = plan_df[(plan_df["period"].dt.year == month_start_ts.year) &
                     (plan_df["period"].dt.month == month_start_ts.month)]
    if match.empty:
        return None
    return float(match["total_target"].iloc[0])

mask = (day_mw["period"].dt.date >= start_d) & (day_mw["period"].dt.date <= end_d)
d_mw = day_mw.loc[mask].copy()
d_nos = day_nos.loc[(day_nos["period"].dt.date >= start_d) & (day_nos["period"].dt.date <= end_d)].copy() if day_nos is not None else None

if d_mw.empty:
    st.warning("No data in the selected date range.")
    st.stop()


# ---------------------------------------------------------------------------
# KPI calculations
# ---------------------------------------------------------------------------
latest_date = d_mw["period"].max()
today_row = d_mw[d_mw["period"] == latest_date]
today_mw = float(today_row["total_mw"].sum())

prior_day = d_mw[d_mw["period"] < latest_date]
yesterday_mw = float(prior_day["total_mw"].iloc[-1]) if not prior_day.empty else None
today_vs_yday = ((today_mw - yesterday_mw) / yesterday_mw * 100) if yesterday_mw else None

month_start = latest_date.replace(day=1)
mtd = d_mw[(d_mw["period"] >= month_start) & (d_mw["period"] <= latest_date)]
mtd_mw = float(mtd["total_mw"].sum())

prev_month_end = month_start - pd.Timedelta(days=1)
prev_month_start = prev_month_end.replace(day=1)
same_day_prev_month = prev_month_start + (latest_date - month_start)
prev_mtd = day_mw[(day_mw["period"] >= prev_month_start) & (day_mw["period"] <= same_day_prev_month)]
prev_mtd_mw = float(prev_mtd["total_mw"].sum())
mtd_vs_lastmonth = ((mtd_mw - prev_mtd_mw) / prev_mtd_mw * 100) if prev_mtd_mw else None

year_start = latest_date.replace(month=1, day=1)
ytd = day_mw[(day_mw["period"] >= year_start) & (day_mw["period"] <= latest_date)]
ytd_mw = float(ytd["total_mw"].sum())
prev_year_start = year_start.replace(year=year_start.year - 1)
prev_year_end = latest_date.replace(year=latest_date.year - 1)
ytd_prev = day_mw[(day_mw["period"] >= prev_year_start) & (day_mw["period"] <= prev_year_end)]
ytd_prev_mw = float(ytd_prev["total_mw"].sum())
ytd_vs_lastyear = ((ytd_mw - ytd_prev_mw) / ytd_prev_mw * 100) if ytd_prev_mw else None

a_saleable = float(mtd["a_num"].sum()) if "a_num" in mtd.columns else 0
total_nos_mtd = None
reject_pct = None
if d_nos is not None and not d_nos.empty:
    nos_mtd = d_nos[(d_nos["period"] >= month_start) & (d_nos["period"] <= latest_date)]
    total_produced = float(nos_mtd["total_prod"].sum()) if "total_prod" in nos_mtd.columns else None
    total_rejected = float(nos_mtd["total_reject"].sum()) if "total_reject" in nos_mtd.columns else None
    if total_produced:
        yield_pct = (1 - (total_rejected or 0) / total_produced) * 100 if total_produced else None
        reject_pct = (total_rejected / total_produced * 100) if total_produced else None
    else:
        yield_pct = None
else:
    yield_pct = None

n_days_mtd = mtd["period"].nunique() or 1
run_rate = mtd_mw / n_days_mtd

monthly_plan_mw = plan_for_month(month_start)
if manual_plan_override > 0 or monthly_plan_mw is None:
    monthly_plan_mw = manual_plan_override if manual_plan_override > 0 else (monthly_plan_mw or 150.0)

if required_rate <= 0:
    days_in_month = pd.Period(latest_date, freq="M").days_in_month
    remaining_days = max(days_in_month - latest_date.day + 1, 1)
    remaining_target = max(monthly_plan_mw - mtd_mw, 0)
    required_rate_calc = remaining_target / remaining_days
else:
    required_rate_calc = required_rate
plan_achv = (mtd_mw / monthly_plan_mw * 100) if monthly_plan_mw else None


def fmt_delta(v, suffix="%"):
    if v is None:
        return ""
    arrow = "▲" if v >= 0 else "▼"
    return f"{arrow} {abs(v):.2f}{suffix}"


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown("## ☀️ SOLAR CELL MANUFACTURING DASHBOARD")
    st.caption(f"Final Product | Real Time Production Monitoring — as of {latest_date.strftime('%d %b %Y')}")
with c2:
    st.metric("Last Refresh", dt.datetime.now().strftime("%H:%M"))

# ---------------------------------------------------------------------------
# KPI Row
# ---------------------------------------------------------------------------
k = st.columns(8)
k[0].metric("Today's Production", f"{today_mw:.2f} MW", fmt_delta(today_vs_yday) + " vs Yesterday" if today_vs_yday is not None else "vs Yesterday")
k[1].metric("MTD Production", f"{mtd_mw:.2f} MW", fmt_delta(mtd_vs_lastmonth) + " vs Last Month" if mtd_vs_lastmonth is not None else "vs Last Month")
k[2].metric("YTD Production", f"{ytd_mw:.2f} MW", fmt_delta(ytd_vs_lastyear) + " vs Last Year" if ytd_vs_lastyear is not None else "vs Last Year")
k[3].metric("Yield %", f"{yield_pct:.2f}%" if yield_pct is not None else "N/A")
k[4].metric("Reject %", f"{reject_pct:.2f}%" if reject_pct is not None else "N/A")
k[5].metric("Run Rate", f"{run_rate:.2f} MW/day")
k[6].metric("Required Rate", f"{required_rate_calc:.2f} MW/day")
k[7].metric("Plan Achievement", f"{plan_achv:.2f}%" if plan_achv is not None else "N/A")

st.divider()

# ---------------------------------------------------------------------------
# Row 2: Grade-wise donuts + Daily trend
# ---------------------------------------------------------------------------
GRADE_KEYS_MW = [("a_mw", "A Grade"), ("b_mw", "B Grade"), ("bel_mw", "BEL Grade"), ("eb_mw", "EB Grade")]
GRADE_KEYS_NOS = [("a_num", "A Grade"), ("b_num", "B Grade"), ("bel_num", "BEL Grade"), ("eb_num", "EB Grade")]

r2c1, r2c2, r2c3 = st.columns([1, 1, 1.3])

with r2c1:
    st.markdown("#### Grade Wise Production (Nos.)")
    vals = [float(mtd[k_].sum()) for k_, _ in GRADE_KEYS_NOS if k_ in mtd.columns]
    labels = [lbl for k_, lbl in GRADE_KEYS_NOS if k_ in mtd.columns]
    fig = go.Figure(go.Pie(labels=labels, values=vals, hole=0.65,
                            marker=dict(colors=[GRADE_COLORS.get(l, "#888") for l in labels])))
    fig.update_layout(template=PLOT_TEMPLATE, showlegend=True, height=320,
                       annotations=[dict(text=f"Total<br><b>{sum(vals):,.0f}</b><br>Nos.", showarrow=False, font_size=14)])
    st.plotly_chart(fig, use_container_width=True)

with r2c2:
    st.markdown("#### Grade Wise Production (MW)")
    vals = [float(mtd[k_].sum()) for k_, _ in GRADE_KEYS_MW if k_ in mtd.columns]
    labels = [lbl for k_, lbl in GRADE_KEYS_MW if k_ in mtd.columns]
    fig = go.Figure(go.Pie(labels=labels, values=vals, hole=0.65,
                            marker=dict(colors=[GRADE_COLORS.get(l, "#888") for l in labels])))
    fig.update_layout(template=PLOT_TEMPLATE, showlegend=True, height=320,
                       annotations=[dict(text=f"Total<br><b>{sum(vals):,.2f}</b><br>MW", showarrow=False, font_size=14)])
    st.plotly_chart(fig, use_container_width=True)

with r2c3:
    st.markdown("#### Daily Production Trend (MW)")
    fig = go.Figure(go.Scatter(x=d_mw["period"], y=d_mw["total_mw"], mode="lines+markers",
                                line=dict(color="#2f6fed"), fill="tozeroy"))
    fig.update_layout(template=PLOT_TEMPLATE, height=320, margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Row 3: Plan vs Actual, Run Rate vs Required, MTD Summary
# ---------------------------------------------------------------------------
r3c1, r3c2, r3c3 = st.columns([1.3, 1.3, 1])

with r3c1:
    st.markdown("#### Plan vs Actual (Monthly)")
    if month_mw is not None and not month_mw.empty:
        mm = month_mw.copy()
        mm["month_label"] = mm["period"].dt.strftime("%b")
        if plan_df is not None and not plan_df.empty and "total_target" in plan_df.columns:
            plan_lookup = plan_df.set_index(plan_df["period"].dt.to_period("M"))["total_target"]
            mm["plan_mw"] = mm["period"].dt.to_period("M").map(plan_lookup)
            mm["plan_mw"] = mm["plan_mw"].fillna(monthly_plan_mw)
        else:
            mm["plan_mw"] = monthly_plan_mw
        fig = go.Figure()
        fig.add_bar(x=mm["month_label"], y=mm["plan_mw"], name="Plan MW", marker_color="#8892b0")
        fig.add_bar(x=mm["month_label"], y=mm["total_mw"], name="Actual MW", marker_color="#2f6fed")
        fig.update_layout(template=PLOT_TEMPLATE, barmode="group", height=300, legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Map the Monthwise MW report sheet to see this chart.")

with r3c2:
    st.markdown("#### Run Rate vs Required Rate (MW/day)")
    daily_run = d_mw.set_index("period")["total_mw"].rename("Run Rate")
    fig = go.Figure()
    fig.add_scatter(x=daily_run.index, y=daily_run.values, mode="lines+markers", name="Run Rate", line=dict(color="#22c55e"))
    fig.add_scatter(x=daily_run.index, y=[required_rate_calc] * len(daily_run), mode="lines", name="Required Rate", line=dict(color="#f59e0b", dash="dot"))
    fig.update_layout(template=PLOT_TEMPLATE, height=300, legend=dict(orientation="h", y=1.15))
    st.plotly_chart(fig, use_container_width=True)

with r3c3:
    st.markdown("#### MTD Summary")
    a_pct = (float(mtd["a_mw"].sum()) / mtd_mw * 100) if mtd_mw else 0
    st.write(f"**Total Production:** {mtd_mw:.2f} MW")
    st.write(f"**A Grade Production:** {float(mtd['a_mw'].sum()):.2f} MW ({a_pct:.1f}%)")
    if d_nos is not None and not d_nos.empty and "total_reject" in nos_mtd.columns:
        st.write(f"**Total Rejection:** {float(nos_mtd['total_reject'].sum()):,.0f} cells")
    if d_nos is not None and not d_nos.empty and "total_brk" in nos_mtd.columns:
        st.write(f"**Total Breakage:** {float(nos_mtd['total_brk'].sum()):,.0f} cells")
    st.write(f"**Yield %:** {yield_pct:.2f}%" if yield_pct is not None else "**Yield %:** N/A")
    st.write(f"**Plan Achievement:** {plan_achv:.2f}%" if plan_achv is not None else "**Plan Achievement:** N/A")

    if plan_df is not None and not plan_df.empty:
        plan_row = plan_df[(plan_df["period"].dt.year == month_start.year) &
                            (plan_df["period"].dt.month == month_start.month)]
        if not plan_row.empty:
            st.markdown("**Grade-wise Plan Achievement:**")
            for grade_key, target_key, label in [("a_mw", "a_target", "A Grade"),
                                                   ("b_mw", "b_target", "B Grade"),
                                                   ("bel_mw", "bel_target", "BEL Grade")]:
                if target_key in plan_row.columns and grade_key in mtd.columns:
                    target = float(plan_row[target_key].iloc[0])
                    actual = float(mtd[grade_key].sum())
                    achv = (actual / target * 100) if target else None
                    st.write(f"- {label}: {actual:.2f} / {target:.2f} MW ({achv:.1f}%)" if achv is not None else f"- {label}: {actual:.2f} MW")

st.divider()

# ---------------------------------------------------------------------------
# Row 4: Yield trend, Rejection trend, Breakage pareto, Heatmap
# ---------------------------------------------------------------------------
r4c1, r4c2, r4c3, r4c4 = st.columns(4)

with r4c1:
    st.markdown("#### Yield Trend (%)")
    if d_nos is not None and not d_nos.empty:
        tmp = d_nos.copy()
        for grade_key, rej_share in [("a_grade", None)]:
            pass
        tmp["yield_pct"] = (1 - tmp["total_reject"] / tmp["total_prod"].replace(0, pd.NA)) * 100
        fig = go.Figure(go.Scatter(x=tmp["period"], y=tmp["yield_pct"], mode="lines", line=dict(color="#22d3ee")))
        fig.update_layout(template=PLOT_TEMPLATE, height=280)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Map the Day wise nos sheet to see yield trend.")

with r4c2:
    st.markdown("#### Rejection Trend (MW / Nos)")
    if d_nos is not None and not d_nos.empty:
        fig = go.Figure()
        fig.add_scatter(x=d_nos["period"], y=d_nos["er"], stackgroup="one", name="ER", line=dict(color="#ef4444"))
        fig.add_scatter(x=d_nos["period"], y=d_nos["fo_r"], stackgroup="one", name="FOR", line=dict(color="#f97316"))
        fig.add_scatter(x=d_nos["period"], y=d_nos["er_q"], stackgroup="one", name="ER(Q)", line=dict(color="#a855f7"))
        fig.update_layout(template=PLOT_TEMPLATE, height=280, legend=dict(orientation="h", y=1.15))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Map the Day wise nos sheet to see rejection trend.")

with r4c3:
    st.markdown("#### Breakage Pareto")
    if d_nos is not None and not d_nos.empty:
        brk_cols = [("raw_wafer", "Raw Wafer"), ("blue", "Blue"), ("al", "Al"), ("ag", "Ag"), ("cell_brk", "Cell")]
        sums = [(lbl, float(d_nos[k_].sum())) for k_, lbl in brk_cols if k_ in d_nos.columns]
        sums.sort(key=lambda x: -x[1])
        labels = [s[0] for s in sums]
        vals = [s[1] for s in sums]
        fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h", marker_color="#2f6fed"))
        fig.update_layout(template=PLOT_TEMPLATE, height=280, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Map the Day wise nos sheet to see breakage pareto.")

with r4c4:
    st.markdown("#### Rejection Heatmap")
    if d_nos is not None and not d_nos.empty:
        tmp = d_nos.copy()
        tmp["dow"] = tmp["period"].dt.day_name().str[:3]
        tmp["week"] = tmp["period"].dt.isocalendar().week
        pivot = tmp.pivot_table(index="week", columns="dow", values="total_reject", aggfunc="sum")
        dow_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        pivot = pivot.reindex(columns=[d for d in dow_order if d in pivot.columns])
        fig = go.Figure(go.Heatmap(z=pivot.values, x=pivot.columns, y=[f"Wk{w}" for w in pivot.index],
                                    colorscale=[[0, "#22c55e"], [0.5, "#f59e0b"], [1, "#ef4444"]]))
        fig.update_layout(template=PLOT_TEMPLATE, height=280)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Map the Day wise nos sheet to see the heatmap.")

st.divider()

# ---------------------------------------------------------------------------
# Row 5: Monthly performance summary table
# ---------------------------------------------------------------------------
st.markdown("#### Monthly Performance Summary")
if month_mw is not None and not month_mw.empty:
    tbl = month_mw.copy()
    tbl["Month"] = tbl["period"].dt.strftime("%b-%Y")
    if plan_df is not None and not plan_df.empty and "total_target" in plan_df.columns:
        plan_lookup = plan_df.set_index(plan_df["period"].dt.to_period("M"))["total_target"]
        tbl["Plan MW"] = tbl["period"].dt.to_period("M").map(plan_lookup).fillna(monthly_plan_mw)
    else:
        tbl["Plan MW"] = monthly_plan_mw
    tbl["Actual MW"] = tbl["total_mw"]
    tbl["Achv %"] = (tbl["Actual MW"] / tbl["Plan MW"] * 100).round(2)
    tbl["A Grade MW"] = tbl["a_mw"]
    tbl["A Grade %"] = (tbl["a_mw"] / tbl["total_mw"] * 100).round(2)

    if month_nos is not None and not month_nos.empty:
        mn = month_nos.copy()
        mn["Month"] = mn["period"].dt.strftime("%b-%Y")
        mn["Yield %"] = ((1 - mn["total_reject"] / mn["total_prod"].replace(0, pd.NA)) * 100).round(2)
        mn["Reject %"] = ((mn["total_reject"] / mn["total_prod"].replace(0, pd.NA)) * 100).round(2)
        mn["Breakage %"] = ((mn["total_brk"] / mn["total_prod"].replace(0, pd.NA)) * 100).round(2)
        tbl = tbl.merge(mn[["Month", "Yield %", "Reject %", "Breakage %"]], on="Month", how="left")

    n_days_per_month = month_mw["period"].dt.days_in_month if "period" in month_mw else 30
    tbl["Run Rate (MW/day)"] = (tbl["Actual MW"] / n_days_per_month).round(2)
    tbl["Required Rate (MW/day)"] = (tbl["Plan MW"] / n_days_per_month).round(2)

    display_cols = ["Month", "Plan MW", "Actual MW", "Achv %", "A Grade MW", "A Grade %",
                     "Yield %", "Reject %", "Breakage %", "Run Rate (MW/day)", "Required Rate (MW/day)"]
    display_cols = [c for c in display_cols if c in tbl.columns]
    st.dataframe(tbl[display_cols].round(2), use_container_width=True, hide_index=True)
else:
    st.info("Map the Monthwise MW report sheet to see the monthly summary table.")

st.caption("All values are in MW unless specified | Source: uploaded Excel file(s)")
