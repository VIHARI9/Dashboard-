# # CSS = r'''<style>
# # :root{--bg:#031426;--side:#08274a;--border:#1d5786;--text:#f7fbff;--muted:#b2c5d9;--input:#f3f6fa;--input-text:#142235}
# # [data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],[data-testid="stSidebarCollapseButton"],[data-testid="collapsedControl"]{display:none!important;visibility:hidden!important}
# # html,body,[data-testid="stAppViewContainer"],.stApp{background:linear-gradient(180deg,#061d37 0%,#031426 48%,#020d1b 100%)!important;color:var(--text)!important}
# # .stAppViewContainer>.main{padding-top:0!important}.block-container{max-width:1900px;padding:.85rem 1.35rem 2rem!important}
# # [data-testid="stSidebar"]{display:block!important;visibility:visible!important;opacity:1!important;transform:translateX(0)!important;left:0!important;width:23rem!important;min-width:23rem!important;max-width:23rem!important;margin-left:0!important;background:linear-gradient(180deg,#0a315b,#061f3e)!important;border-right:1px solid #2470aa!important;box-shadow:8px 0 24px #0004!important}
# # [data-testid="stSidebar"]>div:first-child{display:block!important;visibility:visible!important;width:23rem!important;min-width:23rem!important;padding-top:1rem!important;background:linear-gradient(180deg,#0a315b,#061f3e)!important}
# # [data-testid="stSidebar"][aria-expanded="false"]{transform:translateX(0)!important;margin-left:0!important;visibility:visible!important}
# # [data-testid="stSidebar"] *{color:#eaf4ff!important}[data-testid="stSidebar"] [role="radiogroup"] label{min-height:2.4rem!important;padding:.5rem .65rem!important;border:1px solid transparent!important;border-radius:8px!important}[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#277ec53d!important;border-color:#51a0d859!important}
# # h1,h2,h3,h4,h5,h6{color:#fff!important}p,label,.stCaption,[data-testid="stCaptionContainer"]{color:var(--muted)!important}
# # [data-testid="stDateInput"] label,[data-testid="stSelectbox"] label,[data-testid="stNumberInput"] label{color:#e6f2ff!important;font-weight:650!important}
# # [data-baseweb="input"] input,[data-testid="stDateInput"] input{color:var(--input-text)!important;-webkit-text-fill-color:var(--input-text)!important}
# # [data-baseweb="select"]>div,[data-baseweb="input"]>div,[data-testid="stDateInput"]>div>div{color:var(--input-text)!important;background:var(--input)!important;border:1px solid #b9c8d7!important;border-radius:8px!important}
# # [data-baseweb="select"] span,[data-baseweb="select"] svg{color:var(--input-text)!important;fill:var(--input-text)!important}
# # [data-baseweb="popover"]>div,[role="listbox"],[role="option"],[data-baseweb="calendar"]{color:#eaf4ff!important;background:#0a2948!important}[data-baseweb="popover"] *,[role="listbox"] *,[role="option"] *,[data-baseweb="calendar"] *{color:#eaf4ff!important}[role="option"]:hover,[data-baseweb="calendar"] button:hover{background:#164c78!important}
# # .kpi{position:relative;overflow:hidden;min-height:136px;padding:14px;border:1px solid var(--border);border-radius:10px;background:linear-gradient(145deg,#0c3565,#09213f);box-shadow:0 8px 22px #0005;transition:transform .16s ease,box-shadow .16s ease}.kpi:hover{transform:translateY(-3px);box-shadow:0 13px 30px #0007}.kpi-positive{background:linear-gradient(145deg,#0c5a45,#0a333c 55%,#09213f)!important;border-color:#2fd18e!important}.kpi-negative{background:linear-gradient(145deg,#65253a,#351f36 55%,#09213f)!important;border-color:#ef6a82!important}.kpi-warning{background:linear-gradient(145deg,#67451b,#382e25 55%,#09213f)!important;border-color:#e7a23d!important}.kpi-plan{background:linear-gradient(145deg,#49347a,#292750 55%,#09213f)!important;border-color:#9d87e3!important}.kpi-neutral{background:linear-gradient(145deg,#0c3565,#09213f)!important}.kt{color:#eaf4ff;font-size:.72rem;font-weight:800;line-height:1.3;text-transform:uppercase}.kv{color:#fff;font-size:1.55rem;font-weight:800;margin:10px 0 7px}.ks{color:#c5d7e8;font-size:.68rem;line-height:1.45}.asof{display:inline-block;padding:7px 12px;border:1px solid #3787bf;border-radius:8px;color:#fff;background:#09213f;font-weight:750}
# # [data-testid="stDataFrame"]{overflow:hidden!important;background:#071c34!important;border:1px solid #245d89!important;border-radius:9px!important}[data-testid="stDataFrame"]>div,[data-testid="stDataFrame"] canvas{background:#071c34!important}[data-testid="stElementToolbar"]{color:#eaf4ff!important;background:#0a294a!important}
# # .stDownloadButton>button,.stButton>button{color:#fff!important;background:linear-gradient(135deg,#1468b8,#0c4c91)!important;border:1px solid #3b91d2!important;border-radius:8px!important;font-weight:700!important}[data-testid="stAlert"]{color:#edf7ff!important;background:#0a2948!important;border:1px solid #2b6f9f!important;border-radius:8px!important}[data-testid="stAlert"] *{color:#edf7ff!important}
# # </style>'''
# # CSS = r'''<style>
# # :root{--bg:#031426;--side:#08274a;--border:#1d5786;--text:#f7fbff;--muted:#b2c5d9;--input:#f3f6fa;--input-text:#142235}
# # [data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important;visibility:hidden!important}
# # [data-testid="stHeader"]{background:transparent!important}
# # [data-testid="stSidebarCollapseButton"],[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important}
# # html,body,[data-testid="stAppViewContainer"],.stApp{background:linear-gradient(180deg,#061d37 0%,#031426 48%,#020d1b 100%)!important;color:var(--text)!important}
# # .stAppViewContainer>.main{padding-top:0!important}.block-container{max-width:1900px;padding:.85rem 1.35rem 2rem!important}
# # [data-testid="stSidebar"]{width:21rem!important;min-width:21rem!important;max-width:21rem!important;background:linear-gradient(180deg,#0a315b,#061f3e)!important;border-right:1px solid #2470aa!important;box-shadow:8px 0 24px #0004!important}
# # [data-testid="stSidebar"]>div:first-child{width:21rem!important;min-width:21rem!important;padding-top:1rem!important;background:linear-gradient(180deg,#0a315b,#061f3e)!important}

