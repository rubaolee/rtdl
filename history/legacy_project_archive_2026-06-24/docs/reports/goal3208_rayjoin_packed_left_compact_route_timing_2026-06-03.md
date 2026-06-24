# Goal3208: RayJoin Packed-Left Compact Route Timing

Date: 2026-06-03

## Purpose

Goal3208 measures the packed-left version of the reusable Spatial RayJoin
compact grouped-count route.

Goal3205 removed repeated right-side scene preparation. Its remaining dominant
cost was Python query packing. Goal3208 lets the caller prepack the left query
batch once and run repeated count-only queries through:

```python
packed_left = pack_rayjoin_optix_compact_grouped_count_left_segments(left_segments)
with prepare_rayjoin_optix_compact_grouped_count_segments(right_segments) as prepared:
    payload = prepared.run_packed_left(packed_left, include_rows=False)
```

This is still Python app-layer reuse. The native engine still executes generic
segment-pair candidate device columns and generic compact grouped-count device
columns.

This is not a public speedup claim, not a RayJoin paper reproduction claim, not
a true-zero-copy claim, and not a release gate.

## Setup

Pod artifact:

- `docs/reports/goal3208_rayjoin_packed_left_compact_route_timing_2026-06-03.json`
- Commit under test: `b97553c0`
- Route: `prepared_optix_compact_grouped_count_reuse/run_packed_left`
- Measured repetitions per scale: `11`
- Measured route: `include_rows=False`
- Validation route: one `include_rows=True` pass per scale through the same
  prepared-right / packed-left handles.
- Workload: authored all-crossing direct segment pairs.

## Results

| Scale | Pack Left Once (s) | Prepare Right Once (s) | Median Packed-Left Total (s) | Min (s) | Max (s) | Candidate Pairs | Compact Count Rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 512 x 512 | 0.002429187297821045 | 0.47890207916498184 | 0.0021709520369768143 | 0.0014747362583875656 | 0.011267580091953278 | 262144 | 512 |
| 1024 x 1024 | 0.003810189664363861 | 0.004409259185194969 | 0.0025483760982751846 | 0.002510441467165947 | 0.002570725977420807 | 1048576 | 1024 |
| 2048 x 2048 | 0.0078287273645401 | 0.008337311446666718 | 0.005303880199790001 | 0.00526592880487442 | 0.005417494103312492 | 4194304 | 2048 |
| 4096 x 4096 | 0.015463858842849731 | 0.022470535710453987 | 0.012753259390592575 | 0.012721503153443336 | 0.012788509950041771 | 16777216 | 4096 |

All rows set `all_match_expected_counts: true`.

## Comparison Chain

| Scale | Goal3203 One-Shot Count-Only Median (s) | Goal3205 Prepared-Right Median (s) | Goal3208 Prepared-Right + Packed-Left Median (s) |
| --- | ---: | ---: | ---: |
| 512 x 512 | 0.00587533600628376 | 0.0035278499126434326 | 0.0021709520369768143 |
| 1024 x 1024 | 0.010664353147149086 | 0.0099519994109869 | 0.0025483760982751846 |
| 2048 x 2048 | 0.020370308309793472 | 0.012733235955238342 | 0.005303880199790001 |
| 4096 x 4096 | 0.04079877771437168 | 0.02565891481935978 | 0.012753259390592575 |

At `4096 x 4096`, the packed-left route is about `0.3126x` of the one-shot
count-only median and about `0.4970x` of the prepared-right-only median.

## Interpretation

This result confirms the performance diagnosis from Goal3205:

- right-side preparation reuse matters,
- left-side packing reuse matters,
- after both are removed from repeated calls, candidate device-column traversal
  is the dominant measured work,
- compact grouped-count continuation remains small, about `0.00033s` at
  `4096 x 4096`.

Representative `4096 x 4096` repetitions spend roughly:

- `0.00984s` to `0.00988s` in generic candidate device-column production,
- `0.000326s` to `0.000346s` in compact grouped-count continuation.

The next engineering question is whether the candidate-device-column producer
itself can be improved generically for same-shape segment-pair count streams,
without adding RayJoin-specific native logic.

## Boundaries

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `whole_app_speedup_claim_authorized: False`
- `rayjoin_paper_reproduction_claim_authorized: False`

This timing does not prove:

- final Spatial RayJoin semantics,
- broad RayJoin paper parity,
- public whole-app speedup,
- true zero-copy,
- release readiness.
