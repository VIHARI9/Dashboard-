"""
Generates sample data used to test/demo the dashboard:
  - sample_data.xlsx  (4 sheets: day-nos, month-nos, day-mw, month-mw)
  - plan.xlsx          (Month, A grade, B grade, BEL grade, Total Target — MW)
  - sample_folder/     the same 5 reports as separate files with generic
                        "Sheet1" tabs, mirroring a real folder of exports.

Not needed once you have real data — kept only so app.py always has
something to preview with "Use bundled sample data".
"""
import os

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# Financial year Apr-2025 -> latest date 15-May-2025 (per spec)
dates = pd.date_range("2025-04-01", "2025-05-15", freq="D")
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

month_wise_nos = day_wise_nos.copy()
month_wise_nos["Month"] = month_wise_nos["Date"].dt.to_period("M").dt.to_timestamp()
agg_cols = [c for c in month_wise_nos.columns if c not in ("Date", "Month")]
month_wise_nos = month_wise_nos.groupby("Month", as_index=False)[agg_cols].sum()

cell_watt = 5.65  # approx watts per PERC cell
a_mw = a_grade * cell_watt / 1_000_000
b_mw = b_grade * cell_watt / 1_000_000
bel_mw = bel * cell_watt / 1_000_000
eb_mw = eb * cell_watt / 1_000_000

daywise_mw = pd.DataFrame({
    "Date": dates,
    "A grade saleable (Nos)": a_grade, "B grade saleable (Nos)": b_grade,
    "BEL grade saleable (Nos)": bel, "EB grade saleable (Nos)": eb,
    "A grade saleable MW": a_mw, "B grade saleable MW": b_mw,
    "BEL grade saleable MW": bel_mw, "EB grade saleable MW": eb_mw,
    "Total production MW": a_mw + b_mw + bel_mw + eb_mw,
})

monthwise_mw = daywise_mw.copy()
monthwise_mw["Month"] = monthwise_mw["Date"].dt.to_period("M").dt.to_timestamp()
agg_cols2 = [c for c in monthwise_mw.columns if c not in ("Date", "Month")]
monthwise_mw = monthwise_mw.groupby("Month", as_index=False)[agg_cols2].sum()

with pd.ExcelWriter("sample_data.xlsx", engine="openpyxl") as writer:
    day_wise_nos.to_excel(writer, sheet_name="Day wise no of cells produced", index=False)
    month_wise_nos.to_excel(writer, sheet_name="Month wise no of cells produced", index=False)
    daywise_mw.to_excel(writer, sheet_name="Daywise MW report", index=False)
    monthwise_mw.to_excel(writer, sheet_name="Monthwise MW report", index=False)

# plan.xlsx (Month, A grade, B grade, BEL grade, Total Target — all MW)
plan = monthwise_mw[["Month"]].copy()
plan["A Grade"] = (monthwise_mw["A grade saleable MW"] * 1.08).round(2)
plan["B Grade"] = (monthwise_mw["B grade saleable MW"] * 1.08).round(2)
plan["BEL Grade"] = (monthwise_mw["BEL grade saleable MW"] * 1.08).round(2)
plan["Total Target"] = (plan["A Grade"] + plan["B Grade"] + plan["BEL Grade"]).round(2)
plan.to_excel("plan.xlsx", sheet_name="Sheet1", index=False)

# Mirror as a folder of separate single-sheet files with generic tab names,
# for testing the directory-path + auto-mapping flow end to end.
os.makedirs("sample_folder", exist_ok=True)
day_wise_nos.to_excel("sample_folder/Day wise production.xlsx", sheet_name="Sheet1", index=False)
month_wise_nos.to_excel("sample_folder/Month wise production.xlsx", sheet_name="Sheet1", index=False)
daywise_mw.to_excel("sample_folder/Daywise MW report.xlsx", sheet_name="Sheet1", index=False)
monthwise_mw.to_excel("sample_folder/Monthwise MW report.xlsx", sheet_name="Sheet1", index=False)
plan.to_excel("sample_folder/plan.xlsx", sheet_name="Sheet1", index=False)

print("Generated: sample_data.xlsx, plan.xlsx, sample_folder/ (5 files)")
print("day_wise_nos:", day_wise_nos.shape, "| daywise_mw:", daywise_mw.shape, "| plan:", plan.shape)
