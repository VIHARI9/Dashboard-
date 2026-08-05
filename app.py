import streamlit as st
import pandas as pd
import plotly.express as px
from calendar import monthrange

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Solar Dashboard",
    layout="wide"
)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown("""
<div style="
background:#1565C0;
padding:20px;
border-radius:15px;
text-align:center;
color:#ffffff;">
<h1>☀ RENEW CELL LINE PRODUCTION DASHBOARD - PERC TECHNOLOGY</h1>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CSS Styling
# --------------------------------------------------
st.markdown("""
<style>

h1 {
    font-size: 42px !important;
    font-weight: bold !important;
}

h3 {
    font-size: 40px !important;
    font-weight: bold !important;
    color:#1565C0;
}

[data-testid="stMetricValue"] {
    font-size: 48px !important;
    font-weight: bold !important;
    color: #1565C0;
}

[data-testid="stMetricLabel"] {
    font-size: 30px !important;
    font-weight: bold !important;
}

div[data-testid="stMetric"] {
    background:white;
    border-left:6px solid #1565C0;
    padding:20px;
    min-height:130px;
    border-radius:15px;
    border-top:1px solid #D6D6D6;
    border-right:1px solid #D6D6D6;
    border-bottom:1px solid #D6D6D6;
    text-align:center;
}

section[data-testid="stSidebar"] {
    width: 320px !important;
}

</style>
""", unsafe_allow_html=True)
def kpi_card(title, value, color="#1565C0"):
    st.markdown(
        f"""
        <div style="
            background:white;
            border-left:8px solid {color};
            border-radius:16px;
            padding:22px;
            min-height:120px;
            box-shadow:0 2px 8px rgba(0,0,0,0.12);
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
            text-align:center;
        ">
            <div style="
                font-size:28px;
                font-weight:700;
                color:#333333;
                margin-bottom:12px;
            ">
                {title}
            </div>
            <div style="
                font-size:46px;
                font-weight:800;
                color:{color};
            ">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --------------------------------------------------
# File Upload Section
# --------------------------------------------------
st.sidebar.markdown("### Upload Files")

mw_file = st.sidebar.file_uploader(
    "Upload MW Report",
    type=["xlsx"]
)

plan_file = st.sidebar.file_uploader(
    "Upload Plan File",
    type=["xlsx"]
)

daywise_file = st.sidebar.file_uploader(
    "Upload Daywise File",
    type=["xlsx"]
)
def apply_chart_style(fig, height=500):
    fig.update_layout(
        height=height,
        title_font_size=34,
        font=dict(size=28),
        xaxis_title_font=dict(size=24),
        yaxis_title_font=dict(size=24),
        xaxis=dict(
            tickfont=dict(size=18)
        ),
        yaxis=dict(
            tickfont=dict(size=18)
        ),
        legend=dict(
            font=dict(size=20)
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=22,
            font_family="Arial",
            font_color="black"
        ),
        margin=dict(l=40, r=40, t=80, b=60)
    )
    return fig
# --------------------------------------------------
# Read Uploaded Files
# --------------------------------------------------
if mw_file and plan_file and daywise_file:
    st.sidebar.success("Files Uploaded Successfully")

    mw = pd.read_excel(mw_file)
    plan = pd.read_excel(plan_file)
    daywise = pd.read_excel(daywise_file)

    # Clean column names
    mw.columns = mw.columns.str.strip()
    plan.columns = plan.columns.str.strip()
    daywise.columns = daywise.columns.str.strip()

else:
    st.info("Please upload all files to view the dashboard")
    st.stop()

# --------------------------------------------------
# Required Column Validation
# --------------------------------------------------
required_mw_columns = [
    "DATE",
    "A-GRADE SALEABLE",
    "B-GRADE SALEABLE",
    "B-EL GRADE SALEABLE",
    "EB GRADE SALEABLE",
    "TOTAL PRODUCTION",
    "A-GRADE SALEABLE(MW)",
    "B-GRADE SALEABLE(MW)",
    "B-EL GRADE SALEABLE(MW)",
    "EB GRADE SALEABLE(MW)",
    "TOTAL PRODUCTION(MW)"
]

required_daywise_columns = [
    "DATE",
    "A-GRADE",
    "B-GRADE",
    "B-EL GRADE",
    "EB GRADE",
    "TOTAL PRODUCTION",
    "TOTAL REJECTION",
    "TOTAL BREAKAGES",
    "R-W BREAKAGE",
    "B-W BREAKAGE",
    "AL-W BREAKAGE",
    "AG-W BREAKAGE",
    "CELL BREAKAGE",
    "A-GRADE YIELD(%)"
]

required_plan_columns = [
    "Month",
    "Total Target"
]

missing_mw = [col for col in required_mw_columns if col not in mw.columns]
missing_daywise = [col for col in required_daywise_columns if col not in daywise.columns]
missing_plan = [col for col in required_plan_columns if col not in plan.columns]

if missing_mw:
    st.error("Wrong MW Report uploaded or missing columns:")
    st.write(missing_mw)
    st.write("Available MW columns:")
    st.write(list(mw.columns))
    st.stop()

if missing_daywise:
    st.error("Wrong Daywise Data file uploaded or missing columns:")
    st.write(missing_daywise)
    st.write("Available Daywise columns:")
    st.write(list(daywise.columns))
    st.stop()

if missing_plan:
    st.error("Wrong Plan file uploaded or missing columns:")
    st.write(missing_plan)
    st.write("Available Plan columns:")
    st.write(list(plan.columns))
    st.stop()

# --------------------------------------------------
# Date Conversion
# --------------------------------------------------
mw["DATE"] = pd.to_datetime(mw["DATE"])
daywise["DATE"] = pd.to_datetime(daywise["DATE"])
plan["Month"] = pd.to_datetime(plan["Month"])

# --------------------------------------------------
# Financial Year Function
# --------------------------------------------------
def get_fy(date):
    if date.month >= 4:
        return f"FY {date.year}-{str(date.year + 1)[-2:]}"
    else:
        return f"FY {date.year - 1}-{str(date.year)[-2:]}"

mw["FY"] = mw["DATE"].apply(get_fy)
daywise["FY"] = daywise["DATE"].apply(get_fy)

# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------
st.sidebar.markdown("## Filters")

fy_list = sorted(
    mw["FY"].unique(),
    reverse=True
)

selected_fy = st.sidebar.selectbox(
    "Financial Year",
    fy_list
)

year_list = sorted(
    mw["DATE"].dt.year.unique()
)

selected_year = st.sidebar.selectbox(
    "Select Year",
    year_list,
    index=len(year_list) - 1
)

month_list = [
    "All",
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

month_dict = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

selected_month = st.sidebar.selectbox(
    "Select Month",
    month_list
)

# --------------------------------------------------
# Calendar Date Range Filter
# --------------------------------------------------
st.sidebar.subheader("📅 Date Range")

date_range = st.sidebar.date_input(
    "Select From Date and To Date",
    value=(
        mw["DATE"].min().date(),
        mw["DATE"].max().date()
    )
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_range
    end_date = date_range

# --------------------------------------------------
# Filter MW Data
# --------------------------------------------------
filtered_mw = mw.copy()

filtered_mw = filtered_mw[
    filtered_mw["FY"] == selected_fy
]

filtered_mw = filtered_mw[
    filtered_mw["DATE"].dt.year == selected_year
]

if selected_month != "All":
    filtered_mw = filtered_mw[
        filtered_mw["DATE"].dt.month == month_dict[selected_month]
    ]

filtered_mw = filtered_mw[
    (filtered_mw["DATE"].dt.date >= start_date) &
    (filtered_mw["DATE"].dt.date <= end_date)
]

# --------------------------------------------------
# Filter Daywise Data
# --------------------------------------------------
filtered_daywise = daywise.copy()

filtered_daywise = filtered_daywise[
    filtered_daywise["FY"] == selected_fy
]

filtered_daywise = filtered_daywise[
    filtered_daywise["DATE"].dt.year == selected_year
]

if selected_month != "All":
    filtered_daywise = filtered_daywise[
        filtered_daywise["DATE"].dt.month == month_dict[selected_month]
    ]

filtered_daywise = filtered_daywise[
    (filtered_daywise["DATE"].dt.date >= start_date) &
    (filtered_daywise["DATE"].dt.date <= end_date)
]

# --------------------------------------------------
# Empty Data Check
# --------------------------------------------------
if filtered_mw.empty:
    st.warning("No MW data available for selected filters")
    st.stop()

if filtered_daywise.empty:
    st.warning("No Daywise data available for selected filters")
    st.stop()

# --------------------------------------------------
# Latest Records
# --------------------------------------------------
latest = filtered_mw.iloc[-1]
latest_date = filtered_mw["DATE"].max()

# --------------------------------------------------
# Filter Info
# --------------------------------------------------
st.markdown(
    f"""
    <div style='text-align:right;
                color:gray;
                font-size:16px'>
    FY: {selected_fy} | Year: {selected_year} | Month: {selected_month} | Period: {start_date} to {end_date}
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# Production Calculations
# --------------------------------------------------
mtd_data = mw[
    (mw["DATE"].dt.year == latest_date.year) &
    (mw["DATE"].dt.month == latest_date.month)
]

mtd_mw = mtd_data["TOTAL PRODUCTION(MW)"].sum()

ytd_data = mw[
    mw["FY"] == selected_fy
]

ytd_mw = ytd_data["TOTAL PRODUCTION(MW)"].sum()

# --------------------------------------------------
# Plan Calculations
# --------------------------------------------------
current_month_plan = plan[
    (plan["Month"].dt.month == latest_date.month) &
    (plan["Month"].dt.year == latest_date.year)
]

current_plan = current_month_plan["Total Target"].sum()

if current_plan > 0:
    achievement = (mtd_mw / current_plan) * 100
else:
    achievement = 0

# --------------------------------------------------
# Run Rate / Required Rate
# --------------------------------------------------
days_completed = filtered_mw["DATE"].dt.day.max()

if days_completed > 0:
    run_rate = mtd_mw / days_completed
else:
    run_rate = 0

days_in_month = monthrange(
    latest_date.year,
    latest_date.month
)[1]

days_remaining = days_in_month - days_completed

if days_remaining > 0:
    required_rate = (current_plan - mtd_mw) / days_remaining
else:
    required_rate = 0

# --------------------------------------------------
# Quality Calculations
# --------------------------------------------------
total_production = filtered_daywise["TOTAL PRODUCTION"].sum()
total_rejection = filtered_daywise["TOTAL REJECTION"].sum()
total_breakage = filtered_daywise["TOTAL BREAKAGES"].sum()

total_input = (
    total_production +
    total_rejection +
    total_breakage
)

if total_input > 0:
    yield_pct = (total_production / total_input) * 100
    rejection_pct = (total_rejection / total_input) * 100
    breakage_pct = (total_breakage / total_input) * 100
else:
    yield_pct = 0
    rejection_pct = 0
    breakage_pct = 0

# --------------------------------------------------
# Production KPIs
# --------------------------------------------------
st.markdown("---")
st.subheader("Production KPIs")

col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card("MTD Production", f"{mtd_mw:.2f} MW", "#1565C0")

with col2:
    kpi_card("FYTD Production", f"{ytd_mw:.2f} MW", "#2E7D32")

with col3:
    kpi_card("Today's Production", f"{latest['TOTAL PRODUCTION(MW)']:.2f} MW", "#EF6C00")

with col4:
    kpi_card("Total Qty", f"{latest['TOTAL PRODUCTION']:,.0f}", "#6A1B9A")

col5, col6, col7, col8 = st.columns(4)

with col5:
    kpi_card("A Grade MW", f"{latest['A-GRADE SALEABLE(MW)']:.2f}", "#1B5E20")

with col6:
    kpi_card("B Grade MW", f"{latest['B-GRADE SALEABLE(MW)']:.2f}", "#0277BD")

with col7:
    kpi_card("BEL Grade MW", f"{latest['B-EL GRADE SALEABLE(MW)']:.2f}", "#F9A825")

with col8:
    kpi_card("EB Grade MW", f"{latest['EB GRADE SALEABLE(MW)']:.2f}", "#C62828")

col9, col10, col11, col12 = st.columns(4)

with col9:
    kpi_card("A Grade Qty", f"{latest['A-GRADE SALEABLE']:,.0f}", "#1B5E20")

with col10:
    kpi_card("B Grade Qty", f"{latest['B-GRADE SALEABLE']:,.0f}", "#0277BD")
with col11:
    kpi_card("BEL Grade Qty", f"{latest['B-EL GRADE SALEABLE']:,.0f}", "#F9A825")
with col12:
    kpi_card("EB Grade Qty", f"{latest['EB GRADE SALEABLE']:,.0f}", "#C62828")

# --------------------------------------------------
# Planning KPIs
# --------------------------------------------------
st.markdown("---")
st.subheader("Planning KPIs")

col13, col14, col15 = st.columns(3)

with col13:
    kpi_card("Plan MW", f"{current_plan:.2f}", "#1565C0")

with col14:
    kpi_card("Actual MW", f"{mtd_mw:.2f}", "#2E7D32")

with col15:
    kpi_card("Achievement %", f"{achievement:.2f}%", "#EF6C00")

col16, col17 = st.columns(2)

with col16:
    kpi_card("Run Rate", f"{run_rate:.2f} MW/day", "#00838F")

with col17:
    kpi_card("Required Rate", f"{required_rate:.2f} MW/day", "#C50F5E")

# --------------------------------------------------
# Quality KPIs
# --------------------------------------------------
st.markdown("---")
st.subheader("Quality KPIs")

col18, col19, col20 = st.columns(3)

col18.metric("Yield %", f"{yield_pct:.2f}%")
col19.metric("Reject %", f"{rejection_pct:.2f}%")
col20.metric("Breakage %", f"{breakage_pct:.2f}%")

# --------------------------------------------------
# Grade Mix Analysis
# --------------------------------------------------
st.markdown("---")
st.subheader("Grade Mix Analysis")

left, right = st.columns(2)

grade_mw = pd.DataFrame({
    "Grade": ["A Grade", "B Grade", "BEL Grade", "EB Grade"],
    "MW": [
        filtered_mw["A-GRADE SALEABLE(MW)"].sum(),
        filtered_mw["B-GRADE SALEABLE(MW)"].sum(),
        filtered_mw["B-EL GRADE SALEABLE(MW)"].sum(),
        filtered_mw["EB GRADE SALEABLE(MW)"].sum()
    ]
})

fig = px.pie(
    grade_mw,
    values="MW",
    names="Grade",
    hole=0.6,
    title="Grade-wise Production MW"
)

fig = apply_chart_style(fig, height=500)


with left:
    st.plotly_chart(
        fig,
        use_container_width=True
    )

grade_qty = pd.DataFrame({
    "Grade": ["A Grade", "B Grade", "BEL Grade", "EB Grade"],
    "Qty": [
        filtered_mw["A-GRADE SALEABLE"].sum(),
        filtered_mw["B-GRADE SALEABLE"].sum(),
        filtered_mw["B-EL GRADE SALEABLE"].sum(),
        filtered_mw["EB GRADE SALEABLE"].sum()
    ]
})

fig_qty = px.pie(
    grade_qty,
    values="Qty",
    names="Grade",
    hole=0.6,
    title="Grade-wise Production Qty"
)

fig_qty = apply_chart_style(fig_qty, height=500)

with right:
    st.plotly_chart(
        fig_qty,
        use_container_width=True
    )

# --------------------------------------------------
# Production Trend
# --------------------------------------------------
st.markdown("---")
st.subheader("Production Trend")

fig2 = px.area(
    filtered_mw,
    x="DATE",
    y="TOTAL PRODUCTION(MW)",
    markers=True,
    title="Daily Production Trend (MW)"
)

fig2.update_traces(
    hovertemplate="<b>Date:</b> %{x}<br><b>Production:</b> %{y:.2f} MW<extra></extra>"
)
fig2 = apply_chart_style(fig2, height=550)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# --------------------------------------------------
# Planning Analysis
# --------------------------------------------------
st.markdown("---")
st.subheader("Planning Analysis")

plan_actual = pd.DataFrame({
    "Type": ["Plan", "Actual"],
    "MW": [current_plan, mtd_mw]
})

fig_plan = px.bar(
    plan_actual,
    x="Type",
    y="MW",
    color="Type",
    title="Plan vs Actual",
    text="MW",
    hover_data={
        "Type": True,
        "MW": ":.2f"
    }
)

fig_plan.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside",
    marker_line_width=1.5
)

fig_plan = apply_chart_style(fig_plan, height=550)

st.plotly_chart(
    fig_plan,
    use_container_width=True
)
# --------------------------------------------------
# Monthly Plan vs Actual
# --------------------------------------------------
st.markdown("---")
st.subheader("Monthly Plan vs Actual")

mw_monthly = mw.copy()
mw_monthly["Month_Key"] = mw_monthly["DATE"].dt.to_period("M").astype(str)

actual_monthly = (
    mw_monthly
    .groupby("Month_Key")["TOTAL PRODUCTION(MW)"]
    .sum()
    .reset_index()
)

plan_monthly = plan.copy()
plan_monthly["Month_Key"] = plan_monthly["Month"].dt.to_period("M").astype(str)

plan_monthly = plan_monthly[
    ["Month_Key", "Total Target"]
]

plan_actual_monthly = plan_monthly.merge(
    actual_monthly,
    on="Month_Key",
    how="left"
)

plan_actual_monthly["TOTAL PRODUCTION(MW)"] = plan_actual_monthly[
    "TOTAL PRODUCTION(MW)"
].fillna(0)

plan_actual_monthly["Achievement %"] = (
    plan_actual_monthly["TOTAL PRODUCTION(MW)"] /
    plan_actual_monthly["Total Target"]
) * 100

fig_plan_monthly = px.bar(
    plan_actual_monthly,
    x="Month_Key",
    y=["Total Target", "TOTAL PRODUCTION(MW)"],
    barmode="group",
    title="Monthly Plan vs Actual",
    text_auto=".2f"
)

fig_plan_monthly.update_traces(
    textposition="outside",
    hovertemplate="<b>Month:</b> %{x}<br><b>MW:</b> %{y:.2f}<extra></extra>"
)

fig_plan_monthly = apply_chart_style(
    fig_plan_monthly,
    height=650
)

st.plotly_chart(
    fig_plan_monthly,
    use_container_width=True
)

# --------------------------------------------------
# Yield Trend
# --------------------------------------------------
st.markdown("---")
st.subheader("Yield Trend")

fig_yield = px.line(
    filtered_daywise,
    x="DATE",
    y="A-GRADE YIELD(%)",
    markers=True,
    title="A Grade Yield Trend"
)

fig_yield.update_traces(
    line=dict(width=4),
    marker=dict(size=10),
    hovertemplate="<b>Date:</b> %{x}<br><b>A Grade Yield:</b> %{y:.2f}%<extra></extra>"
)

fig_yield = apply_chart_style(fig_yield, height=550)

st.plotly_chart(
    fig_yield,
    use_container_width=True
)

# --------------------------------------------------
# Rejection Trend
# --------------------------------------------------
st.markdown("---")
st.subheader("Rejection Trend")

fig_reject = px.line(
    filtered_daywise,
    x="DATE",
    y="TOTAL REJECTION",
    markers=True,
    title="Total Rejection Trend"
)

fig_reject = apply_chart_style(fig_reject, height=550)

st.plotly_chart(
    fig_reject,
    use_container_width=True
)

# --------------------------------------------------
# Breakage Pareto
# --------------------------------------------------
st.markdown("---")
st.subheader("Breakage Pareto")

breakage_data = pd.DataFrame({
    "Type": ["R-W", "B-W", "AL-W", "AG-W", "CELL"],
    "Qty": [
        filtered_daywise["R-W BREAKAGE"].sum(),
        filtered_daywise["B-W BREAKAGE"].sum(),
        filtered_daywise["AL-W BREAKAGE"].sum(),
        filtered_daywise["AG-W BREAKAGE"].sum(),
        filtered_daywise["CELL BREAKAGE"].sum()
    ]
})

fig_breakage = px.bar(
    breakage_data,
    x="Qty",
    y="Type",
    orientation="h",
    title="Breakage Pareto"
)

fig_breakage = apply_chart_style(fig_breakage, height=550)

st.plotly_chart(
    fig_breakage,
    use_container_width=True
)