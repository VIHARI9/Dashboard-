import html
import streamlit as st

def kpi(title,value,detail="",tone="neutral"):
    if tone not in {"positive","negative","warning","plan","neutral"}: tone="neutral"
    st.markdown(f'<div class="kpi kpi-{tone}"><div class="kt">{html.escape(str(title))}</div><div class="kv">{html.escape(str(value))}</div><div class="ks">{html.escape(str(detail))}</div></div>',unsafe_allow_html=True)

def empty(message): st.info(message)
