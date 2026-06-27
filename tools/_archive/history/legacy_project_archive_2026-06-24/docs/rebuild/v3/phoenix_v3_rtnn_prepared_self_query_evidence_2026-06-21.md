# Phoenix V3 RTNN Prepared Self-Query Evidence

Status: `rtnn_prepared_self_query_hot_path_material_not_m7_wall_floor_not_met`.

The self-query path is a real generic engine improvement: it reuses prepared search device columns as query columns for fixed_radius_neighbors_3d aggregate workloads. On the RTX 4000 Ada POD it gives 2.482x hot-query speedup and 2.784x input-pack reduction over the prior prepared-query batch route, while preserving same-contract integer parity. It also gives a 19.437x hot-query speedup over the CuPy grid reference. It is not an M7 row yet: cold-plus-query vs CuPy is only 1.214x and runner-wall is only 1.030x.

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
m7_promotion_authorized: false
M7 rows added by this packet: 0
```

## Evidence

- Old prepared-query JSON: `docs/rebuild/v3/evidence/rtnn_self_query_20260621/old_prepared_query.json`
- New prepared-self-query JSON: `docs/rebuild/v3/evidence/rtnn_self_query_20260621/new_prepared_self_query.json`
- CuPy grid reference JSON: `docs/rebuild/v3/evidence/rtnn_self_query_20260621/cupy_grid_reference.json`
- Call for review: `docs/reviews/call_for_review_phoenix_v3_rtnn_prepared_self_query_evidence_2026-06-21.md`
- External review blocked: `docs/reviews/external_review_blocked_phoenix_v3_rtnn_prepared_self_query_evidence_2026-06-21.md`
- 2-AI consensus exists: `false`

## Measurements

| route | hot median sec | pack/prepare sec | cold+query sec | runner wall sec |
| --- | ---: | ---: | ---: | ---: |
| old prepared-query | 0.010818 | 0.507080 + 0.580071 | 1.097970 | 2.641425 |
| new prepared-self-query | 0.004359 | 0.182127 + 0.396564 | 0.583051 | 2.144675 |
| CuPy grid reference | 0.084733 | 0.000000 + 0.622947 | 0.707680 | 2.209954 |

## Comparisons

- Old prepared-query to new self-query hot speedup: `2.482x`
- Old prepared-query to new self-query cold+query speedup: `1.883x`
- Old prepared-query to new self-query runner-wall speedup: `1.232x`
- Input-pack reduction: `2.784x`
- New self-query over CuPy hot-query speedup: `19.437x`
- New self-query over CuPy cold+query speedup: `1.214x`
- New self-query over CuPy runner-wall speedup: `1.030x`

## Not M7

- New self-query cold-plus-query vs CuPy is only 1.214x, below the 2.0x material floor.
- New self-query runner-wall vs CuPy is only 1.030x, so file/input overhead still dominates whole-run evidence.
- This is a prepared/reuse-path win, not a broad V3-vs-V2 or whole-app win.
- No external Claude/Gemini review has accepted this as an M7 release row.

## Forbidden Shortcuts

- Do not quote 19.437x without saying it is hot-query prepared self-query only.
- Do not call 1.030x runner-wall speedup a major V3 performance win.
- Do not claim broad V3 faster-than-V2 from this packet.
- Do not promote this row to M7 without external review and a material cold/runner result.

## Goal-Level Decision Audit

1. Was I foolish? No. This decision separates a material prepared-path improvement from a release-quality whole-run claim.
2. If yes, what made it foolish? It would be foolish to market the 19.437x hot-query number alone or hide the 1.030x runner-wall result.
3. Was there another path? I could have stopped at the old prepared-query route and argued from 7.7x hot speedup, but that left duplicated query packing and weaker evidence.
4. Can I try a different path now? Use self-query as one Phoenix V3 engine capability, then continue toward generic ingestion/prepare amortization before any major release claim.
