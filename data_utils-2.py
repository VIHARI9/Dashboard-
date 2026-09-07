"""
data_utils.py
=============
Data layer for the Solar Cell Manufacturing Dashboard.

Responsibilities:
  1. Read every .xlsx file in a folder (or an uploaded file), all sheets.
  2. Guess which sheet plays which "role" (day-nos / month-nos / day-mw /
     month-mw / plan) from file + sheet name.
  3. Guess which column plays each canonical field in a role's schema,
     using keyword scoring with positional tie-breaks (handles repeated
     "Total" columns: production total, rejection total, breakage total).
  4. Clean/typecast the mapped columns into a canonical DataFrame per role.
  5. Provide small derived-metric helpers (financial year bucketing,
     efficiency proxies, generic delta formatting) used by app.py.

Real-world Excel exports vary in exact header text, so nothing here is
hard-coded to exact strings — the app.py sidebar lets the user confirm or
override every guess before charts render.
"""
import glob
import os
import re

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Canonical schemas: role -> ordered list of (key, label, keyword patterns, required)
# Order matters for positional tie-breaking (e.g. duplicate "Total" columns).
# ---------------------------------------------------------------------------

CELLS_SCHEMA = [
    ("period",           "Date/Month",            [r"^date$", r"^month$"], True),
    ("a_grade",          "A Grade (Nos)",         [r"a\s*grade"], True),
    ("b_grade",          "B Grade (Nos)",         [r"b\s*grade"], True),
    ("bel",              "BEL (Nos)",             [r"\bbel\b"], True),
    ("eb",               "EB (Nos)",              [r"\beb\b"], True),
    ("total_prod",       "Total Production",      [r"^total$", r"total.*prod"], True),
    ("er",               "ER Rejection",          [r"^er$"], True),
    ("fo_r",             "FOR Rejection",         [r"^for$", r"f\.?o\.?r"], True),
    ("er_q",             "ER(Q) Rejection",       [r"er\s*\(?q\)?"], True),
    ("total_reject",     "Total Rejection",       [r"^total$", r"total.*rej"], True),
    ("raw_wafer",        "Raw Wafer Breakage",    [r"raw\s*wafer"], True),
    ("blue",             "Blue/BW Breakage",      [r"^blue$", r"b[\s\-]?w"], True),
    ("al",                "Al Breakage",          [r"^al$", r"al[\s\-]?w"], True),
    ("ag",                "Ag Breakage",          [r"^ag$", r"ag[\s\-]?w"], True),
    ("cell_brk",          "Cell Breakage",        [r"^cell$", r"cell\s*breakage"], True),
    ("total_brk",         "Total Breakage",       [r"^total$", r"total.*break"], True),
    ("sap_efficiency",    "SAP Efficiency - Bin Loss (%, optional)", [r"sap"], False),
    ("tester_efficiency", "Tester Efficiency - Halm (%, optional)",  [r"tester", r"halm"], False),
]

MW_SCHEMA = [
    ("period",   "Date/Month",           [r"^date$", r"^month$"], True),
    ("a_num",    "A Grade Saleable Nos", [r"a\s*grade.*(nos|number)"], True),
    ("b_num",    "B Grade Saleable Nos", [r"b\s*grade.*(nos|number)"], True),
    ("bel_num",  "BEL Saleable Nos",     [r"bel.*(nos|number)"], True),
    ("eb_num",   "EB Saleable Nos",      [r"eb.*(nos|number)"], True),
    ("a_mw",     "A Grade MW",           [r"a\s*grade.*mw"], True),
    ("b_mw",     "B Grade MW",           [r"b\s*grade.*mw"], True),
    ("bel_mw",   "BEL MW",               [r"bel.*mw"], True),
    ("eb_mw",    "EB MW",                [r"eb.*mw"], True),
    ("total_mw", "Total Production MW",  [r"total.*mw", r"total\s*production"], True),
]

