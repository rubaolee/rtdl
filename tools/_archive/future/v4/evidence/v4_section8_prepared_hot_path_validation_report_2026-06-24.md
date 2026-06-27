# V4 Section 8 Prepared Hot-Path Validation Report

Date: 2026-06-24
Status: measured; revised hot-path gate passed; external review required before credit

## Question

Once the fixed-radius count-threshold scene is prepared, does the compact summary hot path beat the separated neighbor-row emit+reduce path by at least 1.5x on serious sizes?

## Evidence Files

- Revised protocol: `future/v4/rtdl_v4_0_section8_prepared_hot_path_protocol_2026-06-24.md`
- Raw result JSON: `future/v4/evidence/v4_section8_prepared_hot_path_result_2026-06-24.json`
- Progress log: `future/v4/evidence/v4_section8_prepared_hot_path_progress_2026-06-24.log`
- Harness: `scripts/v4_section8_prepared_hot_path_validation.py`

## Timing Boundary

Excluded from timed windows:

- case construction
- oracle construction/comparison
- prepared scene creation

Included in timed windows:

- baseline: OptiX neighbor-row emit plus Python `reduce_rows(count)` conversion into density rows
- candidate: prepared native fixed-radius count-threshold query plus Python conversion from compact count rows into density rows

## Results

| copies | points | correctness | rows emit+reduce median | summary prepared hot median | speedup |
| ---: | ---: | :---: | ---: | ---: | ---: |
| 8192 | 65,536 | pass | 0.470929s | 0.284516s | 1.655x |
| 32768 | 262,144 | pass | 2.115525s | 1.193533s | 1.772x |
| 131072 | 1,048,576 | pass | 10.425638s | 5.290915s | 1.970x |

## Gate Outcome

Revised prepared hot-path gate:

- summary hot path must be at least 1.5x over rows emit+reduce on at least two serious sizes: pass, all three sizes passed.
- correctness must pass: pass.
- candidate must use generic fixed-radius count-threshold continuation: pass.

Overall revised gate: `pass`

Harness next-step field: `external_review_then_consider_summary_hot_path_credit`

## Interpretation

The original whole-call app-route gate still failed. This revised result answers a narrower question: when prepared-scene setup is outside the timed hot path, the compact summary continuation is materially faster than separated row emit+reduce. This supports prepared-session summary credit, not whole-call app-route credit.

No V4 release claim is authorized by this report.

