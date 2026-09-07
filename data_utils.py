"""
Data loading + column auto-mapping for the Solar Cell Manufacturing Dashboard.

Real-world Excel exports vary in exact header text (extra spaces, "Nos" vs
"(Nos.)", "A Grade" vs "Agrade", duplicate "Total" columns, etc). Rather than
hard-coding exact header strings, we:
  1. Read every sheet in the uploaded workbook.
  2. Guess which sheet plays which "role" (day-nos / month-nos / day-mw / month-mw)
     from the sheet name.
  3. For each role, guess which column plays each canonical field, using
     keyword scoring + positional tie-breaks (handles the repeated "Total"
     columns: production total, rejection total, breakage total).
  4. Expose the guesses so the Streamlit app can let the user confirm/fix them.
"""
import re
import pandas as pd

# ---------------------------------------------------------------------------
# Canonical schemas: role -> ordered list of (key, label, keyword patterns)
# Order matters for positional tie-breaking (e.g. duplicate "Total" columns).
# ---------------------------------------------------------------------------

CELLS_SCHEMA = [
    ("period",        "Date/Month",           [r"^date$", r"^month$"]),
    ("a_grade",       "A Grade (Nos)",        [r"a\s*grade"]),
    ("b_grade",       "B Grade (Nos)",        [r"b\s*grade"]),
    ("bel",           "BEL (Nos)",            [r"\bbel\b"]),
    ("eb",            "EB (Nos)",             [r"\beb\b"]),
    ("total_prod",    "Total Production",     [r"^total$", r"total.*prod"]),
    ("er",            "ER Rejection",         [r"^er$"]),
    ("fo_r",          "FOR Rejection",        [r"^for$", r"f\.?o\.?r"]),
    ("er_q",          "ER(Q) Rejection",      [r"er\s*\(?q\)?"]),
    ("total_reject",  "Total Rejection",      [r"^total$", r"total.*rej"]),
    ("raw_wafer",     "Raw Wafer Breakage",   [r"raw\s*wafer"]),
    ("blue",          "Blue/BW Breakage",     [r"^blue$", r"b[\s\-]?w"]),
    ("al",             "Al Breakage",         [r"^al$", r"al[\s\-]?w"]),
    ("ag",             "Ag Breakage",         [r"^ag$", r"ag[\s\-]?w"]),
    ("cell_brk",       "Cell Breakage",       [r"^cell$", r"cell\s*breakage"]),
    ("total_brk",      "Total Breakage",      [r"^total$", r"total.*break"]),
]

MW_SCHEMA = [
    ("period",   "Date/Month",           [r"^date$", r"^month$"]),
    ("a_num",    "A Grade Saleable Nos", [r"a\s*grade.*(nos|number)"]),
    ("b_num",    "B Grade Saleable Nos", [r"b\s*grade.*(nos|number)"]),
    ("bel_num",  "BEL Saleable Nos",     [r"bel.*(nos|number)"]),
    ("eb_num",   "EB Saleable Nos",      [r"eb.*(nos|number)"]),
    ("a_mw",     "A Grade MW",           [r"a\s*grade.*mw"]),
    ("b_mw",     "B Grade MW",           [r"b\s*grade.*mw"]),
    ("bel_mw",   "BEL MW",               [r"bel.*mw"]),
    ("eb_mw",    "EB MW",                [r"eb.*mw"]),
    ("total_mw", "Total Production MW",  [r"total.*mw", r"total\s*production"]),
]

ROLE_LABELS = {
    "day_nos":   "Day wise no. of cells produced",
    "month_nos": "Month wise no. of cells produced",
    "day_mw":    "Daywise MW report",
    "month_mw":  "Monthwise MW report",
}

ROLE_SCHEMAS = {
    "day_nos": CELLS_SCHEMA,
    "month_nos": CELLS_SCHEMA,
    "day_mw": MW_SCHEMA,
    "month_mw": MW_SCHEMA,
}


def load_all_sheets(file) -> dict:
    """Read every sheet of an uploaded xlsx into a dict of DataFrames."""
    xls = pd.ExcelFile(file, engine="openpyxl")
    sheets = {}
    for name in xls.sheet_names:
        df = xls.parse(name)
        df.columns = [str(c).strip() for c in df.columns]
        sheets[name] = df
    return sheets


def guess_sheet_roles(sheet_names: list) -> dict:
    """Guess which sheet name corresponds to which of the 4 roles."""
    guesses = {}
    for role in ROLE_LABELS:
        is_month = "month" in role
        is_mw = "mw" in role
        best, best_score = None, 0
        for name in sheet_names:
            n = name.lower()
            score = 0
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
    for key, _label, patterns in schema:
        candidates = []
        for idx, col in enumerate(columns):
            if col in used:
                continue
            score = _score_column(col, patterns)
            if score > 0:
                # prefer columns that come after the last mapped column
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


def build_clean_df(df: pd.DataFrame, mapping: dict, is_month: bool) -> pd.DataFrame:
    """Rename mapped columns to canonical keys, parse period as datetime, coerce numerics."""
    rename = {v: k for k, v in mapping.items() if v is not None}
    clean = df.rename(columns=rename)
    keep = [k for k in mapping if k in clean.columns]
    clean = clean[keep].copy()

    if "period" in clean.columns:
        clean["period"] = pd.to_datetime(clean["period"], errors="coerce")
        clean = clean.dropna(subset=["period"])

    for c in clean.columns:
        if c != "period":
            clean[c] = pd.to_numeric(clean[c], errors="coerce").fillna(0)

    clean = clean.sort_values("period").reset_index(drop=True)
    return clean