# # [data-testid="stSidebar"] *{color:#eaf4ff!important}[data-testid="stSidebar"] [role="radiogroup"] label{min-height:2.4rem!important;padding:.5rem .65rem!important;border:1px solid transparent!important;border-radius:8px!important}[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#277ec53d!important;border-color:#51a0d859!important}
# # h1,h2,h3,h4,h5,h6{color:#fff!important}p,label,.stCaption,[data-testid="stCaptionContainer"]{color:var(--muted)!important}
# # [data-testid="stDateInput"] label,[data-testid="stSelectbox"] label,[data-testid="stNumberInput"] label{color:#e6f2ff!important;font-weight:650!important}
# # [data-baseweb="input"] input,[data-testid="stDateInput"] input{color:var(--input-text)!important;-webkit-text-fill-color:var(--input-text)!important}
# # [data-baseweb="select"]>div,[data-baseweb="input"]>div,[data-testid="stDateInput"]>div>div{color:var(--input-text)!important;background:var(--input)!important;border:1px solid #b9c8d7!important;border-radius:8px!important}
# # [data-baseweb="select"] span,[data-baseweb="select"] svg{color:var(--input-text)!important;fill:var(--input-text)!important}
# # [data-baseweb="popover"]>div,[role="listbox"],[role="option"],[data-baseweb="calendar"]{color:#eaf4ff!important;background:#0a2948!important}[data-baseweb="popover"] *,[role="listbox"] *,[role="option"] *,[data-baseweb="calendar"] *{color:#eaf4ff!important}[role="option"]:hover,[data-baseweb="calendar"] button:hover{background:#164c78!important}
# # .kpi{position:relative;overflow:hidden;min-height:136px;padding:14px;border:1px solid var(--border);border-radius:10px;background:linear-gradient(145deg,#0c3565,#09213f);box-shadow:0 8px 22px #0005;transition:transform .16s ease,box-shadow .16s ease}.kpi:hover{transform:translateY(-3px);box-shadow:0 13px 30px #0007}.kpi-positive{background:linear-gradient(145deg,#0c5a45,#0a333c 55%,#09213f)!important;border-color:#2fd18e!important}.kpi-negative{background:linear-gradient(145deg,#65253a,#351f36 55%,#09213f)!important;border-color:#ef6a82!important}.kpi-warning{background:linear-gradient(145deg,#67451b,#382e25 55%,#09213f)!important;border-color:#e7a23d!important}.kpi-plan{background:linear-gradient(145deg,#49347a,#292750 55%,#09213f)!important;border-color:#9d87e3!important}.kpi-neutral{background:linear-gradient(145deg,#0c3565,#09213f)!important}.kt{color:#eaf4ff;font-size:.72rem;font-weight:800;line-height:1.3;text-transform:uppercase}.kv{color:#fff;font-size:1.55rem;font-weight:800;margin:10px 0 7px}.ks{color:#c5d7e8;font-size:.68rem;line-height:1.45}.asof{display:inline-block;padding:7px 12px;border:1px solid #3787bf;border-radius:8px;color:#fff;background:#09213f;font-weight:750}
# # [data-testid="stDataFrame"]{overflow:hidden!important;background:#071c34!important;border:1px solid #245d89!important;border-radius:9px!important}[data-testid="stDataFrame"]>div,[data-testid="stDataFrame"] canvas{background:#071c34!important}[data-testid="stElementToolbar"]{color:#eaf4ff!important;background:#0a294a!important}
# # .stDownloadButton>button,.stButton>button{color:#fff!important;background:linear-gradient(135deg,#1468b8,#0c4c91)!important;border:1px solid #3b91d2!important;border-radius:8px!important;font-weight:700!important}[data-testid="stAlert"]{color:#edf7ff!important;background:#0a2948!important;border:1px solid #2b6f9f!important;border-radius:8px!important}[data-testid="stAlert"] *{color:#edf7ff!important}