PLAN_SCHEMA = [
    ("period",       "Month",               [r"^month$", r"^date$"], True),
    ("a_target",     "A Grade Target MW",   [r"a\s*grade"], True),
    ("b_target",     "B Grade Target MW",   [r"b\s*grade"], True),
    ("bel_target",   "BEL Grade Target MW", [r"\bbel\b"], True),
    ("total_target", "Total Target MW",     [r"total"], True),
]

ROLE_LABELS = {
    "day_nos":   "Day wise no. of cells produced",
    "month_nos": "Month wise no. of cells produced",
    "day_mw":    "Daywise MW report",
    "month_mw":  "Monthwise MW report",
    "plan":      "Plan / Target (MW)",
}

ROLE_SCHEMAS = {
    "day_nos": CELLS_SCHEMA,
    "month_nos": CELLS_SCHEMA,
    "day_mw": MW_SCHEMA,
    "month_mw": MW_SCHEMA,
    "plan": PLAN_SCHEMA,
}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_all_sheets(file) -> dict:
    """Read every sheet of a single xlsx (path or file-like) into a dict of DataFrames."""
    xls = pd.ExcelFile(file, engine="openpyxl")
    sheets = {}
    for name in xls.sheet_names:
        df = xls.parse(name)
        df.columns = [str(c).strip() for c in df.columns]
        sheets[name] = df
    return sheets


def load_dir(dir_path: str) -> dict:
    """
    Read every .xlsx file in a directory (all sheets in each). Keys are
    composite labels "filename.xlsx :: SheetName" so role-guessing can use
    filename context too (e.g. a "plan.xlsx" with a generic "Sheet1" tab).
    """
    sheets = {}
    for path in sorted(glob.glob(os.path.join(dir_path, "*.xlsx"))):
        fname = os.path.basename(path)
        if fname.startswith("~$"):  # skip Excel lock files
            continue
        try:
            xls = pd.ExcelFile(path, engine="openpyxl")
        except Exception:
            continue
        for name in xls.sheet_names:
            df = xls.parse(name)
            df.columns = [str(c).strip() for c in df.columns]
            sheets[f"{fname} :: {name}"] = df
    return sheets


# ---------------------------------------------------------------------------
# Role guessing
# ---------------------------------------------------------------------------

def guess_sheet_roles(sheet_names: list) -> dict:
    """Guess which sheet label corresponds to which role, using filename + sheet-name text."""
    guesses = {}
    for role in ROLE_LABELS:
        is_month = "month" in role
        is_mw = "mw" in role
        is_plan = role == "plan"
        best, best_score = None, 0
        for name in sheet_names:
            n = name.lower()
            score = 0
            if is_plan:
                if "plan" in n or "target" in n:
                    score += 3
            else:
                if "plan" in n or "target" in n:
                    continue  # never mistake the plan file for a production sheet
                if is_month and "month" in n:
                    score += 2
                if not is_month and "day" in n:
                    score += 2
                if is_mw and ("mw" in n or "megawatt" in n):
                    score += 2
                if not is_mw and ("mw" not in n):
                    score += 1
            if score > best_score:
                best, best_score = name, score
        if best_score > 0:
            guesses[role] = best
    return guesses


def _score_column(col_name: str, patterns: list) -> int:
    n = col_name.lower().strip()
    n_compact = re.sub(r"[\s\._\-]", "", n)
    score = 0
    for pat in patterns:
        if re.search(pat, n) or re.search(pat.replace(r"\s*", ""), n_compact):
            score += 1
    return score


def auto_map_columns(df: pd.DataFrame, schema: list) -> dict:
    """
    Best-effort mapping of canonical field -> actual column name.
    Handles repeated header text (e.g. 3x "Total") by preferring columns
    that appear after previously-mapped columns and haven't been used yet.
    """
    columns = list(df.columns)
    used = set()
    mapping = {}
    last_used_idx = -1
    for key, _label, patterns, _required in schema:
        candidates = []
        for idx, col in enumerate(columns):
            if col in used:
                continue
            score = _score_column(col, patterns)
            if score > 0:
                positional_bonus = 1 if idx > last_used_idx else 0
                candidates.append((score + positional_bonus, idx, col))
        if candidates:
            candidates.sort(key=lambda t: (-t[0], t[1]))
            _, idx, col = candidates[0]
            mapping[key] = col
            used.add(col)
            last_used_idx = idx
        else:
            mapping[key] = None
    return mapping


