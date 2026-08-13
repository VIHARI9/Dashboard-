"""
styles.py
=========
Custom CSS for the dark MES-style theme, plus the accompanying
.streamlit/config.toml so Streamlit's own chrome (sidebar background,
widget colors, text) matches the custom-styled elements instead of fighting
them. Import inject_css() once, near the top of app.py, after
st.set_page_config().
"""
import streamlit as st

CSS = """
<style>
:root{
    --bg:#0b1120; --panel:#141c30; --panel2:#101828; --border:#233054;
    --text:#e7ebf5; --muted:#8a93ab;
    --blue:#3b7bff; --cyan:#22d3ee; --green:#22c55e; --amber:#f5a623; --red:#ef4444; --purple:#a855f7;
}

.stApp { background-color: var(--bg); }
section[data-testid="stSidebar"] { background-color: var(--panel2); border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }

/* Sidebar nav buttons */
div[data-testid="stSidebar"] .stButton button{
    width:100%; text-align:left; background:transparent; border:1px solid transparent;
    color:var(--muted); font-weight:500; border-radius:8px; padding:0.55rem 0.8rem;
    transition: background .15s ease;
}
div[data-testid="stSidebar"] .stButton button:hover{ background:#1a2440; color:var(--text); border-color:var(--border); }
div[data-testid="stSidebar"] .stButton button:focus{ box-shadow:none; }
div[data-testid="stSidebar"] .nav-active button{ background:var(--blue) !important; color:#fff !important; }

/* Generic panel card look for containers wrapped with .panel-card */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: var(--panel);
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

/* KPI card */
.kpi-card{
    border-radius:10px; padding:13px 15px; min-height:112px;
    display:flex; flex-direction:column; justify-content:center;
}
.kpi-card .lbl{font-size:10.5px; letter-spacing:.04em; text-transform:uppercase; opacity:.85; margin-bottom:2px;}
.kpi-card .sub{font-size:9.5px; color:var(--muted); margin-bottom:6px;}
.kpi-card .val{font-size:21px; font-weight:700; margin-bottom:6px; color:var(--text);}
.kpi-card .val .unit{font-size:11px; font-weight:400; opacity:.75;}
.kpi-card .delta{font-size:11.5px; font-weight:600;}
.kpi-card .delta.up{color:var(--green);}
.kpi-card .delta.down{color:var(--red);}
.kpi-card .delta.flat{color:var(--muted);}
.kpi-card .delta2{font-size:10.5px; color:var(--muted); margin-top:2px;}

.kpi-c1{background:linear-gradient(160deg,#16264a,#101a34);}
.kpi-c2{background:linear-gradient(160deg,#123a2a,#0f2820);}
.kpi-c5{background:linear-gradient(160deg,#3a1618,#2a1012);}
.kpi-c6{background:linear-gradient(160deg,#3a2a10,#2a1e0c);}
.kpi-c7{background:linear-gradient(160deg,#2a1c40,#201430);}

.as-of-badge{
    display:inline-block; background:linear-gradient(90deg,#16264a,#101a34);
    border:1px solid var(--border); border-radius:8px; padding:8px 14px;
    font-size:12.5px; font-weight:600; color:var(--cyan); margin-bottom:14px;
}

.section-caption{font-size:11.5px; color:var(--muted); margin:-6px 0 10px;}

/* dataframe / table tone-down */
div[data-testid="stDataFrame"] { border:1px solid var(--border); border-radius:10px; overflow:hidden; }

hr{border-color:var(--border);}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def write_theme_config(app_dir: str):
    """
    Ensure .streamlit/config.toml exists next to the app so Streamlit's own
    theme (not just our CSS overrides) matches — covers dialogs, tooltips,
    and any element our CSS selectors don't reach. Safe to call every run;
    only writes the file if it doesn't already exist so user edits persist.
    """
    import os
    cfg_dir = os.path.join(app_dir, ".streamlit")
    cfg_path = os.path.join(cfg_dir, "config.toml")
    if os.path.exists(cfg_path):
        return
    os.makedirs(cfg_dir, exist_ok=True)
    with open(cfg_path, "w") as f:
        f.write(
            '[theme]\n'
            'base = "dark"\n'
            'backgroundColor = "#0b1120"\n'
            'secondaryBackgroundColor = "#141c30"\n'
            'primaryColor = "#3b7bff"\n'
            'textColor = "#e7ebf5"\n'
        )
