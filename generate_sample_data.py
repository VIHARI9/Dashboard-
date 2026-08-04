"""
Generates a sample workbook (sample_data.xlsx) with the 4 sheets described:
1. Day wise no of cells produced
2. Month wise no of cells produced
3. Daywise MW report
4. Monthwise MW report

Used only to test/demo the dashboard loader. Not needed once you have real data.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# ---------- 1. Day wise no of cells produced ----------
dates = pd.date_range("2025-01-01", "2025-05-15", freq="D")
n = len(dates)

a_grade = rng.integers(9000, 11000, n)
b_grade = rng.integers(30, 90, n)
bel = rng.integers(300, 700, n)
eb = rng.integers(80, 200, n)
total_prod = a_grade + b_grade + bel + eb

er = rng.integers(20, 80, n)
fo_r = rng.integers(10, 60, n)
er_q = rng.integers(5, 30, n)
total_rej = er + fo_r + er_q

raw_wafer = rng.integers(5, 40, n)
blue = rng.integers(10, 60, n)
al = rng.integers(2, 20, n)
ag = rng.integers(1, 10, n)
cell_brk = rng.integers(5, 30, n)
total_brk = raw_wafer + blue + al + ag + cell_brk

day_wise_nos = pd.DataFrame({
    "Date": dates,
    "Agrade": a_grade, "Bgrade": b_grade, "BEL": bel, "EB": eb, "Total": total_prod,
    "ER": er, "FOR": fo_r, "ER(Q)": er_q, "Total_Reject": total_rej,
    "Raw Wafer": raw_wafer, "Blue": blue, "Al": al, "Ag": ag, "Cell": cell_brk, "Total_Breakage": total_brk,
})

# ---------- 2. Month wise no of cells produced ----------
month_wise_nos = day_wise_nos.copy()
month_wise_nos["Month"] = month_wise_nos["Date"].dt.to_period("M").dt.to_timestamp()
agg_cols = [c for c in month_wise_nos.columns if c not in ("Date", "Month")]
month_wise_nos = month_wise_nos.groupby("Month", as_index=False)[agg_cols].sum()

# ---------- 3. Daywise MW report ----------
cell_watt = 5.65  # approx watts per cell, PERC
a_mw = a_grade * cell_watt / 1_000_000
b_mw = b_grade * cell_watt / 1_000_000
bel_mw = bel * cell_watt / 1_000_000
eb_mw = eb * cell_watt / 1_000_000
total_mw = a_mw + b_mw + bel_mw + eb_mw

daywise_mw = pd.DataFrame({
    "Date": dates,
    "A grade saleable (Nos)": a_grade,
    "B grade saleable (Nos)": b_grade,
    "BEL grade saleable (Nos)": bel,
    "EB grade saleable (Nos)": eb,
    "A grade saleable MW": a_mw,
    "B grade saleable MW": b_mw,
    "BEL grade saleable MW": bel_mw,
    "EB grade saleable MW": eb_mw,
    "Total production MW": total_mw,
})

# ---------- 4. Monthwise MW report ----------
monthwise_mw = daywise_mw.copy()
monthwise_mw["Month"] = monthwise_mw["Date"].dt.to_period("M").dt.to_timestamp()
agg_cols2 = [c for c in monthwise_mw.columns if c not in ("Date", "Month")]
monthwise_mw = monthwise_mw.groupby("Month", as_index=False)[agg_cols2].sum()

with pd.ExcelWriter("sample_data.xlsx", engine="openpyxl") as writer:
    day_wise_nos.to_excel(writer, sheet_name="Day wise no of cells produced", index=False)
    month_wise_nos.to_excel(writer, sheet_name="Month wise no of cells produced", index=False)
    daywise_mw.to_excel(writer, sheet_name="Daywise MW report", index=False)
    monthwise_mw.to_excel(writer, sheet_name="Monthwise MW report", index=False)

print("sample_data.xlsx created with sheets:")
print(" -", "Day wise no of cells produced", day_wise_nos.shape)
print(" -", "Month wise no of cells produced", month_wise_nos.shape)
print(" -", "Daywise MW report", daywise_mw.shape)
print(" -", "Monthwise MW report", monthwise_mw.shape)