def build_clean_df(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """Rename mapped columns to canonical keys, parse period as datetime, coerce numerics."""
    rename = {v: k for k, v in mapping.items() if v is not None}
    clean = df.rename(columns=rename)
    keep = [k for k in mapping if mapping[k] is not None and k in clean.columns]
    clean = clean[keep].copy()

    if "period" in clean.columns:
        clean["period"] = pd.to_datetime(clean["period"], errors="coerce", format="mixed")
        clean = clean.dropna(subset=["period"])

    for c in clean.columns:
        if c != "period":
            clean[c] = pd.to_numeric(clean[c], errors="coerce").fillna(0)

    clean = clean.sort_values("period").reset_index(drop=True)
    return clean


# ---------------------------------------------------------------------------
# Derived metrics
# ---------------------------------------------------------------------------

def add_efficiency_proxies(day_nos: pd.DataFrame) -> pd.DataFrame:
    """
    If SAP Efficiency / Tester Efficiency columns weren't found in the source
    sheet, derive reasonable proxies from breakage & rejection data so the
    Daily Efficiency Trend chart still renders. Real mapped columns (if
    present) are always left untouched.
    """
    df = day_nos.copy()
    denom = df["total_prod"].replace(0, np.nan)

    if "sap_efficiency" not in df.columns:
        df["sap_efficiency"] = (1 - df["total_brk"] / denom) * 100
        df["sap_efficiency"] = df["sap_efficiency"].fillna(0).clip(0, 100)
        df.attrs.setdefault("estimated_cols", []).append("sap_efficiency")

    if "tester_efficiency" not in df.columns:
        df["tester_efficiency"] = (1 - df["total_reject"] / denom) * 100
        df["tester_efficiency"] = df["tester_efficiency"].fillna(0).clip(0, 100)
        df.attrs.setdefault("estimated_cols", []).append("tester_efficiency")

    return df


def fy_bounds(as_of: pd.Timestamp, fy_start_month: int = 4) -> tuple:
    """Return (fy_start, fy_end_exclusive) for the financial year containing as_of. Default Apr->Mar."""
    year = as_of.year if as_of.month >= fy_start_month else as_of.year - 1
    fy_start = pd.Timestamp(year=year, month=fy_start_month, day=1)
    fy_end = pd.Timestamp(year=year + 1, month=fy_start_month, day=1)
    return fy_start, fy_end


def fy_label(fy_start: pd.Timestamp) -> str:
    end_year_short = str(fy_start.year + 1)[-2:]
    return f"FY {fy_start.year}-{end_year_short} (Apr {fy_start.year} - Mar {fy_start.year + 1})"


def list_available_fys(min_date: pd.Timestamp, max_date: pd.Timestamp, fy_start_month: int = 4) -> list:
    """All FY start dates that overlap the data's date range, most recent first."""
    starts = []
    start, _ = fy_bounds(min_date, fy_start_month)
    cursor = start
    while True:
        cur_start, cur_end = fy_bounds(cursor, fy_start_month)
        if cur_start > max_date:
            break
        starts.append(cur_start)
        cursor = cur_end
    return sorted(set(starts), reverse=True)


def fmt_pct(v, decimals=2):
    return "N/A" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.{decimals}f}%"


def fmt_mw(v, decimals=2):
    return "N/A" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.{decimals}f} MW"


def fmt_num(v, decimals=2):
    return "N/A" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:,.{decimals}f}"


def clean_zero(v, tol=0.005):
    """Snap near-zero floats to exactly 0.0 so formatted deltas never show '-0.00'."""
    return 0.0 if v is not None and abs(v) < tol else v


def delta_arrow(v, good_when="up"):
    """Return ('up'|'down', arrow char) — good_when='down' flips the color semantics (e.g. Reject %)."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "flat", "–"
    if v >= 0:
        return ("up" if good_when == "up" else "down"), "▲"
    return ("down" if good_when == "up" else "up"), "▼"
