import datetime
import re
from pathlib import Path
import pandas as pd

EXPECTED_FILES={
 'day_quality':'Daywise Data.xlsx','day_mw':'Daywise MW Report.xlsx',
 'month_mw':'Monthwise MW Report.xlsx','month_quality':'Monthwise Report.xlsx','plan':'Plan.xlsx'}

def normalize_header(v):
 s='' if v is None else str(v).strip().lower().replace('\n',' ')
 s=re.sub(r'\bb[\s_-]*el\b','bel',s); s=s.replace('percentage','pct').replace('percent','pct').replace('%',' pct ')
 return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9]+',' ',s)).strip()

ALIASES={
 'a_cells':['a grade','a grade saleable'],'b_cells':['b grade','b grade saleable'],
 'bel_cells':['bel grade','bel grade saleable'],'eb_cells':['eb grade','eb grade saleable'],
 'total_cells':['total production','total cells'],
 'a_mw':['a grade saleable mw','a grade mw'],'b_mw':['b grade saleable mw','b grade mw'],
 'bel_mw':['bel grade saleable mw','bel grade mw'],'eb_mw':['eb grade saleable mw','eb grade mw'],
 'total_mw':['total production mw','total mw'],
 'er_rejection':['er rejection'],'for_rejection':['for rejection'],
 'erq_rejection':['er q rejection'],'total_rejection':['total rejection'],
 'rw_breakage':['r w breakage','rw breakage'],'bw_breakage':['b w breakage','bw breakage'],
 'alw_breakage':['al w breakage','alw breakage'],'agw_breakage':['ag w breakage','agw breakage'],
 'cell_breakage':['cell breakage'],'total_breakage':['total breakages','total breakage'],
 'a_yield_pct':['a grade yield pct'],'b_yield_pct':['b grade yield pct'],
 'bel_yield_pct':['bel grade yield pct'],'eb_yield_pct':['eb grade yield pct'],
 'er_pct':['er pct'],'for_pct':['for pct'],'breakage_pct':['breakage pct'],
 'a_target_mw':['a grade'],'b_target_mw':['b grade'],'bel_target_mw':['bel grade'],
 'eb_target_mw':['eb grade'],'total_target_mw':['total target']}
ALIASES={k:{normalize_header(x) for x in v} for k,v in ALIASES.items()}

def map_columns(df, role):
 cols=list(df.columns); rename={cols[0]:'period'}; used=set()
 allowed=set(ALIASES)
 if role=='plan': allowed={'a_target_mw','b_target_mw','bel_target_mw','eb_target_mw','total_target_mw'}
 elif role in ('day_mw','month_mw'): allowed={'a_cells','b_cells','bel_cells','eb_cells','total_cells','a_mw','b_mw','bel_mw','eb_mw','total_mw'}
 elif role in ('day_quality','month_quality'): allowed-=set(['a_mw','b_mw','bel_mw','eb_mw','total_mw','a_target_mw','b_target_mw','bel_target_mw','eb_target_mw','total_target_mw'])
 for col in cols[1:]:
  n=normalize_header(col); matches=[k for k in allowed if n in ALIASES[k]]
  if len(matches)>1: raise ValueError(f'Ambiguous mapping in {role}: {col!r} -> {matches}')
  if len(matches)==1:
   key=matches[0]
   if key in used: raise ValueError(f'Duplicate mapping in {role}: {key}')
   rename[col]=key; used.add(key)
 return rename

def parse_period(series, grain):
    if grain == "day":
        return pd.to_datetime(
            series,
            dayfirst=True,
            errors="coerce",
        ).dt.normalize()

    if grain == "month":

        def parse_month(value):
            if pd.isna(value):
                return pd.NaT

            # Excel may already return a real date object.
            if isinstance(
                value,
                (
                    pd.Timestamp,
                    datetime.datetime,
                    datetime.date,
                ),
            ):
                return (
                    pd.Timestamp(value)
                    .to_period("M")
                    .to_timestamp()
                )

            text = str(value).strip()

            # Supported source month formats.
            formats = (
                "%B %Y",   # May 2025
                "%b %Y",   # May 2025
                "%b-%y",   # May-25
                "%b-%Y",   # May-2025
                "%m/%d/%Y",
                "%d/%m/%Y",
                "%m-%d-%Y",
                "%d-%m-%Y",
            )

            for date_format in formats:
                parsed = pd.to_datetime(
                    text,
                    format=date_format,
                    errors="coerce",
                )

                if not pd.isna(parsed):
                    return (
                        parsed
                        .to_period("M")
                        .to_timestamp()
                    )

            # Controlled fallback for unusual valid values.
            parsed = pd.to_datetime(
                text,
                errors="coerce",
            )

            if pd.isna(parsed):
                return pd.NaT

            return (
                parsed
                .to_period("M")
                .to_timestamp()
            )

        return series.apply(parse_month)

    raise ValueError(
        f"Unsupported time grain: {grain}"
    )