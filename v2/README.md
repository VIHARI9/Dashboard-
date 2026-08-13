# Solar Cell Manufacturing Dashboard

Place these files together with the five workbooks, install dependencies, and run `streamlit run app.py`.

Expected workbook names: `Daywise Data.xlsx`, `Daywise MW Report.xlsx`, `Monthwise MW Report.xlsx`, `Monthwise Report.xlsx`, and `Plan.xlsx`.

The loader detects the header row, normalizes headers, maps them to canonical fields, parses daily/monthly periods, and reports missing sources or validation warnings in **Diagnostics**. Overview uses the latest common daily date. Production and Analytics use independent date ranges.
