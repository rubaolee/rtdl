# Phoenix V3 RTNN Lazy Exact Prepare Evidence

Status: `rtnn_lazy_exact_prepare_reduces_prepare_not_m7_wall_floor_not_met`.

Lazy exact-search materialization is a valid generic engine cleanup: float32 aggregate/self-query routes no longer pay for the unused double-precision exact search device buffer during prepared search construction. The RTX POD rerun shows real but small movement: self-query prepare improves by 1.111x and self-query cold-plus-query improves by 1.080x. It does not solve the V3 RTNN wall problem.

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
m7_promotion_authorized: false
M7 rows added by this packet: 0
```

## Evidence

- Previous self-query JSON: `docs/rebuild/v3/evidence/rtnn_self_query_20260621/new_prepared_self_query.json`
- Lazy old prepared-query JSON: `docs/rebuild/v3/evidence/rtnn_lazy_exact_prepare_20260621/old_prepared_query_lazy_exact.json`
- Lazy self-query JSON: `docs/rebuild/v3/evidence/rtnn_lazy_exact_prepare_20260621/new_prepared_self_query_lazy_exact.json`
- Same-day CuPy grid JSON: `docs/rebuild/v3/evidence/rtnn_lazy_exact_prepare_20260621/cupy_grid_reference_lazy_exact_compare.json`

## Measurements

| route | hot median sec | pack/prepare sec | cold+query sec | runner wall sec |
| --- | ---: | ---: | ---: | ---: |
| previous self-query | 0.004359 | 0.182127 + 0.396564 | 0.583051 | 2.144675 |
| lazy old prepared-query | 0.010830 | 0.508912 + 0.538840 | 1.058582 | 2.615318 |
| lazy self-query | 0.004353 | 0.178516 + 0.356994 | 0.539863 | 2.092179 |
| same-day CuPy grid | 0.083925 | 0.000000 + 0.613784 | 0.697710 | 2.250147 |

## Comparisons

- Self-query prepare reduction from lazy exact: `1.111x`
- Self-query cold+query reduction from lazy exact: `1.080x`
- Self-query runner-wall reduction from lazy exact: `1.025x`
- Lazy old prepared-query to lazy self-query hot speedup: `2.488x`
- Lazy self-query over CuPy hot-query speedup: `19.280x`
- Lazy self-query over CuPy cold+query speedup: `1.292x`
- Lazy self-query over CuPy runner-wall speedup: `1.076x`

## Not M7

- Lazy exact improves self-query execution_prepare by only 1.111x and self-query cold-plus-query by only 1.080x.
- Lazy self-query over same-day CuPy grid is 1.292x cold-plus-query and 1.076x runner-wall, both below the 2.0x material floor.
- This is a generic overhead reduction, not a broad RTNN, V2, or whole-app claim.
- No external review or 2-AI consensus has promoted this row.

## Forbidden Shortcuts

- Do not call lazy exact a major V3 performance row.
- Do not quote the hot-path CuPy ratio without the cold and runner-wall ratios.
- Do not claim RTNN, nearest-neighbor, or V3-over-V2 broad speedup from this packet.
- Do not promote this to M7 without external review and a material cold/runner result.

## Goal-Level Decision Audit

1. Was I foolish? No. This records the optimization and its limits instead of pretending that a small prepare reduction fixes the V3 wall-clock problem.
2. If yes, what made it foolish? It would be foolish to market the lazy-exact change as a major V3 win, hide the same-day CuPy wall comparison, or keep tuning RTNN wording instead of larger ingestion/prepare costs.
3. Was there another path? I could have skipped documenting this because the gain is small, but that would make the engine change hard to audit and easy to overclaim later.
4. Can I try a different path now? Use this packet as a closed small optimization and move to the next larger generic bottleneck: input/column residency or externally reviewed prepared-handle scope.
