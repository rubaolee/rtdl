# Goal3199: RayJoin Compact Route App Timing Probe

Date: 2026-06-03

## Purpose

Goal3199 records a bounded pod timing probe for the Goal3197 app-facing
`prepared_optix_compact_grouped_count` route.

The question was narrow: after the compact grouped-count primitive is exposed
through the Spatial RayJoin benchmark app, does the app route preserve the
compact device-resident count surface and avoid materializing the full
candidate row stream when the user asks for counts only?

This is not a public speedup claim, not a RayJoin paper reproduction claim, and
not a release gate.

## Setup

Pod artifact:

- `docs/reports/goal3199_rayjoin_compact_route_app_timing_2026-06-03.json`
- Commit under test: `f0607849`
- Pod repository: `/root/rtdl_goal3151`
- OptiX library: `/root/rtdl_goal3151/build/librtdl_optix.so`
- Python: `/root/venvs/rtdl_goal3154/bin/python`

The app route ran:

- `run_rayjoin_prepared_optix_compact_grouped_count_segments(...)`
- authored all-crossing 2D segment-pair inputs,
- dense original left IDs (`10000 + i`) to exercise the Python remap boundary,
- `include_rows=True` for validation, so compact columns were copied back only
  after the resident grouped-count path completed.

The generic native/runtime path still sees:

- segment-pair candidate device columns,
- compact `group_key[]` / `count[]` grouped-count device columns,
- direct-address group capacity after Python-side left-ID remapping.

RayJoin workload naming and ID remapping remain in the Python app layer.

## Results

| Scale | App Route Total (s) | Candidate Rows | Compact Count Rows | Count Sum | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| 512 x 512 | 1.0348584651947021 | 262144 | 512 | 262144 | Includes first-use OptiX/setup warm-up cost. |
| 1024 x 1024 | 0.012706095352768898 | 1048576 | 1024 | 1048576 | Steady route behavior after warm-up. |
| 2048 x 2048 | 0.02264302410185337 | 4194304 | 2048 | 4194304 | Steady route behavior after warm-up. |

All rows set `all_match_expected_counts: true`.

The `2048 x 2048` app route produced the same count total as 4,194,304
candidate pairs, while the count output surface remained 2,048 compact grouped
count rows.

## Interpretation

This confirms that the new app route is wired to the intended compact
device-column contract:

- the app can request per-left segment counts without returning full witness
  rows as its primary output,
- the primitive output surface scales with the number of populated groups, not
  with the candidate pair stream,
- Python owns RayJoin naming, route selection, and non-contiguous input ID
  remapping,
- the native engine remains app-agnostic.

The first scale is intentionally not treated as steady-state performance
evidence because it includes first-use setup cost. A follow-up steady-state
timing goal should separate warm-up from repeated route execution.

## Boundaries

Boundary flags remain:

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `whole_app_speedup_claim_authorized: False`
- `rayjoin_paper_reproduction_claim_authorized: False`

This probe does not prove:

- final Spatial RayJoin semantics,
- broad RayJoin paper parity,
- whole-app speedup,
- true zero-copy,
- release readiness.
