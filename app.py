from pathlib import Path
import datetime as dt
import subprocess
import sys
import time

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from charts import COL, donut, lines, pareto, production, run_rate_chart, ticks
from components import empty, kpi
from data_loader import load_all
from metrics import delta, fy_start, plan_for, previous_row, safe_sum
from styles import CSS
from validation import validate_dataset


st.set_page_config(
    page_title="Solar Cell Manufacturing Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(r"C:\Users\vijaya.kalyani\Downloads\Dashboard\database")
SAP_REFRESH_SCRIPT = APP_DIR / "sap_refresh.vbs"
SAP_REPORT_FILES = [
    "Daywise Data.xlsx",
    "Daywise MW Report.xlsx",
    "Monthwise MW Report.xlsx",
    "Monthwise Report.xlsx",
]

PLOT_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}

ADDITIVE_FIELDS = {
    "a_cells",
    "b_cells",
    "bel_cells",
    "eb_cells",
    "total_cells",
    "a_mw",
    "b_mw",
    "bel_mw",
    "eb_mw",
    "total_mw",
    "er_rejection",
    "for_rejection",
    "erq_rejection",
    "total_rejection",
    "rw_breakage",
    "bw_breakage",
    "alw_breakage",
    "agw_breakage",
    "cell_breakage",
    "total_breakage",
}

PERCENTAGE_FIELDS = {
    "a_yield_pct",
    "b_yield_pct",
    "bel_yield_pct",
    "eb_yield_pct",
    "er_pct",
    "for_pct",
    "breakage_pct",
}

st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Reading production workbooks...")
def cached_load(app_directory: str, workbook_stamp: tuple):
    del workbook_stamp
    return load_all(Path(app_directory))


