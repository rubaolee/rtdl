# Goal3201: RayJoin Compact Route Steady-State Timing

Date: 2026-06-03

## Purpose

Goal3201 reruns the Goal3199 app-route timing with warm-up separated from
measured repetitions.

The target is still narrow: validate the steady-state behavior of the Spatial
RayJoin benchmark route that uses generic segment-pair candidate device columns
followed by generic compact grouped-count device columns.

This is internal performance evidence for the route shape. It is not a public
speedup claim, not a RayJoin paper reproduction claim, and not a release gate.
In short: this is not a public speedup claim.

## Setup

Pod artifact:

- `docs/reports/goal3201_rayjoin_compact_route_steady_state_timing_2026-06-03.json`
- Commit under test: `314ff79f`
- Route: `prepared_optix_compact_grouped_count`
- Repetitions per scale: `5`
- Workload: authored all-crossing direct segment pairs.
- Validation: compact `group_key[]` / `count[]` columns were copied back after
  the device-resident grouped-count path to verify exact expected counts.

The route intentionally used original left IDs of `10000 + i`, so the Python
app layer had to remap them to the generic primitive's direct-address group-key
contract and then map compact results back to the original IDs.

## Results

| Scale | Warm-Up (s) | Median Measured Total (s) | Min (s) | Max (s) | Candidate Pairs | Compact Count Rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 512 x 512 | 0.9906987678259611 | 0.00638449564576149 | 0.006181169301271439 | 0.012239031493663788 | 262144 | 512 |
| 1024 x 1024 | 0.01156957820057869 | 0.0112311951816082 | 0.011097695678472519 | 0.011709483340382576 | 1048576 | 1024 |
| 2048 x 2048 | 0.022650089114904404 | 0.02155112847685814 | 0.021330196410417557 | 0.03589046746492386 | 4194304 | 2048 |
| 4096 x 4096 | 0.04441756755113602 | 0.045530401170253754 | 0.04226326756179333 | 0.0613513495773077 | 16777216 | 4096 |

All rows set `all_match_expected_counts: true`.

At `4096 x 4096`, the app route validated 16,777,216 candidate-pair counts
while returning a compact grouped-count surface of 4,096 rows.

## Interpretation

Goal3199 showed the first-use setup artifact. Goal3201 removes that ambiguity:

- the 512 warm-up row is nearly one second, but its measured repetitions settle
  to millisecond-scale route execution,
- compact count output scales with populated left groups rather than candidate
  pairs,
- app-level non-contiguous left-ID handling remains outside the native engine,
- the native/runtime primitive surface remains generic.

The median totals include Python app orchestration, query packing, OptiX
candidate-device-column production, compact grouped-count continuation, and
validation copies of compact columns only. They do not include materialization
of full witness rows.

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
