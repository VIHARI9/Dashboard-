# Mapping report

Three workbooks were available during development: Daywise MW Report, Monthwise Report, and Plan. Daywise Data and Monthwise MW Report were not available and are therefore mapped dynamically when present.

- Daywise MW: DATE -> period; grade saleable counts -> grade cell fields; grade MW fields -> grade MW fields; total production MW -> total_mw.
- Monthwise quality: MONTH -> period; production/rejection/breakage/yield fields -> corresponding canonical fields.
- Plan: Month -> period; grade targets and Total Target -> target MW fields.

The Diagnostics panel displays exact mappings and validation warnings at runtime.
