"""
app.py
======
Solar Cell Manufacturing Dashboard — entry point.

Architecture
------------
data_utils.py  Reading/mapping/cleaning the 5 Excel sources + derived metrics
charts.py      Reusable Plotly chart builders (one function per chart type)
styles.py      Dark-theme CSS + .streamlit/config.toml bootstrap
app.py (this)  Page layout only: sidebar nav, header, and 3 tab renderers
               (Overview / Production / Analytics)

Run:  streamlit run app.py
"""
import datetime as dt
import os

import pandas as pd
import streamlit as st

import charts as ch
import data_utils as du
import styles

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Solar Cell Manufacturing Dashboard", layout="wide",
                    initial_sidebar_state="expanded")
styles.write_theme_config(APP_DIR)
styles.inject_css()

if "tab" not in st.session_state:
    st.session_state.tab = "Overview"
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = dt.datetime.now()
if "clean_data" not in st.session_state:
    st.session_state.clean_data = {}


# ---------------------------------------------------------------------------
# Sidebar — brand + navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px;margin-bottom:18px;'>"
        "<div style='width:32px;height:32px;border-radius:50%;"
        "background:radial-gradient(circle at 35% 35%,#ffe07a,#f5a623 70%);'></div>"
        "<div><b style='font-size:13.5px;'>SOLAR CELL MFG</b><br>"
        "<span style='font-size:11px;color:#8a93ab;'>Production Dashboard</span></div></div>",
        unsafe_allow_html=True,
    )

    for tab_name in ("Overview", "Production", "Analytics"):
        active = st.session_state.tab == tab_name
        wrapper_class = "nav-active" if active else ""
        st.markdown(f"<div class='{wrapper_class}'>", unsafe_allow_html=True)
        if st.button(tab_name, key=f"nav_{tab_name}", use_container_width=True):
            st.session_state.tab = tab_name
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 📂 Data Source")
    data_dir = st.text_input("Folder with your .xlsx files", value=APP_DIR)
    uploaded = st.file_uploader("...or upload file(s) instead", type=["xlsx"], accept_multiple_files=True)
    use_sample = st.checkbox("Use bundled sample data", value=False)


# ---------------------------------------------------------------------------
# Data ingestion + column-mapping confirmation
# ---------------------------------------------------------------------------
def _ingest(sheets: dict):
    role_to_sheet = du.guess_sheet_roles(list(sheets.keys()))
    with st.sidebar.expander("🔧 Confirm sheet & column mapping"):
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
                for key, field_label, _patterns, required in schema:
                    guess = mapping.get(key)
                    opt_idx = cols.index(guess) if guess in cols else 0
                    star = "" if required else " (optional)"
                    sel = st.selectbox(f"{field_label}{star}", cols, index=opt_idx, key=f"col_{role}_{key}")
                    new_mapping[key] = None if sel == "-- none --" else sel
                clean = du.build_clean_df(df, new_mapping)
                st.session_state.clean_data[role] = clean
            else:
                st.session_state.clean_data.pop(role, None)
            st.divider()


if use_sample:
    sheets = du.load_all_sheets(os.path.join(APP_DIR, "sample_data.xlsx")) if os.path.exists(
        os.path.join(APP_DIR, "sample_data.xlsx")) else {}
    if os.path.exists(os.path.join(APP_DIR, "plan.xlsx")):
        sheets.update({f"plan.xlsx :: {k}": v for k, v in du.load_all_sheets(os.path.join(APP_DIR, "plan.xlsx")).items()})
    if not sheets:
        st.error("Bundled sample data not found next to app.py (sample_data.xlsx / plan.xlsx).")
        st.stop()
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
            "or check 'Use bundled sample data'.")
    st.stop()

day_nos = st.session_state.clean_data.get("day_nos")
month_nos = st.session_state.clean_data.get("month_nos")
day_mw = st.session_state.clean_data.get("day_mw")
month_mw = st.session_state.clean_data.get("month_mw")
plan_df = st.session_state.clean_data.get("plan")

if day_mw is None or day_mw.empty or day_nos is None or day_nos.empty:
    st.warning("Please map at least the 'Daywise MW report' and 'Day wise no. of cells produced' sheets "
               "in the sidebar to see the dashboard.")
    st.stop()

day_nos = du.add_efficiency_proxies(day_nos)
estimated_cols = day_nos.attrs.get("estimated_cols", [])


