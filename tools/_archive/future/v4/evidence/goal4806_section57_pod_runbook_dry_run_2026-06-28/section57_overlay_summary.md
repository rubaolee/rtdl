# RayJoin Section 5.7 Overlay 8/8 Summary

Dataset root: `data\rayjoin_section57_cdb`

Timing caveat: Paper Table 4 values are historical reference numbers. Local author_rt rows are measured process wall times. RTDL rows are warm-cache medians under the selected protocol.

## Coverage

| Metric | Value |
|---|---:|
| overlay_pairs_total | 1 |
| overlay_pairs_complete | 0 |
| overlay_pairs_incomplete | 1 |

## Matrix

| Pair | Paper RayJoin Processing (Preprocess) | Local Author RT Process | RTDL OptiX Total | RTDL Embree Total | V4+Numba Total | V4+Numba Status | RTDL LSI Count Match | Complete |
|---|---:|---:|---:|---:|---:|---|---|---:|
| County x Zipcode | 0.12 (0.07) |  |  |  |  | `` |  | False |
