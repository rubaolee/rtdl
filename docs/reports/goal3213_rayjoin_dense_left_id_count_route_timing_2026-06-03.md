# Goal3213: RayJoin Dense Left-ID Count Route Timing

Date: 2026-06-03

## Purpose

Goal3213 measures the app route that uses the Goal3210 fused generic
segment-pair left-id count primitive:

`prepared.run_packed_left_dense_count(...)`

This route prepares the right-side scene once, packs the left query batch once,
then counts segment-pair hits per remapped left ID during traversal. It avoids
both:

- full pair-column materialization (`left_ids[]` / `right_ids[]`),
- compact grouped-count continuation after pair-column production.

This is a generic segment-pair count route, not a RayJoin-specific native
kernel.

This is not a public speedup claim, not a RayJoin paper reproduction claim, not
a true-zero-copy claim, and not a release gate.

## Setup

Pod artifact:

- `docs/reports/goal3213_rayjoin_dense_left_id_count_route_timing_2026-06-03.json`
- Commit under test: `03209c08`
- Route: `prepared_optix_left_id_dense_count_reuse/run_packed_left_dense_count`
- Measured repetitions per scale: `11`
- Measured route: `include_rows=False`
- Validation route: one `include_rows=True` pass per scale through the same
  prepared-right / packed-left handles.
- Workload: authored all-crossing direct segment pairs.

## Results

| Scale | Pack Left Once (s) | Prepare Right Once (s) | Median Dense Count Total (s) | Min (s) | Max (s) | Candidate Pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 512 x 512 | 0.0019062906503677368 | 0.6236594039946795 | 0.0008123423904180527 | 0.0008045900613069534 | 0.0008428115397691727 | 262144 |
| 1024 x 1024 | 0.0038582049310207367 | 0.004209557548165321 | 0.0015707220882177353 | 0.0015486795455217361 | 0.0016242433339357376 | 1048576 |
| 2048 x 2048 | 0.007645152509212494 | 0.008216673508286476 | 0.0029755420982837677 | 0.0029680412262678146 | 0.00299140065908432 | 4194304 |
| 4096 x 4096 | 0.015611471608281136 | 0.01607738994061947 | 0.005745925009250641 | 0.005710190162062645 | 0.005770867690443993 | 16777216 |

All rows set `all_match_expected_counts: true`.

## Comparison Chain

| Scale | Goal3203 One-Shot Count-Only Median (s) | Goal3205 Prepared-Right Median (s) | Goal3208 Prepared + Packed Compact Median (s) | Goal3213 Fused Dense Count Median (s) |
| --- | ---: | ---: | ---: | ---: |
| 512 x 512 | 0.00587533600628376 | 0.0035278499126434326 | 0.0021709520369768143 | 0.0008123423904180527 |
| 1024 x 1024 | 0.010664353147149086 | 0.0099519994109869 | 0.0025483760982751846 | 0.0015707220882177353 |
| 2048 x 2048 | 0.020370308309793472 | 0.012733235955238342 | 0.005303880199790001 | 0.0029755420982837677 |
| 4096 x 4096 | 0.04079877771437168 | 0.02565891481935978 | 0.012753259390592575 | 0.005745925009250641 |

All four comparison-chain artifacts record `include_rows_measured: false` for
the measured repetitions and reserve `include_rows=True` for validation passes.

At `4096 x 4096`, the fused dense-count route is:

- about `0.1408x` of the Goal3203 one-shot count-only median,
- about `0.2239x` of the Goal3205 prepared-right median,
- about `0.4506x` of the Goal3208 prepared + packed compact median.

## Interpretation

This is the strongest RayJoin-count route so far on the current v2.x basis.

The performance reason is clear: when the application only needs counts per
left segment, the engine should not emit a pair row stream and then reduce it.
The generic fused primitive counts by remapped left ID during traversal and
returns a dense count column.

At `4096 x 4096`, measured repetitions spend about `0.0057s` in the fused
dense-count path. The compact grouped-count continuation is no longer needed
for this count-only contract.

The app-specific parts remain outside native code:

- original left IDs are remapped in Python,
- route choice stays in Python,
- RayJoin interpretation stays in Python,
- native code exposes a generic segment-pair count primitive.

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
