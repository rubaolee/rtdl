# RayJoin Section 5.7 Overlay 8/8 Summary

Dataset root: `data\rayjoin_section57_cdb`

Timing caveat: Paper Table 4 values are historical reference numbers. Local author_rt rows are measured process wall times. RTDL rows are warm-cache medians under the selected protocol.

## Coverage

| Metric | Value |
|---|---:|
| overlay_pairs_total | 8 |
| overlay_pairs_complete | 0 |
| overlay_pairs_incomplete | 8 |

## Matrix

| Pair | Paper RayJoin Processing (Preprocess) | Local Author RT Process | RTDL OptiX Total | RTDL Embree Total | V4+Numba Total | V4+Numba Status | RTDL LSI Count Match | Complete |
|---|---:|---:|---:|---:|---:|---|---|---:|
| County x Zipcode | 0.12 (0.07) |  |  |  |  | `` |  | False |
| Block x Water | 0.23 (0.12) |  |  |  |  | `` |  | False |
| LKAF x PKAF | 0.01 (0.01) |  |  |  |  | `` |  | False |
| LKAS x PKAS | 0.04 (0.05) |  |  |  |  | `` |  | False |
| LKAU x PKAU | 0.01 (0.01) |  |  |  |  | `` |  | False |
| LKEU x PKEU | 0.2 (0.2) |  |  |  |  | `` |  | False |
| LKNA x PKNA | 0.25 (0.21) |  |  |  |  | `` |  | False |
| LKSA x PKSA | 0.02 (0.01) |  |  |  |  | `` |  | False |