# # .app-title{font-size:1.72rem;font-weight:850;letter-spacing:.04em;color:#fff;line-height:1.15;margin-top:.25rem}.brand-fallback{height:72px;width:72px;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:2.1rem;background:linear-gradient(145deg,#0e5fa6,#092a50);border:1px solid #3c8bc4}
# # div[role="radiogroup"]{display:flex!important;gap:.55rem!important;padding:.38rem!important;margin:.35rem 0 1.2rem!important;border:1px solid #245d89!important;border-radius:11px!important;background:#061b32!important}div[role="radiogroup"] label{flex:1!important;justify-content:center!important;min-height:2.6rem!important;padding:.55rem 1rem!important;border-radius:8px!important;border:1px solid transparent!important}div[role="radiogroup"] label:hover{background:#1671bb33!important;border-color:#3b91d266!important}div[role="radiogroup"] label:has(input:checked){background:linear-gradient(135deg,#1468b8,#0c4c91)!important;border-color:#58a8df!important;box-shadow:0 4px 14px #0004!important}div[role="radiogroup"] label p{font-weight:800!important;color:#eef8ff!important}div[role="radiogroup"] [data-testid="stMarkdownContainer"]{width:100%;text-align:center}div[role="radiogroup"] div[data-testid="stRadio"]{width:100%}
# # </style>'''