def refresh_sap_reports():
    """Run the local SAP GUI export script and validate its four outputs."""
    if sys.platform != "win32":
        return False, "SAP refresh can run only on the Windows computer where SAP GUI is installed."

    if not SAP_REFRESH_SCRIPT.exists():
        return False, f"SAP refresh script was not found:\n{SAP_REFRESH_SCRIPT}"

    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return False, f"Could not create the data directory:\n{DATA_DIR}\n\n{exc}"

    try:
        result = subprocess.run(
            [
                "cscript.exe",
                "//nologo",
                str(SAP_REFRESH_SCRIPT),
                str(DATA_DIR),
            ],
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired:
        return False, (
            "SAP export timed out after 10 minutes. Check SAP for an open "
            "popup, warning, selection screen, or export dialog."
        )
    except FileNotFoundError:
        return False, "Windows Script Host could not be started. cscript.exe was not found."
    except Exception as exc:
        return False, f"Could not start the SAP refresh process:\n{exc}"

    output = "\n".join(
        value.strip()
        for value in (result.stdout, result.stderr)
        if value and value.strip()
    )
    if result.returncode != 0:
        return False, output or f"SAP refresh failed with exit code {result.returncode}."

    # Allow Excel and Windows a moment to finish writing and release the files.
    time.sleep(2)
    missing = []
    empty_files = []
    for file_name in SAP_REPORT_FILES:
        file_path = DATA_DIR / file_name
        if not file_path.exists():
            missing.append(file_name)
        elif file_path.stat().st_size == 0:
            empty_files.append(file_name)

    if missing:
        return False, "SAP completed, but these files were not created:\n" + "\n".join(
            f"• {name}" for name in missing
        )
    if empty_files:
        return False, "SAP created empty files:\n" + "\n".join(
            f"• {name}" for name in empty_files
        )

    return True, output or "All four SAP reports were exported successfully."


workbook_stamp = tuple(
    sorted(
        (path.name, path.stat().st_mtime_ns, path.stat().st_size)
        for path in DATA_DIR.glob("*.xlsx")
    )
)

sources, load_errors = cached_load(
    str(DATA_DIR),
    workbook_stamp,
)


# -----------------------------------------------------------------------------
# Shared helpers
# -----------------------------------------------------------------------------
def date_filter(df, start_date, end_date):
    if df is None or df.empty:
        return df

    mask = (
        (df["period"].dt.date >= start_date)
        & (df["period"].dt.date <= end_date)
    )
    return df.loc[mask].copy()


def view_grain(view):
    return {
        "Daily": "day",
        "Weekly": "week",
        "Monthly": "month",
    }[view]


def displayed_ticks(fig, df, view):
    if df is None or df.empty:
        return fig

    return ticks(
        fig,
        df["period"],
        view_grain(view),
        max_visible_ticks=16,
    )


def aggregate(df, view):
    """Aggregate additive fields and volume-weight percentage fields."""
    if df is None or df.empty:
        return df

    if view == "Daily":
        return df.copy()

    frequency = "W-MON" if view == "Weekly" else "MS"
    indexed = df.set_index("period").sort_index()
    result_parts = []

    additive_columns = [
        column
        for column in indexed.columns
        if column in ADDITIVE_FIELDS
    ]

    if additive_columns:
        summed = (
            indexed[additive_columns]
            .resample(frequency)
            .sum(min_count=1)
        )
        result_parts.append(summed)

    percentage_columns = [
        column
        for column in indexed.columns
        if column in PERCENTAGE_FIELDS
    ]

    if percentage_columns:
        if "total_cells" in indexed.columns:
            weights = indexed["total_cells"].where(
                indexed["total_cells"] > 0
            )
            total_weight = weights.resample(frequency).sum(min_count=1)
            weighted_values = {}

            for column in percentage_columns:
                weighted_sum = (
                    indexed[column]
                    .mul(weights)
                    .resample(frequency)
                    .sum(min_count=1)
                )
                weighted_values[column] = weighted_sum.div(total_weight)

            percentages = pd.DataFrame(weighted_values)
        else:
            percentages = (
                indexed[percentage_columns]
                .resample(frequency)
                .mean()
            )

        result_parts.append(percentages)

    if not result_parts:
        return pd.DataFrame(columns=["period"])

    result = pd.concat(result_parts, axis=1)
    result = result.loc[:, ~result.columns.duplicated()]
    result = result.dropna(how="all")
    return result.reset_index()


def comparison_tone(current, reference, higher_is_better=True):
    if current is None or reference is None or pd.isna(current) or pd.isna(reference): return "neutral"
    if np.isclose(current, reference): return "neutral"
    favorable = current > reference if higher_is_better else current < reference
    return "positive" if favorable else "negative"

def achievement_tone(value):
    if value is None or pd.isna(value): return "neutral"
    if value >= 100: return "positive"
    if value >= 90: return "warning"
    return "negative"

def validated_date_range(key_prefix, minimum_date, maximum_date, default_start, default_end, view_options=("Daily","Weekly","Monthly")):
    a,b,c=st.columns([1,1,1]); start_key=f"{key_prefix}_start"; end_key=f"{key_prefix}_end"
    start=a.date_input("Start Date",value=default_start,min_value=minimum_date,max_value=maximum_date,key=start_key,format="DD/MM/YYYY")
    if end_key in st.session_state and st.session_state[end_key] < start: st.session_state[end_key]=start
    end=b.date_input("End Date",value=max(default_end,start),min_value=start,max_value=maximum_date,key=end_key,format="DD/MM/YYYY")
    view=c.selectbox("View",list(view_options),key=f"{key_prefix}_view")
    if start > end:
        st.error("Invalid date range: Start Date cannot be later than End Date."); return None,None,None,False
    return start,end,view,True

def overview_run_data(daily, month_start, as_of_date, target):
    data=daily[(daily.period>=month_start)&(daily.period<=as_of_date)].sort_values("period").copy()
    data["cumulative_mw"]=data["total_mw"].fillna(0).cumsum(); data["run_rate"]=data["cumulative_mw"]/np.arange(1,len(data)+1)
    required=[]
    for _,r in data.iterrows():
        remaining=max(target-r["cumulative_mw"],0); days=max(pd.Period(r["period"],freq="M").days_in_month-r["period"].day,1); required.append(remaining/days)
    return data,pd.Series(required,index=data.index)

def selected_run_data(raw_daily, selected, plan_data, view):
    data=selected.sort_values("period").copy()
    if view=="Daily": data["run_rate"]=data["total_mw"]
    elif view=="Weekly": data["run_rate"]=data["total_mw"]/7
    else: data["run_rate"]=data["total_mw"]/data["period"].dt.days_in_month
    required=[]
    for _,r in data.iterrows():
        target=plan_for(plan_data,r["period"])
        if target is None: required.append(np.nan); continue
        m0=r["period"].replace(day=1); prior=raw_daily.loc[(raw_daily.period>=m0)&(raw_daily.period<r["period"]),"total_mw"].sum(); days=max(pd.Period(r["period"],freq="M").days_in_month-r["period"].day+1,1)
        required.append(max(target-prior,0)/days)
    return data,pd.Series(required,index=data.index)

def application_header(as_of_date):
    title_column, date_column = st.columns([4, 1])

    with title_column:
        st.markdown("## ☀️ SOLAR CELL MANUFACTURING DASHBOARD")
        st.caption("Final Product · Real-Time Production Monitoring")

    with date_column:
        st.markdown(
            f'<div class="asof">AS OF: {as_of_date:%d-%b-%Y}</div>',
            unsafe_allow_html=True,
        )


def plot(fig):
    st.plotly_chart(
        fig,
        use_container_width=True,
        config=PLOT_CONFIG,
    )


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
st.sidebar.markdown("## ☀️ Solar Cell MES")
page = st.sidebar.radio(
    "Navigation",
    ["Overview", "Production", "Analytics"],
    label_visibility="collapsed",
)

st.sidebar.divider()

SOURCE_LABELS = [
    ("day_quality", "Daywise Data"),
    ("day_mw", "Daywise MW Report"),
    ("month_mw", "Monthwise MW Report"),
    ("month_quality", "Monthwise Report"),
    ("plan", "Plan"),
]

for role, label in SOURCE_LABELS:
    status = "🟢" if role in sources else "🔴"
    st.sidebar.markdown(f"{status} {label}")

st.sidebar.divider()
st.sidebar.markdown("### SAP Data Refresh")
st.sidebar.caption("Open SAP GUI and log in before starting the refresh.")

refresh_clicked = st.sidebar.button(
    "↻ Refresh SAP Data",
    use_container_width=True,
    type="primary",
    help="Export fresh operational reports from SAP and reload the dashboard.",
)

if refresh_clicked:
    with st.spinner(
        "Exporting fresh reports from SAP. Do not use SAP or Excel until this finishes..."
    ):
        refresh_success, refresh_message = refresh_sap_reports()

    if refresh_success:
        st.cache_data.clear()
        st.session_state["sap_refresh_success"] = (
            "SAP data refreshed successfully at "
            f"{dt.datetime.now():%d-%b-%Y %I:%M:%S %p}."
        )
        st.session_state["sap_refresh_details"] = refresh_message
        st.rerun()
    else:
        st.sidebar.error("SAP refresh failed.")
        with st.sidebar.expander("View refresh error", expanded=True):
            st.code(refresh_message, language=None)

if "sap_refresh_success" in st.session_state:
    st.sidebar.success(st.session_state.pop("sap_refresh_success"))
    refresh_details = st.session_state.pop("sap_refresh_details", None)
    if refresh_details:
        with st.sidebar.expander("Refresh details", expanded=False):
            st.text(refresh_details)

latest_file_refresh = max(
    (path.stat().st_mtime for path in DATA_DIR.glob("*.xlsx")),
    default=None,
)
if latest_file_refresh is not None:
    st.sidebar.caption(
        "Latest data file: "
        + dt.datetime.fromtimestamp(latest_file_refresh).strftime(
            "%d-%b-%Y %I:%M:%S %p"
        )
    )
else:
    st.sidebar.caption("Latest data file: unavailable")

with st.sidebar.expander("Diagnostics", expanded=False):
    for error in load_errors:
        st.warning(error)

    for role, item in sources.items():
        st.markdown(
            f"**{item['file']}** — "
            f"{len(item['data']):,} rows, "
            f"header row {item['header_row']}"
        )

        issues = validate_dataset(item)
        if issues:
            for issue in issues:
                st.warning(issue)
        else:
            st.success("No validation warnings.")

        st.json(item["mapping"])


# -----------------------------------------------------------------------------
# Source assignment and effective date
# -----------------------------------------------------------------------------
if "day_mw" not in sources:
    st.error(
        "Daywise MW Report.xlsx is required. "
        "Place the workbook in the configured database directory."
    )
    st.stop()


dmw = sources["day_mw"]["data"]
dq = sources.get("day_quality", {}).get("data")
mmw = sources.get("month_mw", {}).get("data")
mq = sources.get("month_quality", {}).get("data")
plan = sources.get("plan", {}).get("data")

if dmw is None or dmw.empty:
    st.error("Daywise MW Report.xlsx did not contain valid mapped rows.")
    st.stop()

latest_mw = dmw["period"].max()
latest_quality = (
    dq["period"].max()
    if dq is not None and not dq.empty
    else None
)

as_of = (
    min(latest_mw, latest_quality)
    if latest_quality is not None
    else latest_mw
)

application_header(as_of)

if latest_quality is not None and latest_quality != latest_mw:
    st.warning(
        "Daily sources are not synchronized: "
        f"MW latest {latest_mw:%d-%b-%Y}; "
        f"quality latest {latest_quality:%d-%b-%Y}. "
        f"Overview uses {as_of:%d-%b-%Y}."
    )


# -----------------------------------------------------------------------------
# Overview
# -----------------------------------------------------------------------------
if page == "Overview":
    effective_rows = dmw.loc[dmw["period"] == as_of]
    if effective_rows.empty:
        st.error("No Daywise MW row exists for the effective Overview date.")
        st.stop()

    current_row = effective_rows.iloc[-1]
    prior_row = previous_row(dmw, as_of)

    month_start = as_of.replace(day=1)
    financial_year_start = fy_start(as_of)

    mtd = dmw.loc[
        (dmw["period"] >= month_start)
        & (dmw["period"] <= as_of)
    ].copy()

    ytd = dmw.loc[
        (dmw["period"] >= financial_year_start)
        & (dmw["period"] <= as_of)
    ].copy()

    target = plan_for(plan, as_of)
    mtd_actual = safe_sum(mtd, "total_mw")
    production_days = max(mtd["period"].nunique(), 1)
    run_rate = mtd_actual / production_days

    days_in_month = pd.Period(as_of, freq="M").days_in_month
    remaining_days = max(days_in_month - as_of.day, 1)

    required_rate = (
        max(target - mtd_actual, 0) / remaining_days
        if target is not None
        else None
    )

    plan_achievement = (
        mtd_actual / target * 100
        if target not in (None, 0)
        else None
    )

    remaining_plan_mw=max(target-mtd_actual,0) if target is not None else None
    today_mw=current_row.get("total_mw",0); previous_mw=None if prior_row is None else prior_row.get("total_mw")
    today_cells=current_row.get("total_cells",0); previous_cells=None if prior_row is None else prior_row.get("total_cells")
    columns=st.columns(8)
    card_values=[
        (f"Today's Production ({as_of:%d-%b-%Y})",f"{today_mw:.3f} MW",delta(today_mw,previous_mw,"MW"),comparison_tone(today_mw,previous_mw)),
        ("Today's Production — Cells",f"{today_cells:,.0f}",delta(today_cells,previous_cells,"Cells"),comparison_tone(today_cells,previous_cells)),
        ("MTD Production",f"{mtd_actual:.3f} MW",f"{month_start:%d-%b-%Y} → {as_of:%d-%b-%Y}","neutral"),
        ("FY YTD Production",f"{safe_sum(ytd,'total_mw'):.3f} MW",f"{financial_year_start:%d-%b-%Y} → {as_of:%d-%b-%Y}","neutral"),
        ("A Grade MW",f"{current_row.get('a_mw',0):.3f} MW","Effective production date","neutral"),
        ("Run Rate",f"{run_rate:.3f} MW/day",f"Required: {required_rate:.3f} MW/day" if required_rate is not None else "Required unavailable",comparison_tone(run_rate,required_rate)),
        ("Required Rate",f"{required_rate:.3f} MW/day" if required_rate is not None else "N/A",f"Remaining target: {remaining_plan_mw:.3f} MW" if remaining_plan_mw is not None else "Plan unavailable","plan"),
        ("Plan Achievement",f"{plan_achievement:.2f}%" if plan_achievement is not None else "N/A",f"Actual {mtd_actual:.3f} · Plan {target:.3f} · Remaining {remaining_plan_mw:.3f} MW" if target is not None else "Plan unavailable",achievement_tone(plan_achievement)),
    ]
    for column, values in zip(columns,card_values):
        with column: kpi(*values)

    trend_column, cells_column, mw_column = st.columns([1.5, 1, 1])

    with trend_column:
        st.subheader("Current-Month Production Trend")
        plot(production(mtd))

    with cells_column:
        st.subheader("Grade-wise Production — Cells")
        plot(
            donut(
                mtd,
                ["a_cells", "b_cells", "bel_cells", "eb_cells"],
                ["A Grade", "B Grade", "B-EL Grade", "EB Grade"],
                "Cells",
            )
        )

    with mw_column:
        st.subheader("Grade-wise Production — MW")
        plot(
            donut(
                mtd,
                ["a_mw", "b_mw", "bel_mw", "eb_mw"],
                ["A Grade", "B Grade", "B-EL Grade", "EB Grade"],
                "MW",
            )
        )

    st.subheader("Run Rate vs Required Rate — Current Plan")
    if target is not None:
        run_data, required_series=overview_run_data(dmw,month_start,as_of,target)
        plot(run_rate_chart(run_data,required_series,grain="day"))
    else: empty(f"No plan target is available for {as_of:%b-%Y}.")

    st.subheader("Source Data")
    source_options = {
        item["file"]: role
        for role, item in sources.items()
    }
    selected_file = st.selectbox(
        "Choose Excel file",
        list(source_options),
        key="overview_source_file",
    )

    raw_data = sources[source_options[selected_file]]["raw"].copy()
    st.dataframe(
        raw_data,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download selected data as CSV",
        data=raw_data.to_csv(index=False).encode("utf-8"),
        file_name=f"{Path(selected_file).stem}.csv",
        mime="text/csv",
    )


# -----------------------------------------------------------------------------
# Production
# -----------------------------------------------------------------------------
elif page == "Production":
    production_min=dmw["period"].min().date(); production_max=as_of.date()
    start_date,end_date,view,valid_range=validated_date_range("production",production_min,production_max,max(production_min,(as_of-pd.Timedelta(days=29)).date()),production_max)
    if not valid_range: st.stop()

    mw_data = aggregate(
        date_filter(dmw, start_date, end_date),
        view,
    )

    quality_data = (
        aggregate(
            date_filter(dq, start_date, end_date),
            view,
        )
        if dq is not None
        else None
    )

    if mw_data is None or mw_data.empty:
        st.warning("No production data is available for the selected range.")
        st.stop()

    production_column, yield_column = st.columns([1.5, 1])

    with production_column:
        st.subheader("Production Trend")
        production_figure = production(mw_data)
        displayed_ticks(production_figure, mw_data, view)
        plot(production_figure)

    with yield_column:
        st.subheader("Yield Percentage Trend")

        if quality_data is not None and not quality_data.empty:
            yield_figure = lines(
                quality_data,
                [
                    ("a_yield_pct", "A Grade Yield", COL["green"]),
                    ("b_yield_pct", "B Grade Yield", COL["blue"]),
                    ("bel_yield_pct", "B-EL Yield", COL["orange"]),
                    ("eb_yield_pct", "EB Yield", COL["purple"]),
                ],
                "Yield (%)",
                grain=view_grain(view),
            )
            displayed_ticks(yield_figure, quality_data, view)
            plot(yield_figure)
        else:
            empty("Daywise Data.xlsx is required for yield charts.")

    st.subheader("Run Rate vs Required Rate")
    selected_run, selected_required=selected_run_data(dmw,mw_data,plan,view)
    if selected_required.notna().any(): plot(run_rate_chart(selected_run,selected_required,grain=view_grain(view)))
    else: empty("No matching Plan targets are available for the selected range.")

    cells_column, mw_column = st.columns(2)

    with cells_column:
        st.subheader("Grade-wise Production — Cells")
        plot(
            donut(
                mw_data,
                ["a_cells", "b_cells", "bel_cells", "eb_cells"],
                ["A Grade", "B Grade", "B-EL Grade", "EB Grade"],
                "Cells",
            )
        )

    with mw_column:
        st.subheader("Grade-wise Production — MW")
        plot(
            donut(
                mw_data,
                ["a_mw", "b_mw", "bel_mw", "eb_mw"],
                ["A Grade", "B Grade", "B-EL Grade", "EB Grade"],
                "MW",
            )
        )


# -----------------------------------------------------------------------------
# Analytics
# -----------------------------------------------------------------------------
else:
    analytics_source = (
        dq
        if dq is not None and not dq.empty
        else mq
    )

    if analytics_source is None or analytics_source.empty:
        st.info(
            "Daywise Data.xlsx or Monthwise Report.xlsx "
            "is required for Analytics."
        )
        st.stop()

    source_grain_is_monthly = (
        analytics_source["time_grain"].iloc[0] == "month"
        if "time_grain" in analytics_source.columns
        else False
    )

    analytics_min=analytics_source["period"].min().date(); analytics_max=analytics_source["period"].max().date()
    analytics_views=("Monthly",) if source_grain_is_monthly else ("Daily","Weekly","Monthly")
    start_date,end_date,view,valid_range=validated_date_range("analytics",analytics_min,analytics_max,max(analytics_min,(analytics_source["period"].max()-pd.Timedelta(days=60)).date()),analytics_max,analytics_views)
    if not valid_range: st.stop()

    analytics_data = aggregate(
        date_filter(analytics_source, start_date, end_date),
        view,
    )

    if analytics_data is None or analytics_data.empty:
        st.warning("No analytics data is available for the selected range.")
        st.stop()

    yield_column, rejection_column = st.columns(2)

    with yield_column:
        st.subheader("Yield Trend (%)")
        yield_figure = lines(
            analytics_data,
            [
                ("a_yield_pct", "A Grade", COL["green"]),
                ("b_yield_pct", "B Grade", COL["blue"]),
                ("bel_yield_pct", "B-EL Grade", COL["orange"]),
                ("eb_yield_pct", "EB Grade", COL["purple"]),
            ],
            "Yield (%)",
            grain=view_grain(view),
        )
        displayed_ticks(yield_figure, analytics_data, view)
        plot(yield_figure)

    with rejection_column:
        st.subheader("Rejection Trend (%)")
        rejection_figure = lines(
            analytics_data,
            [
                ("er_pct", "ER %", COL["gray"]),
                ("for_pct", "FOR %", COL["blue"]),
                ("breakage_pct", "Breakage %", COL["orange"]),
            ],
            "Rejection / Breakage (%)",
            grain=view_grain(view),
        )
        displayed_ticks(rejection_figure, analytics_data, view)
        plot(rejection_figure)

    pareto_column, heatmap_column = st.columns(2)

    with pareto_column:
        st.subheader("Breakage Pareto")
        plot(pareto(analytics_data))

    with heatmap_column:
        st.subheader("Rejection Heatmap")

        if view == "Daily" and "total_rejection" in analytics_data.columns:
            heatmap_data = analytics_data.copy()
            heatmap_data["dow"] = (
                heatmap_data["period"].dt.day_name().str[:3]
            )
            heatmap_data["week"] = (
                heatmap_data["period"].dt.isocalendar().week
            )

            pivot = heatmap_data.pivot_table(
                index="week",
                columns="dow",
                values="total_rejection",
                aggfunc="sum",
            ).reindex(
                columns=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            )

            heatmap = go.Figure(
                go.Heatmap(
                    z=pivot.values,
                    x=pivot.columns,
                    y=[f"Wk {week}" for week in pivot.index],
                    text=np.round(pivot.values, 0),
                    texttemplate="%{text:,.0f}",
                    colorscale=[
                        [0, "#16a05d"],
                        [0.5, "#f4c542"],
                        [1, "#d73838"],
                    ],
                    colorbar_title="Rejection (Cells)",
                    hovertemplate=(
                        "Day: %{x}<br>"
                        "Week: %{y}<br>"
                        "Rejection: %{z:,.0f} Cells"
                        "<extra></extra>"
                    ),
                )
            )

            heatmap.update_layout(
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#dcecff"),
                margin=dict(l=55, r=60, t=40, b=55),
                xaxis_title="Day of Week",
                yaxis_title="ISO Week",
            )
            plot(heatmap)
        else:
            empty(
                "Select Daily view with rejection data "
                "to display the weekday heatmap."
            )


st.caption(
    "Plan values are used only for target comparisons. "
    "All production values are Actuals from operational workbooks."
)
