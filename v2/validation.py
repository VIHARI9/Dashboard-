import numpy as np

def validate_dataset(item):
 df=item['data']; issues=[]
 dup=int(df['period'].duplicated().sum())
 if dup: issues.append(f'{dup} duplicate periods')
 numeric=[c for c in df.columns if c not in ('period','time_grain')]
 neg=int((df[numeric]<0).sum().sum()) if numeric else 0
 if neg: issues.append(f'{neg} negative values')
 checks=[('total_cells',['a_cells','b_cells','bel_cells','eb_cells'],1),('total_mw',['a_mw','b_mw','bel_mw','eb_mw'],.02),('total_rejection',['er_rejection','for_rejection','erq_rejection'],1),('total_breakage',['rw_breakage','bw_breakage','alw_breakage','agw_breakage','cell_breakage'],1)]
 for total,parts,tol in checks:
  if total in df and all(x in df for x in parts):
   n=int(((df[total]-df[parts].sum(axis=1)).abs()>tol).sum())
   if n: issues.append(f'{n} {total} component mismatches')
 return issues