# ---------------------------------------------------------------------------
# Sidebar — Financial Year selector (depends on data being loaded)
# ---------------------------------------------------------------------------
asof = day_mw["period"].max()
min_date = min(day_mw["period"].min(), day_nos["period"].min())
available_fys = du.list_available_fys(min_date, asof)
fy_options = {du.fy_label(f): f for f in available_fys}
with st.sidebar:
    st.divider()
    st.markdown("#### 🗓️ Financial Year")
    fy_choice_label = st.selectbox("FY (Apr - Mar)", list(fy_options.keys()), index=0)
    fy_start = fy_options[fy_choice_label]
    fy_end = du.fy_bounds(fy_start)[1]

    st.markdown("#### 🎯 Plan Fallback")
    if plan_df is not None and not plan_df.empty and "total_target" in plan_df.columns:
        st.success(f"plan.xlsx loaded — {len(plan_df)} month(s) of targets.")
        manual_plan_override = st.number_input("Override current month's plan MW (0 = use plan.xlsx)", value=0.0, step=1.0)
    else:
        st.warning("No plan sheet mapped — using a manual monthly target.")
        manual_plan_override = st.number_input("Plan MW for current month", value=150.0, step=1.0)


def plan_for_month(month_start_ts: pd.Timestamp):
    if plan_df is None or plan_df.empty or "total_target" not in plan_df.columns:
        return None
    match = plan_df[(plan_df["period"].dt.year == month_start_ts.year) &
                     (plan_df["period"].dt.month == month_start_ts.month)]
    return float(match["total_target"].iloc[0]) if not match.empty else None


# ---------------------------------------------------------------------------
# Header (shared across tabs)
# ---------------------------------------------------------------------------
hc1, hc2 = st.columns([3, 1.4])
with hc1:
    st.markdown("## SOLAR CELL MANUFACTURING DASHBOARD")
    st.caption("Final Product · Real-Time Production Monitoring")
with hc2:
    b1, b2, b3 = st.columns(3)
    b1.markdown(f"<div class='as-of-badge' style='color:#e7ebf5;'>FY&nbsp;{fy_start.year}-{str(fy_end.year)[-2:]}</div>", unsafe_allow_html=True)
    b2.markdown(f"<div class='as-of-badge'>⟳ {st.session_state.last_refresh.strftime('%H:%M')}</div>", unsafe_allow_html=True)
    if b3.button("Refresh", use_container_width=True):
        st.session_state.last_refresh = dt.datetime.now()
        st.rerun()

st.divider()


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def period_sum(df, col, start, end_inclusive):
    m = (df["period"] >= start) & (df["period"] <= end_inclusive)
    return float(df.loc[m, col].sum()) if col in df.columns else None


def row_on_or_before(df, target_date):
    m = df["period"] <= target_date
    sub = df.loc[m]
    return sub.iloc[-1] if not sub.empty else None


def kpi_card(container, css_class, label, value, sub=None, delta_text=None, delta2=None, delta_dir="flat"):
    sub_html = f"<div class='sub'>{sub}</div>" if sub else ""
    delta_html = f"<div class='delta {delta_dir}'>{delta_text}</div>" if delta_text else ""
    delta2_html = f"<div class='delta2'>{delta2}</div>" if delta2 else ""
    container.markdown(
        f"<div class='kpi-card {css_class}'>"
        f"<div class='lbl'>{label}</div>{sub_html}"
        f"<div class='val'>{value}</div>{delta_html}{delta2_html}"
        f"</div>", unsafe_allow_html=True)


def aggregate_view(df, view, sum_cols, mean_cols=None):
    """Aggregate a period-indexed dataframe to Daily / Weekly / Monthly buckets."""
    mean_cols = mean_cols or []
    if view == "Daily" or df.empty:
        return df.copy()
    freq = "W-SUN" if view == "Weekly" else "MS"
    agg_dict = {c: "sum" for c in sum_cols if c in df.columns}
    agg_dict.update({c: "mean" for c in mean_cols if c in df.columns})
    out = df.set_index("period").resample(freq).agg(agg_dict).reset_index()
    return out


def period_label(ts, view):
    if view == "Daily":
        return ts.strftime("%d %b")
    if view == "Weekly":
        return "Wk " + ts.strftime("%d %b")
    return ts.strftime("%b %Y")


