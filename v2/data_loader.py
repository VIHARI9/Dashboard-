from pathlib import Path
import pandas as pd
from mapping import EXPECTED_FILES, normalize_header, map_columns, parse_period

TOKENS={'date','month','total production','total production mw','total rejection','total breakages','total target'}

def detect_header(path, sheet, scan=30):
 raw=pd.read_excel(path,sheet_name=sheet,header=None,nrows=scan,engine='openpyxl')
 best=(-1,-1)
 for i,row in raw.iterrows():
  vals=[normalize_header(x) for x in row if pd.notna(x)]
  score=sum(v in TOKENS or any(t in v for t in TOKENS) for v in vals)+len(vals)*.05
  if score>best[0]: best=(score,i)
 if best[0]<1: raise ValueError(f'No credible header in {path.name} / {sheet}')
 return best[1]

def load_one(path, role):
 xls=pd.ExcelFile(path,engine='openpyxl'); sheet=xls.sheet_names[0]; header=detect_header(path,sheet)
 raw=pd.read_excel(path,sheet_name=sheet,header=header,engine='openpyxl').dropna(how='all').dropna(axis=1,how='all')
 original=raw.copy(); mapped=raw.rename(columns=map_columns(raw,role)); grain='day' if role.startswith('day_') else 'month'
 mapped['period']=parse_period(mapped['period'],grain)
 mapped=mapped.dropna(subset=['period']).copy(); mapped['time_grain']=grain
 for c in mapped.columns:
  if c not in ('period','time_grain'): mapped[c]=pd.to_numeric(mapped[c],errors='coerce')
 return {'role':role,'file':path.name,'sheet':sheet,'header_row':header+1,'raw':original,'data':mapped,'mapping':{str(k):v for k,v in map_columns(raw,role).items()}}

def load_all(app_dir):
 out={}; errors=[]
 for role,name in EXPECTED_FILES.items():
  path=Path(app_dir)/name
  if not path.exists(): errors.append(f'Missing: {name}'); continue
  try: out[role]=load_one(path,role)
  except Exception as e: errors.append(f'{name}: {e}')
 return out,errors
