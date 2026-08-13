import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

COL = {"blue":"#2b9cff","cyan":"#38d9f5","green":"#30d17b","red":"#ff5a68","orange":"#ffb020","purple":"#9b79ff","gray":"#b7c6d8"}

def layout(fig,h=360,xt="Reporting Period",yt=None,legend=True):
    fig.update_layout(height=h,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#dcecff",size=11),margin=dict(l=58,r=56,t=62,b=88),hovermode="x unified",xaxis_title=xt,yaxis_title=yt,legend=(dict(orientation="h",x=0,xanchor="left",y=1.16,yanchor="bottom",font=dict(color="#eaf4ff",size=10),bgcolor="rgba(0,0,0,0)") if legend else dict(visible=False)))
    fig.update_xaxes(color="#b8cbe0",title_font=dict(color="#cfe0f2",size=11),tickfont=dict(color="#a9bfd5",size=9),gridcolor="rgba(108,144,178,0.12)",zerolinecolor="rgba(108,144,178,0.20)",linecolor="#7894ae",showline=True,automargin=True)
    fig.update_yaxes(color="#b8cbe0",title_font=dict(color="#cfe0f2",size=11),tickfont=dict(color="#a9bfd5",size=9),gridcolor="rgba(108,144,178,0.18)",zerolinecolor="rgba(108,144,178,0.20)",linecolor="#7894ae",showline=True,automargin=True)
    return fig

def ticks(fig,periods,grain="day",max_visible_ticks=16):
    values=list(periods)
    if not values:return fig
    if grain=="day":labels=[v.strftime("%d-%b-%Y") for v in values]
    elif grain=="week":labels=[v.strftime("Wk %W\n%d-%b") for v in values]
    else:labels=[v.strftime("%b-%Y") for v in values]
    step=max(1,math.ceil(len(values)/max_visible_ticks)); visible_values=values[::step]; visible_labels=labels[::step]
    if visible_values[-1]!=values[-1]:visible_values.append(values[-1]);visible_labels.append(labels[-1])
    fig.update_xaxes(tickmode="array",tickvals=visible_values,ticktext=visible_labels,tickangle=-35 if len(visible_values)>8 else 0,automargin=True)
    return fig

def _line_mode(row_count):return "lines+markers+text" if row_count<=15 else "lines+markers"

def production(df):
    fig=make_subplots(specs=[[{"secondary_y":True}]]); row_count=len(df); show_labels=row_count<=15
    if "total_cells" in df.columns:
        fig.add_trace(go.Bar(x=df["period"],y=df["total_cells"],name="Total Saleable Cells",marker_color="rgba(56,217,245,0.72)",text=df["total_cells"] if show_labels else None,texttemplate="%{text:,.0f}" if show_labels else None,textposition="inside",hovertemplate="Date: %{x|%d-%b-%Y}<br>Total Saleable Cells: %{y:,.0f}<extra></extra>"),secondary_y=False)
    if "total_mw" in df.columns:
        fig.add_trace(go.Scatter(x=df["period"],y=df["total_mw"],name="Overall MW",mode=_line_mode(row_count),line=dict(color=COL["green"],width=2.4),marker=dict(size=6),text=df["total_mw"] if show_labels else None,texttemplate="%{text:.3f}" if show_labels else None,textposition="top center",hovertemplate="Date: %{x|%d-%b-%Y}<br>Overall Production: %{y:.3f} MW<extra></extra>"),secondary_y=True)
    if "a_mw" in df.columns:
        fig.add_trace(go.Scatter(x=df["period"],y=df["a_mw"],name="A Grade MW",mode=_line_mode(row_count),line=dict(color=COL["blue"],width=2.4),marker=dict(size=6),text=df["a_mw"] if show_labels else None,texttemplate="%{text:.3f}" if show_labels else None,textposition="bottom center",hovertemplate="Date: %{x|%d-%b-%Y}<br>A Grade Production: %{y:.3f} MW<extra></extra>"),secondary_y=True)
    layout(fig,h=410,xt="Production Date");fig.update_yaxes(title_text="Production (Cells)",secondary_y=False);fig.update_yaxes(title_text="Production (MW)",secondary_y=True,showgrid=False);fig.update_layout(bargap=.18,dragmode="pan");fig.update_xaxes(rangeslider=dict(visible=row_count>31,thickness=.08))
    return ticks(fig,df["period"],grain="day")

def donut(df,columns,names,unit):
    values=[float(df[c].fillna(0).sum()) if c in df.columns else 0.0 for c in columns];total=sum(values)
    fig=go.Figure(go.Pie(labels=names,values=values,hole=.62,textinfo="percent",marker=dict(colors=[COL["blue"],COL["green"],COL["orange"],COL["purple"]]),hovertemplate="%{label}<br>%{value:,.3f} "+unit+"<br>%{percent}<extra></extra>"))
    fig.update_layout(height=310,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#dcecff"),margin=dict(l=10,r=10,t=20,b=10),legend=dict(orientation="h",y=-.08,x=.5,xanchor="center",font=dict(color="#dcecff",size=10)),annotations=[dict(text=f"Total<br><b>{total:,.3f}</b><br>{unit}",x=.5,y=.5,showarrow=False,font=dict(color="#fff",size=12))])
    return fig

def lines(df,series,ytitle,grain="day"):
    fig=go.Figure();row_count=len(df);show_labels=row_count<=15
    for column,name,color in series:
        if column not in df.columns:continue
        fig.add_trace(go.Scatter(x=df["period"],y=df[column],name=name,mode=_line_mode(row_count),line=dict(color=color,width=2.2),marker=dict(size=6),text=df[column] if show_labels else None,texttemplate="%{text:.3f}" if show_labels else None,textposition="top center",hovertemplate="Period: %{x}<br>"+name+": %{y:.3f}<extra></extra>"))
    layout(fig,h=380,xt="Reporting Period",yt=ytitle);fig.update_xaxes(rangeslider=dict(visible=row_count>31,thickness=.08))
    return ticks(fig,df["period"],grain=grain)

def pareto(df):
    pairs=[]
    for column,label in [("rw_breakage","R-W Breakage"),("bw_breakage","B-W Breakage"),("alw_breakage","AL-W Breakage"),("agw_breakage","AG-W Breakage"),("cell_breakage","Cell Breakage")]:
        if column in df.columns:pairs.append((label,float(df[column].fillna(0).sum())))
    pairs.sort(key=lambda item:item[1],reverse=True);total=sum(v for _,v in pairs) or 1.0
    fig=go.Figure(go.Bar(x=[v for _,v in pairs],y=[n for n,_ in pairs],orientation="h",marker_color=COL["blue"],text=[f"{v:,.0f} ({v/total:.1%})" for _,v in pairs],textposition="outside",textfont=dict(color="#fff"),hovertemplate="%{y}<br>Breakage: %{x:,.0f} Cells<extra></extra>"));fig.update_yaxes(autorange="reversed")
    return layout(fig,h=380,xt="Breakage (Cells)",yt="Breakage Category",legend=False)

def run_rate_chart(df,required_rates,grain="day"):
    fig=go.Figure()
    if df is None or df.empty:return layout(fig,h=370,xt="Reporting Period",yt="Rate (MW/day)")
    data=df.copy();data["required_rate"]=list(required_rates);rows=len(data);mode="lines+markers+text" if rows<=15 else "lines+markers"
    fig.add_trace(go.Scatter(x=data["period"],y=data["run_rate"],name="Run Rate",mode=mode,line=dict(color=COL["green"],width=2.5),marker=dict(size=7),text=data["run_rate"] if rows<=15 else None,texttemplate="%{text:.3f}" if rows<=15 else None,textposition="top center",hovertemplate="Period: %{x}<br>Run Rate: %{y:.3f} MW/day<extra></extra>"))
    fig.add_trace(go.Scatter(x=data["period"],y=data["required_rate"],name="Required Rate",mode=mode,line=dict(color=COL["orange"],width=2.3,dash="dash"),marker=dict(size=7),text=data["required_rate"] if rows<=15 else None,texttemplate="%{text:.3f}" if rows<=15 else None,textposition="bottom center",hovertemplate="Period: %{x}<br>Required Rate: %{y:.3f} MW/day<extra></extra>"))
    layout(fig,h=370,xt="Reporting Period",yt="Rate (MW/day)");fig.update_xaxes(rangeslider=dict(visible=rows>31,thickness=.08))
    return ticks(fig,data["period"],grain=grain)
