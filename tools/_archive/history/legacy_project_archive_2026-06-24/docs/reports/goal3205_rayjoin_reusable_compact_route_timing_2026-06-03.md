# Goal3205: RayJoin Reusable Compact Route Timing

Date: 2026-06-03

## Purpose

Goal3205 measures the Goal3204 reusable prepared Python handle for the
Spatial RayJoin compact grouped-count route.

Goal3203 showed that count-only execution avoids validation-row materialization,
but repeated static right-scene preparation remained a large app-route cost.
Goal3205 asks whether a Python app-layer prepared handle can remove that
repeated preparation cost while preserving the app-agnostic native boundary.

This remains internal performance evidence for a reference route. It is not a
public speedup claim, not a RayJoin paper reproduction claim, not a true-zero-copy
claim, and not a release gate.

## Setup

Pod artifact:

- `docs/reports/goal3205_rayjoin_reusable_compact_route_timing_2026-06-03.json`
- Commit under test: `da247fe8`
- Route: `prepared_optix_compact_grouped_count_reuse`
- Measured repetitions per scale: `9`
- Measured route: `include_rows=False`
- Validation route: one `include_rows=True` pass per scale through the same
  prepared handle.
- Workload: authored all-crossing direct segment pairs.

The reusable handle prepares the right-side segment scene once per scale:

```python
with prepare_rayjoin_optix_compact_grouped_count_segments(right_segments) as prepared:
    payload = prepared.run(left_segments, include_rows=False)
```

The native engine still sees generic segment-pair candidate columns and generic
compact grouped-count columns. RayJoin route policy, left-ID remapping, and
right-scene reuse are Python app-layer responsibilities.

## Results

| Scale | Prepare Once (s) | Validation Pass (s) | Median Reusable Count-Only Total (s) | Min (s) | Max (s) | Candidate Pairs | Compact Count Rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 512 x 512 | 0.4619568232446909 | 0.5220995508134365 | 0.0035278499126434326 | 0.003497151657938957 | 0.0038161426782608032 | 262144 | 512 |
| 1024 x 1024 | 0.004440559074282646 | 0.007221067324280739 | 0.0099519994109869 | 0.006553415209054947 | 0.013484282419085503 | 1048576 | 1024 |
| 2048 x 2048 | 0.008918792009353638 | 0.019478492438793182 | 0.012733235955238342 | 0.012594824656844139 | 0.024629956111311913 | 4194304 | 2048 |
| 4096 x 4096 | 0.0156503114849329 | 0.038600724190473557 | 0.02565891481935978 | 0.024932274594902992 | 0.03802254982292652 | 16777216 | 4096 |

All rows set `all_match_expected_counts: true`.

## Comparison With Goal3203

| Scale | Goal3203 One-Shot Count-Only Median (s) | Goal3205 Reusable Prepared Median (s) | Internal Ratio |
| --- | ---: | ---: | ---: |
| 512 x 512 | 0.00587533600628376 | 0.0035278499126434326 | 0.6004514763887198 |
| 1024 x 1024 | 0.010664353147149086 | 0.0099519994109869 | 0.9332010111837606 |
| 2048 x 2048 | 0.020370308309793472 | 0.012733235955238342 | 0.6249908216164234 |
| 4096 x 4096 | 0.04079877771437168 | 0.02565891481935978 | 0.6289149369047468 |

## Interpretation

The reusable prepared handle solves the largest cost called out by Goal3203:
right-side scene preparation is now paid once and is absent from each measured
query payload's `phases_sec`.

At `4096 x 4096`, the median measured count-only route falls from
`0.04079877771437168s` to `0.02565891481935978s` for the same all-crossing
direct segment-pair shape.

The new bottleneck is query packing. Representative `4096 x 4096` measured
repetitions spend about:

- `0.0137s` to `0.0157s` in query packing,
- about `0.0062s` to `0.0065s` in candidate device-column production,
- about `0.00036s` to `0.00039s` in compact grouped-count continuation.

The next useful engineering target is a packed-left query reuse path or a
caller-supplied packed segment input contract, still at the Python/app boundary
and still without adding RayJoin-specific native logic.

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