# =============================================================================
# OVERVIEW TAB — driven by the latest available date, not a range picker
# =============================================================================
def render_overview():
    st.markdown(f"<div class='as-of-badge'>AS OF: {asof.strftime('%d-%b-%Y')} "
                f"<span style='color:#8a93ab;font-weight:400;'>(latest available production date)</span></div>",
                unsafe_allow_html=True)

    # ---- KPI calculations -------------------------------------------------
    today_mw = period_sum(day_mw, "total_mw", asof, asof) or 0.0
    prev_day_row = row_on_or_before(day_mw, asof - pd.Timedelta(days=1))
    yday_mw = float(prev_day_row["total_mw"]) if prev_day_row is not None else None
    today_vs_yday_pct = ((today_mw - yday_mw) / yday_mw * 100) if yday_mw else None

    month_start = asof.replace(day=1)
    mtd_mw = period_sum(day_mw, "total_mw", month_start, asof) or 0.0
    prev_month_start = (month_start - pd.Timedelta(days=1)).replace(day=1)
    prev_mtd_end = prev_month_start + (asof - month_start)
    prev_mtd_mw = period_sum(day_mw, "total_mw", prev_month_start, prev_mtd_end) or 0.0
    mtd_delta_pct = ((mtd_mw - prev_mtd_mw) / prev_mtd_mw * 100) if prev_mtd_mw else None

    ytd_mw = period_sum(day_mw, "total_mw", fy_start, asof) or 0.0
    prev_fy_start = fy_start.replace(year=fy_start.year - 1)
    prev_fy_end = asof.replace(year=asof.year - 1)
    prev_ytd_mw = period_sum(day_mw, "total_mw", prev_fy_start, prev_fy_end) or 0.0
    ytd_delta_pct = ((ytd_mw - prev_ytd_mw) / prev_ytd_mw * 100) if prev_ytd_mw else None

    today_nos_row = row_on_or_before(day_nos, asof)
    yday_nos_row = row_on_or_before(day_nos, asof - pd.Timedelta(days=1))

    def row_yield(row):
        if row is None or row["total_prod"] == 0:
            return None
        return (1 - row["total_reject"] / row["total_prod"]) * 100

    def row_reject(row):
        if row is None or row["total_prod"] == 0:
            return None
        return row["total_reject"] / row["total_prod"] * 100

    today_yield = row_yield(today_nos_row)
    yday_yield = row_yield(yday_nos_row)
    yield_delta = (today_yield - yday_yield) if (today_yield is not None and yday_yield is not None) else None

    today_reject = row_reject(today_nos_row)
    last_month_row = row_on_or_before(day_nos, asof - pd.DateOffset(months=1))
    last_month_reject = row_reject(last_month_row)
    reject_delta = (today_reject - last_month_reject) if (today_reject is not None and last_month_reject is not None) else None

    n_days_mtd = day_mw[(day_mw["period"] >= month_start) & (day_mw["period"] <= asof)]["period"].nunique() or 1
    run_rate = mtd_mw / n_days_mtd

    month_plan = plan_for_month(month_start)
    if manual_plan_override > 0 or month_plan is None:
        month_plan = manual_plan_override if manual_plan_override > 0 else (month_plan or 150.0)
    days_in_month = pd.Period(asof, freq="M").days_in_month
    remaining_days = max(days_in_month - asof.day + 1, 1)
    required_rate = max(month_plan - mtd_mw, 0) / remaining_days
    plan_achv = (mtd_mw / month_plan * 100) if month_plan else 0.0

    # ---- KPI row 1 ----------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    today_diff = du.clean_zero(today_mw - (yday_mw or 0)) if yday_mw is not None else None
    mtd_diff = du.clean_zero(mtd_mw - prev_mtd_mw)
    ytd_diff = du.clean_zero(ytd_mw - prev_ytd_mw)
    yield_diff = du.clean_zero(yield_delta) if yield_delta is not None else None

    d, arrow = du.delta_arrow(today_vs_yday_pct)
    kpi_card(c1, "kpi-c1", f"Today's Production ({asof.strftime('%d-%b-%Y')})", du.fmt_mw(today_mw),
             delta_text=f"{arrow} {abs(today_vs_yday_pct):.2f}% vs Yesterday" if today_vs_yday_pct is not None else "vs Yesterday: N/A",
             delta2=f"({du.fmt_mw(yday_mw)}, {'+' if today_diff >= 0 else ''}{today_diff:.2f} MW)" if today_diff is not None else None,
             delta_dir=d)

    d, arrow = du.delta_arrow(mtd_delta_pct)
    kpi_card(c2, "kpi-c2", "MTD Production", du.fmt_mw(mtd_mw),
             sub=f"{month_start.strftime('%d-%b-%Y')} → {asof.strftime('%d-%b-%Y')}",
             delta_text=f"{arrow} {abs(mtd_delta_pct):.2f}% Previous MTD" if mtd_delta_pct is not None else "Previous MTD: N/A",
             delta2=f"({'+' if mtd_diff >= 0 else ''}{mtd_diff:.2f} MW)",
             delta_dir=d)

    d, arrow = du.delta_arrow(ytd_delta_pct)
    kpi_card(c3, "kpi-c1", "YTD Production", du.fmt_mw(ytd_mw),
             sub=f"{fy_start.strftime('%d-%b-%Y')} → {asof.strftime('%d-%b-%Y')}",
             delta_text=f"{arrow} {abs(ytd_delta_pct):.2f}% Previous FY YTD" if ytd_delta_pct is not None else "Previous FY YTD: N/A",
             delta2=f"({'+' if ytd_diff >= 0 else ''}{ytd_diff:.2f} MW)",
             delta_dir=d)

    d, arrow = du.delta_arrow(yield_delta)
    kpi_card(c4, "kpi-c2", "Yield %", du.fmt_pct(today_yield),
             delta_text=f"{arrow} {abs(yield_delta):.2f}% vs Yesterday" if yield_delta is not None else "vs Yesterday: N/A",
             delta2=f"({du.fmt_pct(yday_yield)}, {'+' if yield_diff is not None and yield_diff >= 0 else ''}{yield_diff:.2f}%)" if yield_diff is not None else None,
             delta_dir=d)

    # ---- KPI row 2 ----------------------------------------------------
    c5, c6, c7, c8 = st.columns(4)
    d, arrow = du.delta_arrow(reject_delta, good_when="down")
    reject_diff = du.clean_zero(reject_delta) if reject_delta is not None else None
    kpi_card(c5, "kpi-c5", "Reject %", du.fmt_pct(today_reject),
             delta_text=f"{arrow} {abs(reject_delta):.2f}% vs Last Month" if reject_delta is not None else "vs Last Month: N/A",
             delta2=f"({du.fmt_pct(last_month_reject)}, {'+' if reject_diff is not None and reject_diff >= 0 else ''}{reject_diff:.2f}%)" if reject_diff is not None else None,
             delta_dir=d)

    run_delta = run_rate - required_rate
    d, arrow = du.delta_arrow(run_delta)
    kpi_card(c6, "kpi-c6", "Run Rate", f"{run_rate:.2f} <span class='unit'>MW/day</span>",
             delta_text=f"{arrow} {abs(run_delta):.2f} MW/day vs Required" if True else "",
             delta2=f"({required_rate:.2f} MW/day)", delta_dir=d)

    kpi_card(c7, "kpi-c7", "Required Rate", f"{required_rate:.2f} <span class='unit'>MW/day</span>",
             delta2="to hit current plan")

    with c8:
        st.plotly_chart(ch.plan_achievement_gauge(plan_achv), use_container_width=True, config={"displayModeBar": False})
        st.markdown(f"<div style='text-align:center;font-size:11px;color:#8a93ab;margin-top:-10px;'>Plan Achievement — MTD vs plan target</div>", unsafe_allow_html=True)

    st.write("")

    # ---- Donuts ---------------------------------------------------------
    mtd_nos = day_nos[(day_nos["period"] >= month_start) & (day_nos["period"] <= asof)]
    mtd_mw_rows = day_mw[(day_mw["period"] >= month_start) & (day_mw["period"] <= asof)]

    g1, g2, g3 = st.columns(3)
    with g1:
        with st.container(border=True):
            st.markdown("**Grade Wise Production** <span style='color:#8a93ab;font-size:11px;'>Nos. — MTD</span>", unsafe_allow_html=True)
            labels = ["A Grade", "B Grade", "B-EL Grade", "EB Grade"]
            values = [float(mtd_nos["a_grade"].sum()), float(mtd_nos["b_grade"].sum()),
                      float(mtd_nos["bel"].sum()), float(mtd_nos["eb"].sum())]
            total_nos = sum(values)
            fig = ch.grade_donut(labels, values, ch.GRADE_COLORS, f"{total_nos:,.0f}", "Total Nos.")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with g2:
        with st.container(border=True):
            st.markdown("**Grade Wise Production** <span style='color:#8a93ab;font-size:11px;'>MW — MTD</span>", unsafe_allow_html=True)
            labels = ["A Grade", "B Grade", "BEL Grade", "EB Grade"]
            values = [float(mtd_mw_rows["a_mw"].sum()), float(mtd_mw_rows["b_mw"].sum()),
                      float(mtd_mw_rows["bel_mw"].sum()), float(mtd_mw_rows["eb_mw"].sum())]
            total_g_mw = sum(values)
            fig = ch.grade_donut(labels, values, ch.GRADE_COLORS, f"{total_g_mw:.2f}", "Total MW")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with g3:
        with st.container(border=True):
            st.markdown("**Breakage Split** <span style='color:#8a93ab;font-size:11px;'>MW & Cell Count — MTD</span>", unsafe_allow_html=True)
            brk_labels = ["B-W Breakage", "Cell Breakage", "R-W Breakage", "AL-W Breakage", "AG-W Breakage"]
            brk_cells = [float(mtd_nos[c].sum()) for c in ["blue", "cell_brk", "raw_wafer", "al", "ag"]]
            total_saleable_nos = float(mtd_mw_rows[["a_num", "b_num", "bel_num", "eb_num"]].sum().sum())
            watt_per_cell = (total_g_mw / total_saleable_nos) if total_saleable_nos else 0.0
            brk_mw = [c * watt_per_cell for c in brk_cells]
            fig = ch.breakage_donut(brk_labels, brk_mw, brk_cells, ch.BREAKAGE_COLORS, sum(brk_mw))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("MW estimated from cell counts using average watt/cell for the period.")

    # ---- Run Rate vs Required + MTD Summary -------------------------------
    rc1, rc2 = st.columns([1.6, 1])
    with rc1:
        with st.container(border=True):
            st.markdown("**Run Rate vs Required Rate** <span style='color:#8a93ab;font-size:11px;'>MW/day, MTD</span>", unsafe_allow_html=True)
            rr = mtd_mw_rows.copy()
            rr["cum_mw"] = rr["total_mw"].cumsum()
            rr["day_n"] = range(1, len(rr) + 1)
            rr["run_rate"] = rr["cum_mw"] / rr["day_n"]
            rr["required_rate"] = [(month_plan - rr["cum_mw"].iloc[max(i - 1, 0)]) / max(days_in_month - i, 1)
                                    if i > 0 else month_plan / days_in_month for i in range(len(rr))]
            fig = ch.run_rate_vs_required(rr["period"], rr["run_rate"], rr["required_rate"])
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with rc2:
        with st.container(border=True):
            st.markdown("**MTD Summary**")
            a_mw_mtd = float(mtd_mw_rows["a_mw"].sum())
            reject_mw_mtd = mtd_mw * (float(mtd_nos["total_reject"].sum()) / float(mtd_nos["total_prod"].sum())) if float(mtd_nos["total_prod"].sum()) else 0.0
            brk_mw_mtd = mtd_mw * (float(mtd_nos["total_brk"].sum()) / float(mtd_nos["total_prod"].sum())) if float(mtd_nos["total_prod"].sum()) else 0.0
            a_pct = (a_mw_mtd / mtd_mw * 100) if mtd_mw else 0.0
            reject_pct_mtd = (reject_mw_mtd / mtd_mw * 100) if mtd_mw else 0.0
            brk_pct_mtd = (brk_mw_mtd / mtd_mw * 100) if mtd_mw else 0.0
            mtd_yield = (1 - float(mtd_nos["total_reject"].sum()) / float(mtd_nos["total_prod"].sum())) * 100 if float(mtd_nos["total_prod"].sum()) else 0.0
            rows = [
                ("Total Production", du.fmt_mw(mtd_mw)),
                ("A Grade Production", f"{du.fmt_mw(a_mw_mtd)} ({a_pct:.2f}%)"),
                ("Total Rejection", f"{du.fmt_mw(reject_mw_mtd)} ({reject_pct_mtd:.2f}%)"),
                ("Total Breakage", f"{du.fmt_mw(brk_mw_mtd)} ({brk_pct_mtd:.2f}%)"),
                ("Yield %", du.fmt_pct(mtd_yield)),
                ("Plan Achievement", du.fmt_pct(plan_achv)),
            ]
            for lbl, val in rows:
                st.markdown(f"<div class='kv'><span>{lbl}</span><b>{val}</b></div>", unsafe_allow_html=True)

    # ---- Rejection Trend (SPC style, MTD) ----------------------------------
    with st.container(border=True):
        st.markdown("**Rejection Trend** <span style='color:#8a93ab;font-size:11px;'>FOR % · ER % · Breakage % — MTD, daily</span>", unsafe_allow_html=True)
        rt = mtd_nos.copy()
        denom = rt["total_prod"].replace(0, pd.NA)
        for_pct = (rt["fo_r"] / denom * 100).fillna(0)
        er_pct = (rt["er"] / denom * 100).fillna(0)
        brk_pct = (rt["total_brk"] / denom * 100).fillna(0)
        fig = ch.rejection_trend(rt["period"], for_pct, er_pct, brk_pct)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---- Monthly Performance Summary table ----------------------------------
    with st.container(border=True):
        st.markdown("**Monthly Performance Summary**")
        if month_mw is not None and not month_mw.empty:
            tbl = month_mw.copy()
            tbl = tbl[(tbl["period"] >= fy_start) & (tbl["period"] < fy_end)]
            tbl["Month"] = tbl["period"].dt.strftime("%b %Y")
            if plan_df is not None and not plan_df.empty and "total_target" in plan_df.columns:
                plan_lookup = plan_df.set_index(plan_df["period"].dt.to_period("M"))["total_target"]
                tbl["Plan MW"] = tbl["period"].dt.to_period("M").map(plan_lookup).fillna(manual_plan_override or 0.0)
            else:
                tbl["Plan MW"] = manual_plan_override or 150.0
            tbl["Actual MW"] = tbl["total_mw"]
            tbl["Achv %"] = (tbl["Actual MW"] / tbl["Plan MW"].replace(0, pd.NA) * 100)
            tbl["A Grade MW"] = tbl["a_mw"]
            tbl["A Grade %"] = (tbl["a_mw"] / tbl["total_mw"].replace(0, pd.NA) * 100)

            if month_nos is not None and not month_nos.empty:
                mn = month_nos.copy()
                mn["Month"] = mn["period"].dt.strftime("%b %Y")
                mn["Yield %"] = (1 - mn["total_reject"] / mn["total_prod"].replace(0, pd.NA)) * 100
                mn["Reject %"] = (mn["total_reject"] / mn["total_prod"].replace(0, pd.NA) * 100)
                mn["Breakage %"] = (mn["total_brk"] / mn["total_prod"].replace(0, pd.NA) * 100)
                tbl = tbl.merge(mn[["Month", "Yield %", "Reject %", "Breakage %"]], on="Month", how="left")

            days_per_month = tbl["period"].dt.days_in_month
            tbl["Run Rate"] = tbl["Actual MW"] / days_per_month
            tbl["Required Rate"] = tbl["Plan MW"] / days_per_month
            tbl["Status"] = tbl["Achv %"].apply(lambda v: "🟢" if v >= 95 else ("🟡" if v >= 80 else "🔴"))

            show_cols = ["Month", "Plan MW", "Actual MW", "Achv %", "A Grade MW", "A Grade %",
                         "Yield %", "Reject %", "Breakage %", "Run Rate", "Required Rate", "Status"]
            display = tbl[show_cols].copy()
            for c in display.columns:
                if c not in ("Month", "Status"):
                    display[c] = display[c].round(2)
            st.dataframe(display, use_container_width=True, hide_index=True)
        else:
            st.info("Map the Monthwise MW report sheet to see the monthly summary table.")

    if estimated_cols:
        st.caption(f"Note: {', '.join(estimated_cols)} not found in your data — estimated from breakage/rejection "
                   "ratios. Map real SAP/Tester efficiency columns in the sidebar for exact values.")


