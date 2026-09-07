data_servie.py:
from __future__ import annotations

import calendar
import re
import subprocess
import sys
import uuid
from pathlib import Path
from threading import Lock

import numpy as np
import pandas as pd

from .config import OR_SOURCE_FIELD, settings

REFRESH_LOCK = Lock()
JOBS: dict[str, dict] = {}

FILES = {
    "quality": "Daywise Data.xlsx",
    "mw": "Daywise MW Report.xlsx",
    "plan": "Plan.xlsx",
}


def norm(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def read_workbook(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path, engine="openpyxl")
    frame.columns = [norm(column) for column in frame.columns]
    return frame.dropna(how="all")


def pick(frame: pd.DataFrame, aliases: list[str], default: float = 0.0) -> pd.Series:
    normalized = {norm(column): column for column in frame.columns}
    for alias in aliases:
        key = norm(alias)
        if key in normalized:
            return pd.to_numeric(frame[normalized[key]], errors="coerce").fillna(default)
    return pd.Series(default, index=frame.index, dtype=float)


def pick_date(frame: pd.DataFrame, aliases: list[str]) -> pd.Series:
    normalized = {norm(column): column for column in frame.columns}
    for alias in aliases:
        key = norm(alias)
        if key in normalized:
            return pd.to_datetime(frame[normalized[key]], errors="coerce", dayfirst=True)
    return pd.Series(pd.NaT, index=frame.index, dtype="datetime64[ns]")


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    paths = {key: settings.data_dir / name for key, name in FILES.items()}
    missing = [path.name for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing workbook(s): " + ", ".join(missing))

    mw = read_workbook(paths["mw"])
    quality = read_workbook(paths["quality"])
    plan = read_workbook(paths["plan"])

    daily_mw = pd.DataFrame({
        "period": pick_date(mw, ["date", "day", "production date"]),
        "a_cells": pick(mw, ["a grade saleable", "a-grade saleable"]),
        "b_cells": pick(mw, ["b grade saleable", "b-grade saleable"]),
        "bel_cells": pick(mw, ["b el grade saleable", "b-el grade saleable"]),
        "eb_cells": pick(mw, ["eb grade saleable"]),
        "total_cells": pick(mw, ["total production"]),
        "a_mw": pick(mw, ["a grade saleable mw", "a-grade saleable mw"]),
        "b_mw": pick(mw, ["b grade saleable mw", "b-grade saleable mw"]),
        "bel_mw": pick(mw, ["b el grade saleable mw", "b-el grade saleable mw"]),
        "eb_mw": pick(mw, ["eb grade saleable mw"]),
        "total_mw": pick(mw, ["total production mw"]),
    }).dropna(subset=["period"])

    daily_quality = pd.DataFrame({
        "period": pick_date(quality, ["date", "day", "production date"]),
        "er_rejection": pick(quality, ["er rejection"]),
        "for_rejection": pick(quality, ["for rejection"]),
        "erq_rejection": pick(quality, ["er q rejection", "er(q)rejection"]),
        "total_rejection": pick(quality, ["total rejection"]),
        "rw_breakage": pick(quality, ["r w breakage", "rw breakage"]),
        "bw_breakage": pick(quality, ["b w breakage", "bw breakage"]),
        "alw_breakage": pick(quality, ["al w breakage", "alw breakage"]),
        "agw_breakage": pick(quality, ["ag w breakage", "agw breakage"]),
        "cell_breakage": pick(quality, ["cell breakage"]),
        "total_breakage": pick(quality, ["total breakages", "total breakage"]),
        "a_yield_pct": pick(quality, ["a grade yield", "a-grade yield"]),
        "b_yield_pct": pick(quality, ["b grade yield", "b-grade yield"]),
        "bel_yield_pct": pick(quality, ["b el grade yield", "b-el grade yield"]),
        "eb_yield_pct": pick(quality, ["eb grade yield"]),
        "er_pct": pick(quality, ["er", "er percent", "er pct"]),
        "for_pct": pick(quality, ["for", "for percent", "for pct"]),
        "breakage_pct": pick(quality, ["breakage", "breakage percent", "breakage pct"]),
    }).dropna(subset=["period"])

    daily = daily_mw.merge(daily_quality, on="period", how="left").sort_values("period")
    denominator = (daily["total_cells"] + daily["total_rejection"] + daily["total_breakage"]).replace(0, np.nan)
    daily["or_pct"] = daily[OR_SOURCE_FIELD].div(denominator).mul(100).fillna(0)

    plan_data = pd.DataFrame({
        "period": pick_date(plan, ["month", "period", "date"]),
        "target_mw": pick(plan, ["total target", "target mw", "plan mw"]),
    }).dropna(subset=["period"]).sort_values("period")

    return daily, plan_data


def fy_label(date: pd.Timestamp) -> str:
    start = date.year if date.month >= 4 else date.year - 1
    return f"FY {start}-{str(start + 1)[-2:]}"


def fy_bounds(label: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    start = int(label.split()[1].split("-")[0])
    return pd.Timestamp(start, 4, 1), pd.Timestamp(start + 1, 3, 31)


def financial_years(frame: pd.DataFrame) -> list[str]:
    return sorted({fy_label(date) for date in frame["period"]}, reverse=True)


def effective_context(frame: pd.DataFrame, fy: str):
    start, end = fy_bounds(fy)
    selected = frame[(frame.period >= start) & (frame.period <= end)].copy()
    if selected.empty:
        raise ValueError(f"No data found for {fy}")
    as_of = selected.period.max()
    on_date = selected[selected.period == as_of]
    mtd = selected[(selected.period >= as_of.replace(day=1)) & (selected.period <= as_of)]
    ytd = selected[selected.period <= as_of]
    return start, end, as_of, on_date, mtd, ytd


def target_for(plan: pd.DataFrame, date: pd.Timestamp) -> float | None:
    row = plan[(plan.period.dt.year == date.year) & (plan.period.dt.month == date.month)]
    return None if row.empty else float(row.iloc[-1].target_mw)


def cumulative_target(plan: pd.DataFrame, start: pd.Timestamp, as_of: pd.Timestamp) -> float | None:
    rows = plan[(plan.period.dt.to_period("M") >= start.to_period("M")) & (plan.period.dt.to_period("M") <= as_of.to_period("M"))]
    return None if rows.empty else float(rows.target_mw.sum())


def weighted_pct(frame: pd.DataFrame, field: str) -> float:
    weights = frame["total_cells"].where(frame["total_cells"] > 0)
    valid = frame[field].notna() & weights.notna()
    if valid.any() and weights[valid].sum() > 0:
        return float((frame.loc[valid, field] * weights[valid]).sum() / weights[valid].sum())
    value = frame[field].mean()
    return 0.0 if pd.isna(value) else float(value)


def comparison(title: str, actual: float, plan: float | None, unit: str) -> dict:
    variance = None if plan is None else actual - plan
    achievement = None if plan in (None, 0) else actual / plan * 100
    return {"title": title, "actual": actual, "plan": plan, "variance": variance, "achievement_pct": achievement, "unit": unit}


def overview(fy: str) -> dict:
    daily, plan = load_data()
    start, _, as_of, on_date, mtd, ytd = effective_context(daily, fy)
    monthly_plan = target_for(plan, as_of)
    ytd_plan = cumulative_target(plan, start, as_of)
    days_in_month = calendar.monthrange(as_of.year, as_of.month)[1]
    daily_plan = monthly_plan / days_in_month if monthly_plan else None
    on_actual = float(on_date.total_mw.sum())
    mtd_actual = float(mtd.total_mw.sum())
    ytd_actual = float(ytd.total_mw.sum())
    run_rate = mtd_actual / max(mtd.period.nunique(), 1)
    remaining_days = max(days_in_month - as_of.day, 1)
    required = max((monthly_plan or 0) - mtd_actual, 0) / remaining_days if monthly_plan is not None else None

    distribution = []
    grade_fields = [
        ("A Grade", "a_cells", "a_mw"),
        ("B Grade", "b_cells", "b_mw"),
        ("B-EL", "bel_cells", "bel_mw"),
        ("EB", "eb_cells", "eb_mw"),
    ]
    for label, cells_field, mw_field in grade_fields:
        distribution.append({"label": label, "cells": float(on_date[cells_field].sum()), "on_date": float(on_date[mw_field].sum()), "mtd": float(mtd[mw_field].sum()), "ytd": float(ytd[mw_field].sum())})

    rejection = []
    for label, field in [("ER", "er_rejection"), ("OR", OR_SOURCE_FIELD), ("FO", "for_rejection"), ("Breakage", "total_breakage")]:
        rejection.append({"label": label, "on_date": float(on_date[field].sum()), "mtd": float(mtd[field].sum()), "ytd": float(ytd[field].sum())})

    yield_rows = []
    fields = [("A Grade", "a_yield_pct"), ("B Grade", "b_yield_pct"), ("B-EL", "bel_yield_pct"), ("EB", "eb_yield_pct")]
    for label, field in fields:
        yield_rows.append({"label": label, "on_date": weighted_pct(on_date, field), "mtd": weighted_pct(mtd, field), "ytd": weighted_pct(ytd, field)})
    yield_rows.append({"label": "Good Cells", "on_date": sum(weighted_pct(on_date, f) for _, f in fields), "mtd": sum(weighted_pct(mtd, f) for _, f in fields), "ytd": sum(weighted_pct(ytd, f) for _, f in fields)})

    return {
        "financial_year": fy,
        "as_of": as_of.date().isoformat(),
        "kpis": [
            comparison("On-date production", on_actual, daily_plan, "MW"),
            comparison("MTD production", mtd_actual, monthly_plan, "MW"),
            comparison("YTD production", ytd_actual, ytd_plan, "MW"),
            comparison("Run rate", run_rate, required, "MW/day"),
            comparison("Plan achievement", mtd_actual, monthly_plan, "MW"),
        ],
        "distribution": distribution,
        "rejection": rejection,
        "yield_table": yield_rows,
    }


def records(frame: pd.DataFrame, columns: list[str]) -> list[dict]:
    result = []
    for _, row in frame.iterrows():
        item = {"period": row.period.date().isoformat()}
        for column in columns:
            item[column] = None if pd.isna(row.get(column)) else float(row.get(column))
        result.append(item)
    return result


def trends(fy: str) -> dict:
    daily, _ = load_data()
    start, end = fy_bounds(fy)
    data = daily[(daily.period >= start) & (daily.period <= end)].copy()
    data["wafer_loss_pct"] = data[["or_pct", "er_pct", "breakage_pct"]].sum(axis=1)
    monthly = data.set_index("period")["total_mw"].resample("MS").agg(["sum", "count"]).reset_index()
    monthly["avg_mw_per_day"] = monthly["sum"] / monthly["count"].replace(0, np.nan)
    return {
        "production": records(data, ["a_mw", "b_mw", "bel_mw", "eb_mw", "total_mw"]),
        "rejection": records(data, ["er_pct", "or_pct", "for_pct", "breakage_pct"]),
        "yield": records(data, ["a_yield_pct", "b_yield_pct", "bel_yield_pct", "eb_yield_pct"]),
        "wafer_loss": records(data, ["wafer_loss_pct"]),
        "breakage": {field: float(data[field].sum()) for field in ["total_breakage", "rw_breakage", "bw_breakage", "alw_breakage", "agw_breakage", "cell_breakage"]},
        "monthly_average": [{"period": row.period.date().isoformat(), "avg_mw_per_day": float(row.avg_mw_per_day)} for _, row in monthly.dropna().iterrows()],
    }


def run_refresh_job(job_id: str) -> None:
    if not REFRESH_LOCK.acquire(blocking=False):
        JOBS[job_id].update(status="failed", error="Another refresh is already running")
        return
    try:
        JOBS[job_id].update(status="running", progress=10)
        if sys.platform != "win32":
            raise RuntimeError("SAP refresh requires Windows with SAP GUI")
        if not settings.sap_script.exists():
            raise RuntimeError(f"Missing SAP script: {settings.sap_script}")
        result = subprocess.run(["cscript.exe", "//nologo", str(settings.sap_script), str(settings.data_dir)], capture_output=True, text=True, timeout=600)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        load_data()
        JOBS[job_id].update(status="completed", progress=100, message=result.stdout.strip())
    except Exception as exc:
        JOBS[job_id].update(status="failed", progress=100, error=str(exc))
    finally:
        REFRESH_LOCK.release()


def create_job() -> dict:
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"id": job_id, "status": "queued", "progress": 0}
    return JOBS[job_id]


app.tsx:
import { useEffect, useMemo, useState } from "react";
import { ArrowDownRight, ArrowUpRight, Minus, RefreshCw } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ComposedChart, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "./api";

type KPI={title:string;actual:number;plan:number|null;variance:number|null;achievement_pct:number|null;unit:string};
type Row={label:string;cells?:number;on_date:number;mtd:number;ytd:number};
type Overview={as_of:string;kpis:KPI[];distribution:Row[];rejection:Row[];yield_table:Row[]};
type Trends={production:any[];rejection:any[];yield:any[];wafer_loss:any[];breakage:Record<string,number>;monthly_average:any[]};
const fmt=(v:number|null|undefined,d=2)=>v==null?"N/A":Number(v).toLocaleString(undefined,{maximumFractionDigits:d});

function KpiCard({k}:{k:KPI}){const positive=k.variance==null?null:k.variance>=0;const Icon=positive==null?Minus:positive?ArrowUpRight:ArrowDownRight;const label=k.title==="Run rate"?"Required":"Plan";return <article className={`kpi ${positive==null?"neutral":positive?"positive":"negative"}`}><div className="kpiTop"><span>{k.title}</span><Icon/></div><div className="compare"><div><small>Actual</small><strong>{fmt(k.actual)}</strong><em>{k.unit}</em></div><i/><div><small>{label}</small><strong>{fmt(k.plan)}</strong><em>{k.unit}</em></div></div><footer><b>{k.variance==null?"Comparison unavailable":`${positive?"+":""}${fmt(k.variance)} ${k.unit}`}</b><span>{k.achievement_pct==null?"":`${fmt(k.achievement_pct)}% achieved`}</span></footer></article>}
function Chart({title,children}:{title:string;children:React.ReactNode}){return <section className="panel"><h2>{title}</h2><div className="chart">{children}</div></section>}
function TooltipBox({active,payload,label}:any){if(!active||!payload?.length)return null;return <div className="tooltip"><b>{label}</b>{payload.map((p:any)=><span key={p.dataKey} style={{color:p.color}}>{p.name}: {fmt(p.value)}</span>)}</div>}

export default function App(){
 const[tab,setTab]=useState("overview"),[years,setYears]=useState<string[]>([]),[fy,setFy]=useState(""),[overview,setOverview]=useState<Overview|null>(null),[trends,setTrends]=useState<Trends|null>(null),[error,setError]=useState(""),[refreshing,setRefreshing]=useState(false);
 const load=async(value:string)=>{const[o,t]=await Promise.all([api.get<Overview>(`/api/overview?fy=${encodeURIComponent(value)}`),api.get<Trends>(`/api/trends?fy=${encodeURIComponent(value)}`)]);setOverview(o);setTrends(t)};
 useEffect(()=>{api.get<{items:string[]}>("/api/financial-years").then(x=>{setYears(x.items);setFy(x.items[0]||"")}).catch(e=>setError(String(e)))},[]);
 useEffect(()=>{if(fy)load(fy).catch(e=>setError(String(e)))},[fy]);
 async function refresh(){setRefreshing(true);setError("");try{const job=await api.post<any>("/api/refresh");const timer=window.setInterval(async()=>{const status=await api.get<any>(`/api/refresh/${job.id}`);if(status.status==="completed"||status.status==="failed"){clearInterval(timer);setRefreshing(false);if(status.status==="failed")setError(status.error);else await load(fy)}},1500)}catch(e){setRefreshing(false);setError(String(e))}}
 const breakage=useMemo(()=>trends?Object.entries(trends.breakage).map(([name,value])=>({name:name.replace(/_/g," "),value})):[],[trends]);
 return <div className="app"><header><img src="/company_logo.png" alt="Company logo"/><div className="brand"><h1>SOLAR MANUFACTURING DASHBOARD</h1><p>Final Product · Production and Quality Intelligence</p></div><div className="controls"><label>Financial year<select value={fy} onChange={e=>setFy(e.target.value)}>{years.map(y=><option key={y}>{y}</option>)}</select></label><div className="asof">AS OF<b>{overview?.as_of||"-"}</b></div><button onClick={refresh} disabled={refreshing}><RefreshCw className={refreshing?"spin":""}/>{refreshing?"Refreshing":"Refresh SAP Data"}</button></div></header>{error&&<div className="error">{error}</div>}<nav><button className={tab==="overview"?"active":""} onClick={()=>setTab("overview")}>Overview</button><button className={tab==="trends"?"active":""} onClick={()=>setTab("trends")}>Trends</button></nav><main>
 {tab==="overview"&&overview&&<><div className="kpiGrid">{overview.kpis.map(k=><KpiCard key={k.title} k={k}/>)}</div><section className="panel"><h2>Production and Rejection Distribution</h2><div className="tableWrap"><table><thead><tr><th>Grade / Type</th><th>Cells</th><th>On Date</th><th>MTD</th><th>YTD</th></tr></thead><tbody><tr className="group"><th colSpan={5}>Production</th></tr>{overview.distribution.map(r=><tr key={r.label}><th>{r.label}</th><td>{fmt(r.cells,0)}</td><td>{fmt(r.on_date)}</td><td>{fmt(r.mtd)}</td><td>{fmt(r.ytd)}</td></tr>)}<tr className="group"><th colSpan={5}>Rejection</th></tr>{overview.rejection.map(r=><tr key={r.label}><th>{r.label}</th><td>—</td><td>{fmt(r.on_date,0)}</td><td>{fmt(r.mtd,0)}</td><td>{fmt(r.ytd,0)}</td></tr>)}</tbody></table></div></section><section className="panel"><h2>Yield Percentage</h2><div className="tableWrap"><table><thead><tr><th>Grade</th><th>On Date</th><th>MTD</th><th>YTD</th></tr></thead><tbody><tr className="group"><th colSpan={4}>Yield</th></tr>{overview.yield_table.map(r=><tr key={r.label} className={r.label==="Good Cells"?"total":""}><th>{r.label}</th><td>{fmt(r.on_date)}%</td><td>{fmt(r.mtd)}%</td><td>{fmt(r.ytd)}%</td></tr>)}</tbody></table></div></section></>}
 {tab==="trends"&&trends&&<><Chart title="Production Trend"><ResponsiveContainer><ComposedChart data={trends.production}><CartesianGrid stroke="#e5ebe6" vertical={false}/><XAxis dataKey="period"/><YAxis/><Tooltip content={<TooltipBox/>}/><Legend/><Bar dataKey="total_mw" fill="#8acb4a" name="Total MW"/><Line dataKey="a_mw" stroke="#006b3f" strokeWidth={2.5} dot={false} name="A Grade MW"/></ComposedChart></ResponsiveContainer></Chart><Chart title="Rejection Trend (%)"><ResponsiveContainer><LineChart data={trends.rejection}><CartesianGrid stroke="#e5ebe6" vertical={false}/><XAxis dataKey="period"/><YAxis/><Tooltip content={<TooltipBox/>}/><Legend/><Line dataKey="er_pct" stroke="#d84c5b" dot={false} name="ER %"/><Line dataKey="or_pct" stroke="#7857c9" dot={false} name="OR %"/><Line dataKey="for_pct" stroke="#f59e0b" dot={false} name="FO %"/><Line dataKey="breakage_pct" stroke="#64748b" dot={false} name="Breakage %"/></LineChart></ResponsiveContainer></Chart><Chart title="Yield Trend (%) · Dual Axis"><ResponsiveContainer><LineChart data={trends.yield}><CartesianGrid stroke="#e5ebe6" vertical={false}/><XAxis dataKey="period"/><YAxis yAxisId="left" domain={["auto","auto"]}/><YAxis yAxisId="right" orientation="right" domain={["auto","auto"]}/><Tooltip content={<TooltipBox/>}/><Legend/><Line yAxisId="left" dataKey="a_yield_pct" stroke="#006b3f" dot={false} name="A Grade %"/><Line yAxisId="left" dataKey="b_yield_pct" stroke="#1687e8" dot={false} name="B Grade %"/><Line yAxisId="right" dataKey="bel_yield_pct" stroke="#f59e0b" dot={false} name="B-EL %"/><Line yAxisId="right" dataKey="eb_yield_pct" stroke="#7c3aed" dot={false} name="EB %"/></LineChart></ResponsiveContainer></Chart><Chart title="Wafer Loss Trend (%)"><ResponsiveContainer><LineChart data={trends.wafer_loss}><CartesianGrid stroke="#e5ebe6" vertical={false}/><XAxis dataKey="period"/><YAxis/><Tooltip content={<TooltipBox/>}/><Line dataKey="wafer_loss_pct" stroke="#d84c5b" strokeWidth={3} dot={false} name="Wafer Loss %"/></LineChart></ResponsiveContainer></Chart><Chart title="Breakage Distribution"><ResponsiveContainer><BarChart data={breakage}><CartesianGrid stroke="#e5ebe6" vertical={false}/><XAxis dataKey="name"/><YAxis/><Tooltip content={<TooltipBox/>}/><Bar dataKey="value" fill="#79c143" name="Breakage Cells"/></BarChart></ResponsiveContainer></Chart><Chart title="Monthly Average MW Production per Day"><ResponsiveContainer><LineChart data={trends.monthly_average}><CartesianGrid stroke="#e5ebe6" vertical={false}/><XAxis dataKey="period"/><YAxis domain={["auto","auto"]}/><Tooltip content={<TooltipBox/>}/><Line dataKey="avg_mw_per_day" stroke="#006b3f" strokeWidth={3} dot={{r:4}} name="Average MW/day"/></LineChart></ResponsiveContainer></Chart></>}
 </main></div>
}
