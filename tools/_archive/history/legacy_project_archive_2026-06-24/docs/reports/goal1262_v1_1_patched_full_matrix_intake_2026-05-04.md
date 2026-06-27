# Goal1262 v1.1 Patched Full Matrix Intake

Date: 2026-05-04

Valid: `True`
Public wording authorized: `False`
Release gate authorized: `False`

This report interprets the patched v1.1 Embree/OptiX full-matrix rerun on the
RTX A5000 pod after Goal1261 fixes. It supersedes the failed-row status in
Goal1260 for `database_analytics` 100k and `polygon_set_jaccard` 8192.

## Artifact

- archive: `docs/reports/goal1261_full_matrix_2026-05-04/goal1261_full_matrix.tgz`
- sha256: see `docs/reports/goal1261_full_matrix_2026-05-04/goal1261_full_matrix.tgz.sha256`
- extracted directory: `docs/reports/goal1261_full_matrix_2026-05-04/goal1261_full_matrix/`
- status file: `docs/reports/goal1261_full_matrix_2026-05-04/goal1261_full_matrix/status_summary.json`

## Status

- status count: `16`
- failed count: `0`
- failed labels: `[]`

All target rows completed for both Embree and OptiX at the selected scales.

## Timing Table

Ratios are `OptiX / Embree`; values below `1.0` mean OptiX is faster.

| Row | Scale | Embree sec | OptiX sec | Ratio | Correctness |
| --- | ---: | ---: | ---: | ---: | --- |
| DB compact summary, one-shot total | 30000 | `3.193151` | `4.205712` | `1.317` | pass |
| DB compact summary, warm query median | 30000 | `0.325254` | `0.359058` | `1.104` | pass |
| DB compact summary, one-shot total | 100000 | `11.001850` | `9.899949` | `0.900` | pass |
| DB compact summary, warm query median | 100000 | `0.993707` | `1.261987` | `1.270` | pass |
| Graph visibility, total OptiX path vs Embree query | 30000 | `1.065511` | `1.586865` | `1.489` | pass |
| Graph visibility, total OptiX path vs Embree query | 60000 | `2.112987` | `2.720350` | `1.287` | pass |
| Polygon pair candidate discovery | 10000 | `1.670372` | `2.013577` | `1.205` | pass |
| Polygon pair candidate discovery | 40000 | `6.255445` | `5.225501` | `0.835` | pass |
| Polygon pair total observed pipeline | 10000 | `3.577987` | `3.381419` | `0.945` | pass |
| Polygon pair total observed pipeline | 40000 | `13.695955` | `10.837770` | `0.791` | pass |
| Polygon Jaccard candidate discovery | 4096 | `0.516111` | `1.337461` | `2.591` | pass |
| Polygon Jaccard candidate discovery | 8192 | `1.018536` | `1.817546` | `1.784` | pass |
| Polygon Jaccard total observed pipeline | 4096 | `0.891567` | `2.607679` | `2.925` | pass |
| Polygon Jaccard total observed pipeline | 8192 | `2.172314` | `4.284394` | `1.972` | pass |

Graph visibility still shows a fast RT kernel but host-dominated total path:

| Scale | Embree query sec | OptiX any-hit kernel sec | Embree / kernel |
| ---: | ---: | ---: | ---: |
| 30000 | `1.065511` | `0.000213` | `5001.0x` |
| 60000 | `2.112987` | `0.000261` | `8086.3x` |

## Decisions

| App row | Decision | Reason |
| --- | --- | --- |
| `database_analytics` | `execution_unblocked_but_not_public_speedup_ready` | 30k and 100k pass both backends; OptiX is faster only for 100k one-shot total, while warm-query median remains slower. |
| `graph_analytics` | `correct_but_total_optix_slower` | Visibility passes, and the RT kernel is fast, but total OptiX path remains slower due to prepare/pack overhead. |
| `polygon_pair_overlap_area_rows` | `best_current_positive_candidate` | 40k shows OptiX faster for candidate and total observed pipeline with parity; 10k candidate is slower but total observed pipeline is slightly faster. |
| `polygon_set_jaccard` | `correct_but_optix_slower` | 4096 and 8192 now pass with chunk `1024`, but OptiX remains slower than Embree. |

## Interpretation

The v1.1 patch removes two execution blockers:

- DB 100k no longer hits the `250000` candidate ceiling.
- Jaccard 8192 no longer fails parity when chunked at `1024`.

The performance picture remains bounded:

- The clearest positive row is `polygon_pair_overlap_area_rows` at 40k.
- `database_analytics` has mixed evidence: 100k one-shot total favors OptiX, but
  prepared warm-query median favors Embree.
- `graph_analytics` and `polygon_set_jaccard` are correctness-ready but still
  not public speedup candidates under same-machine total-path timing.

## Next Work

1. Prepare a review packet for Gemini/Claude before any public wording decision.
2. For v1.1, focus on `polygon_pair_overlap_area_rows` as the near-term positive
   OptiX/Embree performance candidate.
3. For v1.5, use these results to drive general primitive work: reduce
   host-side scene/ray prepare overhead and remove app-specific continuation
   assumptions.

## Boundary

This is Codex intake of patched pod evidence. It is not a public claim, not a
release authorization, and not a substitute for required 3-AI consensus on key
performance conclusions.