# =============================================================================
# PRODUCTION TAB — date range + Daily/Weekly/Monthly view
# =============================================================================
def render_production():
    with st.container(border=True):
        f1, f2, f3, f4 = st.columns([1, 1, 1, 2])
        start_default = max(fy_start, min_date).date()
        with f1:
            start_d = st.date_input("From", value=start_default, min_value=min_date.date(), max_value=asof.date())
        with f2:
            end_d = st.date_input("To", value=asof.date(), min_value=min_date.date(), max_value=asof.date())
        with f3:
            st.markdown("<div style='height:1.6rem;'></div>", unsafe_allow_html=True)
            apply_clicked = st.button("Apply Range", use_container_width=True)
        with f4:
            view = st.radio("View", ["Daily", "Weekly", "Monthly"], horizontal=True, key="prod_view")

    start_ts, end_ts = pd.Timestamp(start_d), pd.Timestamp(end_d)
    d_nos = day_nos[(day_nos["period"] >= start_ts) & (day_nos["period"] <= end_ts)].copy()
    d_mw = day_mw[(day_mw["period"] >= start_ts) & (day_mw["period"] <= end_ts)].copy()

    if d_nos.empty or d_mw.empty:
        st.warning("No data in the selected date range.")
        return

    nos_sum_cols = ["a_grade", "b_grade", "bel", "eb", "total_prod", "er", "fo_r", "er_q",
                     "total_reject", "raw_wafer", "blue", "al", "ag", "cell_brk", "total_brk"]
    mw_sum_cols = ["a_num", "b_num", "bel_num", "eb_num", "a_mw", "b_mw", "bel_mw", "eb_mw", "total_mw"]

    agg_nos = aggregate_view(d_nos, view, nos_sum_cols, mean_cols=["sap_efficiency", "tester_efficiency"])
    agg_mw = aggregate_view(d_mw, view, mw_sum_cols)

    # ---- Daily Production Trend (combo) + Daily Efficiency Trend ----------
    with st.container(border=True):
        st.markdown(f"**Daily Production Trend** <span style='color:#8a93ab;font-size:11px;'>Good Cells (Nos., bars) vs Overall MW & A Grade MW (lines) — {view}</span>", unsafe_allow_html=True)
        fig = ch.daily_production_combo(agg_nos["period"], agg_nos["total_prod"], agg_mw["total_mw"], agg_mw["a_mw"])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with st.container(border=True):
        st.markdown(f"**Daily Efficiency Trend** <span style='color:#8a93ab;font-size:11px;'>SAP Efficiency (Bin Loss) vs Tester Efficiency (Halm) — {view}</span>", unsafe_allow_html=True)
        fig = ch.efficiency_trend(agg_nos["period"], agg_nos["sap_efficiency"], agg_nos["tester_efficiency"])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        if estimated_cols:
            st.caption("Efficiency values are estimated proxies (see note at the bottom of the Overview tab).")

    # ---- Yield Trend + Rejection Trend --------------------------------------
    p1, p2 = st.columns(2)
    with p1:
        with st.container(border=True):
            st.markdown(f"**Yield Trend** <span style='color:#8a93ab;font-size:11px;'>% — {view}</span>", unsafe_allow_html=True)
            denom = agg_nos["total_prod"].replace(0, pd.NA)
            yld = ((1 - agg_nos["total_reject"] / denom) * 100).fillna(0)
            fig = ch.yield_trend(agg_nos["period"], yld)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with p2:
        with st.container(border=True):
            st.markdown(f"**Rejection Trend** <span style='color:#8a93ab;font-size:11px;'>FOR % · ER % · Breakage % — {view}</span>", unsafe_allow_html=True)
            denom = agg_nos["total_prod"].replace(0, pd.NA)
            for_pct = (agg_nos["fo_r"] / denom * 100).fillna(0)
            er_pct = (agg_nos["er"] / denom * 100).fillna(0)
            brk_pct = (agg_nos["total_brk"] / denom * 100).fillna(0)
            fig = ch.rejection_trend(agg_nos["period"], for_pct, er_pct, brk_pct)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ---- Plan vs Actual -------------------------------------------------
    with st.container(border=True):
        st.markdown(f"**Plan vs Actual** <span style='color:#8a93ab;font-size:11px;'>MW — {view}</span>", unsafe_allow_html=True)
        if plan_df is not None and not plan_df.empty and "total_target" in plan_df.columns:
            daily_plan = d_mw[["period"]].copy()
            month_days = d_mw["period"].dt.to_period("M").dt.to_timestamp().dt.days_in_month
            plan_lookup = plan_df.set_index(plan_df["period"].dt.to_period("M"))["total_target"]
            monthly_target = d_mw["period"].dt.to_period("M").map(plan_lookup).fillna(manual_plan_override or 0.0)
            daily_plan["plan_mw"] = monthly_target.values / month_days.values
            agg_plan = aggregate_view(daily_plan, view, ["plan_mw"])
            plan_series = agg_plan["plan_mw"]
        else:
            n_periods = len(agg_mw)
            plan_series = pd.Series([(manual_plan_override or 150.0) / max(n_periods, 1)] * n_periods)

        labels = [period_label(p, view) for p in agg_mw["period"]]
        fig = ch.plan_vs_actual(labels, plan_series.values, agg_mw["total_mw"].values)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# =============================================================================