# CSS = r'''<style>
# :root{
#   --renew-dark:#006b3f;--renew-green:#7ac943;--renew-lime:#a6ce39;
#   --renew-pale:#eef8e8;--bg:#f6f8f5;--card:#ffffff;--border:#dce7dc;
#   --text:#173126;--muted:#61736a;--danger:#c83d4d;--orange:#d58920;
# }
# html,body,[data-testid="stAppViewContainer"],.stApp{background:var(--bg)!important;color:var(--text)!important}
# [data-testid="stHeader"]{background:rgba(255,255,255,.96)!important;border-bottom:1px solid var(--border)!important}
# [data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important}
# [data-testid="stSidebarCollapseButton"],[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important;color:var(--renew-dark)!important}
# .block-container{max-width:1900px;padding:1.05rem 1.45rem 2.5rem!important}
# [data-testid="stSidebar"]{background:#fff!important;border-right:1px solid var(--border)!important;box-shadow:4px 0 18px rgba(0,65,36,.06)!important}
# [data-testid="stSidebar"]>div:first-child{background:#fff!important;padding-top:1rem!important}
# [data-testid="stSidebar"] *{color:var(--text)!important}
# h1,h2,h3,h4,h5,h6{color:var(--renew-dark)!important}p,label,.stCaption,[data-testid="stCaptionContainer"]{color:var(--muted)!important}
# .app-title{font-size:1.72rem;font-weight:850;letter-spacing:.035em;color:var(--renew-dark);line-height:1.15;margin-top:.25rem}
# .asof{display:inline-block;padding:8px 13px;border:1px solid #b9d9bd;border-radius:9px;color:var(--renew-dark);background:var(--renew-pale);font-weight:800;white-space:nowrap}
# /* Main page navigation */
# div[role="radiogroup"]{display:flex!important;gap:.55rem!important;padding:.4rem!important;margin:.4rem 0 1.25rem!important;border:1px solid var(--border)!important;border-radius:12px!important;background:#fff!important;box-shadow:0 3px 14px rgba(0,70,35,.05)!important}
# div[role="radiogroup"] label{flex:1!important;justify-content:center!important;min-height:2.7rem!important;padding:.55rem 1rem!important;border-radius:8px!important;border:1px solid transparent!important}div[role="radiogroup"] label:hover{background:var(--renew-pale)!important;border-color:#c8dfc9!important}div[role="radiogroup"] label:has(input:checked){background:linear-gradient(135deg,var(--renew-dark),#008f55)!important;border-color:var(--renew-dark)!important;box-shadow:0 4px 12px rgba(0,107,63,.18)!important}div[role="radiogroup"] label:has(input:checked) p{color:#fff!important}div[role="radiogroup"] label p{font-weight:800!important;color:var(--renew-dark)!important}div[role="radiogroup"] [data-testid="stMarkdownContainer"]{width:100%;text-align:center}
# /* Controls */
# [data-baseweb="select"]>div,[data-baseweb="input"]>div,[data-testid="stDateInput"]>div>div{background:#fff!important;color:var(--text)!important;border-color:#cbdaca!important;border-radius:8px!important}
# .stButton>button,.stDownloadButton>button{color:#fff!important;background:linear-gradient(135deg,var(--renew-dark),#008f55)!important;border:1px solid var(--renew-dark)!important;border-radius:8px!important;font-weight:750!important}.stButton>button:hover,.stDownloadButton>button:hover{background:linear-gradient(135deg,#005531,#76bd36)!important;border-color:#76bd36!important}
# /* KPI cards */
# .kpi{min-height:144px;padding:16px;border:1px solid var(--border);border-top:4px solid var(--renew-green);border-radius:12px;background:#fff;box-shadow:0 5px 18px rgba(0,62,34,.07)}
# .kpi-positive{border-top-color:#51ad43;background:linear-gradient(145deg,#fff,#f0faed)}.kpi-negative{border-top-color:#d65360;background:linear-gradient(145deg,#fff,#fff4f4)}.kpi-warning{border-top-color:#e4a642;background:linear-gradient(145deg,#fff,#fff9ed)}.kpi-plan{border-top-color:#8cc63f;background:linear-gradient(145deg,#fff,#f3fae8)}.kpi-neutral{border-top-color:var(--renew-dark)}
# .kt{color:var(--muted);font-size:.72rem;font-weight:800;line-height:1.3;text-transform:uppercase}.kv{color:var(--renew-dark);font-size:1.55rem;font-weight:850;margin:10px 0 7px}.ks{color:#6d7d74;font-size:.68rem;line-height:1.45}
# /* Content surfaces */
# [data-testid="stPlotlyChart"]{background:#fff!important;border:1px solid var(--border)!important;border-radius:12px!important;padding:.35rem!important;box-shadow:0 4px 16px rgba(0,62,34,.055)!important}
# [data-testid="stDataFrame"]{overflow:hidden!important;background:#fff!important;border:1px solid var(--border)!important;border-radius:10px!important}[data-testid="stDataFrame"]>div,[data-testid="stDataFrame"] canvas{background:#fff!important}
# [data-testid="stExpander"]{background:#fff!important;border:1px solid var(--border)!important;border-radius:9px!important}[data-testid="stAlert"]{color:var(--text)!important;background:#f1f8ec!important;border:1px solid #c9dfc8!important;border-radius:9px!important}[data-testid="stAlert"] *{color:var(--text)!important}
# hr{border-color:var(--border)!important}
# </style>'''
CSS = r'''<style>
:root{--renew:#00703c;--renew2:#79c143;--lime:#a8cf45;--bg:#f6f8f5;--card:#fff;--border:#d7e2d8;--text:#111;--muted:#4c5a52}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--bg)!important;color:var(--text)!important}
/* Remove the top white Streamlit bar while retaining the sidebar controls. */
[data-testid="stHeader"]{background:transparent!important;height:0!important;min-height:0!important;border:0!important;box-shadow:none!important}
[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important}
[data-testid="stSidebarCollapseButton"],[data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important;position:fixed!important;top:.55rem!important;z-index:100000!important;color:var(--renew)!important}
[data-testid="collapsedControl"]{left:.55rem!important;background:#fff!important;border:1px solid var(--border)!important;border-radius:8px!important;box-shadow:0 2px 8px #0002!important}
.block-container{max-width:1900px;padding:.65rem 1.45rem 2.5rem!important}
[data-testid="stSidebar"]{background:#fff!important;border-right:1px solid var(--border)!important;box-shadow:4px 0 18px rgba(0,72,38,.07)!important}
[data-testid="stSidebar"]>div:first-child{background:#fff!important;padding-top:1rem!important}
[data-testid="stSidebar"] *{color:var(--text)!important}
h1,h2,h3,h4,h5,h6,.app-title{color:var(--renew)!important}p,label,.stCaption,[data-testid="stCaptionContainer"]{color:var(--text)!important}
.app-title{font-size:1.8rem;font-weight:900;letter-spacing:.035em;line-height:1.15;margin-top:.25rem}.asof{display:inline-block;padding:8px 13px;border:1px solid #b9d9bd;border-radius:9px;color:#111;background:#eef8e8;font-weight:800;white-space:nowrap}
/* Full-width real tab-style segmented navigation. */
[data-testid="stSegmentedControl"]{width:100%!important;margin:.45rem 0 1.35rem!important}
[data-testid="stSegmentedControl"]>div{width:100%!important;display:grid!important;grid-template-columns:repeat(3,1fr)!important;gap:0!important;padding:0!important;background:#fff!important;border:1px solid #bcd1bf!important;border-radius:10px!important;overflow:hidden!important;box-shadow:0 3px 13px rgba(0,70,36,.07)!important}
[data-testid="stSegmentedControl"] button{width:100%!important;min-height:3.25rem!important;border:0!important;border-right:1px solid #d4e0d5!important;border-radius:0!important;background:#fff!important;color:#111!important;font-size:1rem!important;font-weight:850!important;justify-content:center!important}
[data-testid="stSegmentedControl"] button:last-child{border-right:0!important}
[data-testid="stSegmentedControl"] button:hover{background:#edf7e9!important;color:#005b31!important}
[data-testid="stSegmentedControl"] button[aria-pressed="true"]{background:linear-gradient(135deg,var(--renew),#009451)!important;color:#fff!important;box-shadow:inset 0 -4px 0 var(--lime)!important}
[data-testid="stSegmentedControl"] button[aria-pressed="true"] *{color:#fff!important}
/* Inputs, buttons and tables. */
[data-baseweb="select"]>div,[data-baseweb="input"]>div,[data-testid="stDateInput"]>div>div{background:#fff!important;color:#111!important;border-color:#c7d5c8!important}
.stButton>button,.stDownloadButton>button{color:#fff!important;background:linear-gradient(135deg,var(--renew),#008e4d)!important;border:1px solid var(--renew)!important;border-radius:8px!important;font-weight:800!important}
/* Equal-size, large, high-contrast KPI tiles. */
[data-testid="stHorizontalBlock"]:has(.kpi){align-items:stretch!important}
[data-testid="column"]:has(.kpi){display:flex!important}
[data-testid="column"]:has(.kpi)>div{width:100%!important;display:flex!important}
[data-testid="column"]:has(.kpi) [data-testid="stMarkdownContainer"]{width:100%!important;display:flex!important}
.kpi{box-sizing:border-box!important;width:100%!important;height:175px!important;min-height:175px!important;max-height:175px!important;padding:18px 16px!important;border:1px solid var(--border)!important;border-top:5px solid var(--renew)!important;border-radius:12px!important;background:#fff!important;box-shadow:0 5px 18px rgba(0,62,34,.08)!important;display:flex!important;flex-direction:column!important;justify-content:space-between!important;overflow:hidden!important}
.kpi-positive{border-top-color:#36a852!important;background:#f7fcf5!important}.kpi-negative{border-top-color:#d94d5d!important;background:#fff8f8!important}.kpi-warning{border-top-color:#d89a2b!important;background:#fffaf0!important}.kpi-plan{border-top-color:var(--renew2)!important;background:#f8fced!important}.kpi-neutral{border-top-color:var(--renew)!important}
.kt{color:#111!important;font-size:.88rem!important;font-weight:900!important;line-height:1.28!important;text-transform:uppercase!important;min-height:2.25rem!important}.kv{color:#111!important;font-size:1.7rem!important;font-weight:900!important;line-height:1.12!important;margin:8px 0!important;white-space:normal!important}.ks{color:#222!important;font-size:.78rem!important;font-weight:550!important;line-height:1.38!important;min-height:2.2rem!important}
/* Plotly and component surfaces. */
[data-testid="stPlotlyChart"]{background:#fff!important;border:1px solid var(--border)!important;border-radius:12px!important;padding:.35rem!important;box-shadow:0 4px 16px rgba(0,62,34,.055)!important}
[data-testid="stPlotlyChart"] text{fill:#111!important;color:#111!important}
.js-plotly-plot .plotly .legendtext,.js-plotly-plot .plotly .xtick text,.js-plotly-plot .plotly .ytick text,.js-plotly-plot .plotly .gtitle,.js-plotly-plot .plotly .annotation-text{fill:#111!important;color:#111!important}
[data-testid="stDataFrame"]{background:#fff!important;border:1px solid var(--border)!important;border-radius:10px!important;overflow:hidden!important;color:#111!important}[data-testid="stDataFrame"] *{color:#111!important}
[data-testid="stExpander"]{background:#fff!important;border:1px solid var(--border)!important;border-radius:9px!important}[data-testid="stAlert"]{color:#111!important;background:#f1f8ec!important;border:1px solid #c9dfc8!important}[data-testid="stAlert"] *{color:#111!important}hr{border-color:var(--border)!important}
@media(max-width:1200px){.kpi{height:190px!important;min-height:190px!important;max-height:190px!important}.kv{font-size:1.45rem!important}.kt{font-size:.78rem!important}}
</style>'''
