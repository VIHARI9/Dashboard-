"""
charts.py
=========
Reusable Plotly chart builders for the dashboard. Every function returns a
`plotly.graph_objects.Figure` and takes only plain data (Series/lists/dicts)
so charts can be unit-tested and reused across the Overview / Production /
Analytics tabs without duplicating layout code.
"""
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Palette (kept in one place so every chart stays visually consistent)
# ---------------------------------------------------------------------------
COLORS = {
    "blue": "#3b7bff",
    "cyan": "#22d3ee",
    "green": "#22c55e",
    "amber": "#f5a623",
    "red": "#ef4444",
    "purple": "#a855f7",
    "gray": "#c7ced9",
    "grid": "#233054",
    "panel": "#141c30",
    "text": "#e7ebf5",
    "muted": "#8a93ab",
}

GRADE_COLORS = [COLORS["blue"], COLORS["green"], COLORS["amber"], COLORS["purple"]]
BREAKAGE_COLORS = [COLORS["red"], COLORS["amber"], COLORS["blue"], COLORS["purple"], COLORS["cyan"]]


def _base_layout(fig: go.Figure, height=300, legend=True, y2_title=None) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["panel"],
        plot_bgcolor=COLORS["panel"],
        font=dict(color=COLORS["text"], size=12),
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                     bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=COLORS["panel"], font_color=COLORS["text"]),
    )
    fig.update_xaxes(gridcolor=COLORS["grid"], zeroline=False)
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False)
    return fig


# ---------------------------------------------------------------------------
# Donuts
# ---------------------------------------------------------------------------

def grade_donut(labels, values, colors, center_title, center_sub, height=300) -> go.Figure:
    """Simple grade-wise donut with a centered total label."""
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors, line=dict(color=COLORS["panel"], width=2)),
        textinfo="percent", texttemplate="%{percent:.2%}",
        hovertemplate="%{label}<br>%{value:,.2f}<br>%{percent:.2%}<extra></extra>",
    ))
    fig.update_layout(
        annotations=[dict(text=f"<b>{center_title}</b><br><span style='font-size:11px;color={COLORS['muted']}'>{center_sub}</span>",
                           showarrow=False, font=dict(size=15))],
    )
    return _base_layout(fig, height=height)


def breakage_donut(labels, mw_values, cell_values, colors, total_mw, height=300) -> go.Figure:
    """Breakage donut whose legend/hover shows both MW and cell count per slice."""
    legend_labels = [f"{lbl} — {mw:.2f} MW · {cells:,.0f} cells"
                      for lbl, mw, cells in zip(labels, mw_values, cell_values)]
    fig = go.Figure(go.Pie(
        labels=legend_labels, values=mw_values, hole=0.62,
        marker=dict(colors=colors, line=dict(color=COLORS["panel"], width=2)),
        textinfo="percent", texttemplate="%{percent:.2%}",
        customdata=list(zip(labels, cell_values)),
        hovertemplate="%{customdata[0]}<br>%{value:.2f} MW<br>%{customdata[1]:,.0f} cells<extra></extra>",
    ))
    fig.update_layout(
        annotations=[dict(text=f"<b>{total_mw:.2f} MW</b><br><span style='font-size:11px'>Total Breakage</span>",
                           showarrow=False, font=dict(size=15))],
    )
    return _base_layout(fig, height=height)


# ---------------------------------------------------------------------------
# Overview / Production line & combo charts
# ---------------------------------------------------------------------------

def run_rate_vs_required(dates, run_rate, required_rate, height=300) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=dates, y=run_rate, name="Run Rate", mode="lines+markers",
                     line=dict(color=COLORS["green"], width=2.5), marker=dict(size=5))
    fig.add_scatter(x=dates, y=required_rate, name="Required Rate", mode="lines+markers",
                     line=dict(color=COLORS["amber"], width=2.5, dash="dot"), marker=dict(size=5))
    fig.update_yaxes(title_text="MW/day")
    return _base_layout(fig, height=height)


