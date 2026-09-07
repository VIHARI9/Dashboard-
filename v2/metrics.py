import pandas as pd

def fy_start(ts): return pd.Timestamp(ts.year if ts.month>=4 else ts.year-1,4,1)
def safe_sum(df,col): return float(df[col].fillna(0).sum()) if df is not None and col in df else 0.0
def previous_row(df,asof):
 p=df[df.period<asof].sort_values('period'); return None if p.empty else p.iloc[-1]
def delta(current,previous,unit,label='Previous Available Day'):
 if previous is None or pd.isna(previous) or previous==0: return 'No comparable prior value'
 diff=current-previous; arrow='▲' if diff>=0 else '▼'
 return f'{arrow} {abs(diff/previous*100):.2f}% vs {label} ({previous:,.3f} {unit}, {diff:+,.3f} {unit})'
def plan_for(plan,ts):
 if plan is None or plan.empty or 'total_target_mw' not in plan:return None
 hit=plan[(plan.period.dt.year==ts.year)&(plan.period.dt.month==ts.month)]
 return None if hit.empty else float(hit.total_target_mw.iloc[0])