# ANALYTICS TAB — date range + view selector; Breakage Pareto + Rejection Heatmap
# =============================================================================
def render_analytics():
    with st.container(border=True):
        f1, f2, f3, f4 = st.columns([1, 1, 1, 2])
        start_default = max(fy_start, min_date).date()
        with f1:
            start_d = st.date_input("From", value=start_default, min_value=min_date.date(), max_value=asof.date(), key="an_start")
        with f2:
            end_d = st.date_input("To", value=asof.date(), min_value=min_date.date(), max_value=asof.date(), key="an_end")
        with f3:
            st.markdown("<div style='height:1.6rem;'></div>", unsafe_allow_html=True)
            st.button("Apply Range", use_container_width=True, key="an_apply")
        with f4:
            view = st.radio("View", ["Daily", "Weekly", "Monthly"], horizontal=True, key="an_view")

    start_ts, end_ts = pd.Timestamp(start_d), pd.Timestamp(end_d)
    d_nos = day_nos[(day_nos["period"] >= start_ts) & (day_nos["period"] <= end_ts)].copy()
    d_mw = day_mw[(day_mw["period"] >= start_ts) & (day_mw["period"] <= end_ts)].copy()

    if d_nos.empty:
        st.warning("No data in the selected date range.")
        return

    a1, a2 = st.columns(2)
    with a1:
        with st.container(border=True):
            st.markdown("**Breakage Pareto** <span style='color:#8a93ab;font-size:11px;'>MW & % of total, sorted descending</span>", unsafe_allow_html=True)
            labels = ["B-W Breakage", "Cell Breakage", "R-W Breakage", "AL-W Breakage", "AG-W Breakage"]
            cells = [float(d_nos[c].sum()) for c in ["blue", "cell_brk", "raw_wafer", "al", "ag"]]
            total_saleable = float(d_mw[["a_num", "b_num", "bel_num", "eb_num"]].sum().sum())
            total_mw_range = float(d_mw["total_mw"].sum())
            watt_per_cell = (total_mw_range / total_saleable) if total_saleable else 0.0
            mw_values = [c * watt_per_cell for c in cells]
            fig = ch.breakage_pareto(labels, mw_values)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("MW estimated from cell counts using average watt/cell for the period. "
                       "Reflects totals over the selected range (the view selector doesn't re-bucket this chart).")

    with a2:
        with st.container(border=True):
            st.markdown("**Rejection Heatmap** <span style='color:#8a93ab;font-size:11px;'>MW by day of week</span>", unsafe_allow_html=True)
            hm = d_nos.copy()
            denom_total = float(hm["total_prod"].sum())
            wpc = (total_mw_range / total_saleable) if total_saleable else 0.0
            hm["reject_mw"] = hm["total_reject"] * wpc
            hm["dow"] = hm["period"].dt.day_name().str[:3]
            hm["week"] = hm["period"].dt.isocalendar().week
            pivot = hm.pivot_table(index="week", columns="dow", values="reject_mw", aggfunc="sum")
            dow_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            pivot = pivot.reindex(columns=[d for d in dow_order if d in pivot.columns])
            week_labels = [f"Wk{w}" for w in pivot.index]
            fig = ch.rejection_heatmap(week_labels, list(pivot.columns), pivot.values)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("Always shown at daily granularity, grouped by ISO week (the view selector doesn't re-bucket this chart).")


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------
if st.session_state.tab == "Overview":
    render_overview()
elif st.session_state.tab == "Production":
    render_production()
else:
    render_analytics()

st.caption("All figures shown to 2 decimal places. Source: uploaded/local Excel file(s).")