def daily_production_combo(dates, good_cells_nos, overall_mw, a_grade_mw, height=340) -> go.Figure:
    """Bars = Good Cells (Nos.) on primary axis; lines = Overall MW & A Grade MW on secondary axis."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=dates, y=good_cells_nos, name="Good Cells (Nos.)",
                marker_color=COLORS["blue"], opacity=0.75,
                text=[f"{v:,.0f}" for v in good_cells_nos], textposition="outside",
                textfont=dict(size=9), secondary_y=False)
    fig.add_scatter(x=dates, y=overall_mw, name="Overall MW", mode="lines+markers+text",
                     line=dict(color=COLORS["green"], width=2.5), marker=dict(size=5),
                     text=[f"{v:.2f}" for v in overall_mw], textposition="top center",
                     textfont=dict(size=9, color=COLORS["green"]), secondary_y=True)
    fig.add_scatter(x=dates, y=a_grade_mw, name="A Grade MW", mode="lines+markers+text",
                     line=dict(color=COLORS["cyan"], width=2.5, dash="dot"), marker=dict(size=5),
                     text=[f"{v:.2f}" for v in a_grade_mw], textposition="bottom center",
                     textfont=dict(size=9, color=COLORS["cyan"]), secondary_y=True)
    fig.update_yaxes(title_text="Good Cells (Nos.)", secondary_y=False)
    fig.update_yaxes(title_text="MW", secondary_y=True)
    return _base_layout(fig, height=height)


def efficiency_trend(dates, sap_efficiency, tester_efficiency, height=300) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=dates, y=sap_efficiency, name="SAP Efficiency – Bin Loss",
                     mode="lines+markers+text", line=dict(color=COLORS["blue"], width=2.2),
                     marker=dict(size=5), text=[f"{v:.2f}%" for v in sap_efficiency],
                     textposition="top center", textfont=dict(size=9, color=COLORS["blue"]))
    fig.add_scatter(x=dates, y=tester_efficiency, name="Tester Efficiency (Halm)",
                     mode="lines+markers+text", line=dict(color=COLORS["purple"], width=2.2, dash="dot"),
                     marker=dict(size=5), text=[f"{v:.2f}%" for v in tester_efficiency],
                     textposition="bottom center", textfont=dict(size=9, color=COLORS["purple"]))
    fig.update_yaxes(title_text="%")
    return _base_layout(fig, height=height)


def yield_trend(dates, yield_pct, height=300) -> go.Figure:
    fig = go.Figure(go.Scatter(x=dates, y=yield_pct, mode="lines+markers", fill="tozeroy",
                                line=dict(color=COLORS["cyan"], width=2.2), marker=dict(size=4)))
    fig.update_yaxes(title_text="Yield %")
    return _base_layout(fig, height=height, legend=False)


def plan_vs_actual(period_labels, plan_mw, actual_mw, height=300) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(x=period_labels, y=plan_mw, name="Plan MW", marker_color=COLORS["gray"],
                text=[f"{v:.2f}" for v in plan_mw], textposition="outside", textfont=dict(size=9))
    fig.add_bar(x=period_labels, y=actual_mw, name="Actual MW", marker_color=COLORS["blue"],
                text=[f"{v:.2f}" for v in actual_mw], textposition="outside", textfont=dict(size=9))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="MW")
    return _base_layout(fig, height=height)


def rejection_trend(dates, for_pct, er_pct, brk_pct, height=320) -> go.Figure:
    """SPC-style trend: FOR % (blue), ER % (gray), Breakage % (amber) with data labels on every point."""
    fig = go.Figure()
    fig.add_scatter(x=dates, y=for_pct, name="FOR %", mode="lines+markers+text",
                     line=dict(color=COLORS["blue"], width=2), marker=dict(size=5),
                     text=[f"{v:.2f}%" for v in for_pct], textposition="top center", textfont=dict(size=8.5, color=COLORS["blue"]))
    fig.add_scatter(x=dates, y=er_pct, name="ER %", mode="lines+markers+text",
                     line=dict(color=COLORS["gray"], width=2), marker=dict(size=5),
                     text=[f"{v:.2f}%" for v in er_pct], textposition="bottom center", textfont=dict(size=8.5, color=COLORS["gray"]))
    fig.add_scatter(x=dates, y=brk_pct, name="Breakage %", mode="lines+markers+text",
                     line=dict(color=COLORS["amber"], width=2), marker=dict(size=5),
                     text=[f"{v:.2f}%" for v in brk_pct], textposition="top center", textfont=dict(size=8.5, color=COLORS["amber"]))
    fig.update_yaxes(title_text="%")
    return _base_layout(fig, height=height)


def daily_production_trend_simple(dates, total_mw, height=300) -> go.Figure:
    """Single-series MW trend, used on the Production tab."""
    fig = go.Figure(go.Scatter(x=dates, y=total_mw, mode="lines+markers", fill="tozeroy",
                                line=dict(color=COLORS["blue"], width=2.2), marker=dict(size=4)))
    fig.update_yaxes(title_text="MW")
    return _base_layout(fig, height=height, legend=False)


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

def breakage_pareto(labels, mw_values, height=320) -> go.Figure:
    """Horizontal bars, sorted descending, with MW + % labels."""
    total = sum(mw_values) or 1
    order = sorted(range(len(labels)), key=lambda i: -mw_values[i])
    labels = [labels[i] for i in order]
    mw_values = [mw_values[i] for i in order]
    pct = [v / total * 100 for v in mw_values]
    text = [f"{v:.2f} MW · {p:.2f}%" for v, p in zip(mw_values, pct)]

    fig = go.Figure(go.Bar(
        x=mw_values, y=labels, orientation="h",
        marker_color=COLORS["blue"], text=text, textposition="outside", textfont=dict(size=10),
    ))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(title_text="MW")
    return _base_layout(fig, height=height, legend=False)


def rejection_heatmap(week_labels, day_labels, z_values, height=320) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=z_values, x=day_labels, y=week_labels,
        colorscale=[[0, COLORS["green"]], [0.5, COLORS["amber"]], [1, COLORS["red"]]],
        colorbar=dict(title="MW", tickformat=".2f"),
        hovertemplate="%{y}, %{x}<br>%{z:.2f} MW<extra></extra>",
    ))
    return _base_layout(fig, height=height, legend=False)


def plan_achievement_gauge(value_pct, height=140) -> go.Figure:
    color = COLORS["green"] if value_pct >= 95 else (COLORS["amber"] if value_pct >= 80 else COLORS["red"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value_pct,
        number={"suffix": "%", "valueformat": ".2f", "font": {"size": 20}},
        gauge={
            "axis": {"range": [0, 120], "tickcolor": COLORS["muted"]},
            "bar": {"color": color},
            "bgcolor": COLORS["panel"],
            "borderwidth": 0,
            "steps": [
                {"range": [0, 80], "color": "#2a3350"},
                {"range": [80, 100], "color": "#33405f"},
                {"range": [100, 120], "color": "#3d4d70"},
            ],
        },
    ))
    fig.update_layout(paper_bgcolor=COLORS["panel"], font=dict(color=COLORS["text"]),
                       height=height, margin=dict(l=10, r=10, t=10, b=0))
    return fig
