# Goal3203: RayJoin Compact Route Count-Only Timing

Date: 2026-06-03

## Purpose

Goal3203 measures the `prepared_optix_compact_grouped_count` app route in
count-only mode, with correctness validation separated from the measured runs.

Goal3201 measured the route with compact validation rows copied back on every
repetition. Goal3203 asks the next narrower question: what does the route look
like when the app requests counts only and does not ask Python to materialize
compact result rows during the measured repetitions?

This remains an internal route timing probe. It is not a public speedup claim,
not a RayJoin paper reproduction claim, not a true-zero-copy claim, and not a
release gate.

## Setup

Pod artifact:

- `docs/reports/goal3203_rayjoin_compact_route_count_only_timing_2026-06-03.json`
- Commit under test: `c4c11f28`
- Route: `prepared_optix_compact_grouped_count`
- Measured repetitions per scale: `7`
- Measured route: `include_rows=False`
- Validation route: one `include_rows=True` pass per scale before measured
  count-only repetitions.
- Workload: authored all-crossing direct segment pairs.

The measured route still validates host-visible scalar metadata:

- candidate row count equals `n_left * n_right`,
- compact group count equals `n_left`,
- compact grouped-count columns are reported device-resident.

The exact count sum is validated once per scale by copying compact rows in the
separate validation pass.

## Results

| Scale | Validation Pass (s) | Count-Only Warm-Up (s) | Median Count-Only Total (s) | Min (s) | Max (s) | Candidate Pairs | Compact Count Rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 512 x 512 | 1.1018056124448776 | 0.006388094276189804 | 0.00587533600628376 | 0.005779426544904709 | 0.006181471049785614 | 262144 | 512 |
| 1024 x 1024 | 0.011608555912971497 | 0.010905817151069641 | 0.010664353147149086 | 0.010478835552930832 | 0.010722501203417778 | 1048576 | 1024 |
| 2048 x 2048 | 0.02238679863512516 | 0.03284996189177036 | 0.020370308309793472 | 0.02024773135781288 | 0.0245790034532547 | 4194304 | 2048 |
| 4096 x 4096 | 0.06430059112608433 | 0.048877179622650146 | 0.04079877771437168 | 0.04003002308309078 | 0.054019730538129807 | 16777216 | 4096 |

All rows set `all_match_expected_counts: true`.

## Interpretation

The count-only route is clean:

- measured payloads do not contain a `rows` field,
- compact grouped-count columns remain the output contract,
- the app avoids full witness-row materialization,
- RayJoin-specific left-ID interpretation remains in Python.

Compared with Goal3201, removing per-repetition compact validation-row copy is
useful but not the dominant remaining cost. The per-repetition phase timings
show that repeated query packing and static right-scene preparation are now
larger than the compact grouped-count continuation itself. At `4096 x 4096`,
representative measured repetitions spend roughly:

- `0.0136s` to `0.0141s` in query packing,
- `0.0148s` to `0.0278s` in static-scene preparation,
- `0.0062s` to `0.0080s` in candidate device-column production,
- about `0.00037s` in compact grouped-count continuation.

That points to the next engineering target: a reusable prepared app route or
handle that can keep the right-side scene prepared across repeated count
queries, without moving RayJoin logic into the native engine.

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
