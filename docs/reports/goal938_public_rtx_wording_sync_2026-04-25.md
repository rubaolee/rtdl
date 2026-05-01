# Goal938 Public RTX Wording Sync

Date: 2026-04-25

## Purpose

Synchronize user-visible RTX wording after the Goal937 ready-claim packet.
The key problem was public-doc drift: older Goal818-era text still said graph,
facility KNN, and polygon overlap/Jaccard were rejected as RT-core claim paths,
while the current support matrix and Goal937 packet now allow bounded versions
of those paths to enter RTX claim review.

## Files Updated

- `README.md`
- `docs/rtdl_feature_guide.md`
- `docs/release_facing_examples.md`
- `docs/application_catalog.md`
- `docs/tutorials/graph_workloads.md`
- `docs/tutorials/nearest_neighbor_workloads.md`
- `docs/tutorials/segment_polygon_workloads.md`
- `docs/app_engine_support_matrix.md`
- `tests/goal821_public_docs_require_rt_core_test.py`
- `tests/goal938_public_rtx_wording_sync_test.py`

## Current Public Wording Contract

The public docs now distinguish three states:

1. Ready for RTX claim review: the nine bounded sub-paths listed in Goal937.
2. RT-core-gated or OptiX-capable but still held: DB compact-summary,
   road-hazard, segment/polygon hit-count, segment/polygon pair rows,
   Hausdorff exact-distance/ranking, ANN ranking, and Barnes-Hut force
   reduction.
3. Non-claim compatibility paths: OptiX backend selection, CUDA-through-OptiX,
   host-indexed fallback, Python post-processing, exact polygon
   area/Jaccard refinement, and whole-app behavior.

## Ready Claim-Review Paths

The public docs now name the current ready claim-review candidates:

- graph analytics visibility edges
- service coverage gap summary
- event hotspot count summary
- facility coverage decision
- polygon pair overlap candidate discovery
- polygon set Jaccard candidate discovery
- outlier fixed-radius threshold-count summary
- DBSCAN core-flag summary
- robot collision prepared count or pose flags

## Explicit Non-Claims

This goal does not authorize public speedup claims. It only makes the docs
consistent with the current claim-review packet. The docs continue to forbid:

- broad whole-app speedup claims;
- "all graph/database/spatial work is RT-core accelerated";
- full DBMS claims;
- exact polygon area/Jaccard as fully native OptiX;
- ranked KNN, full DBSCAN cluster expansion, and Barnes-Hut force reduction as
  RT-core claims;
- per-app cloud restarts.

## Verification

Local focused checks:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal937_ready_rtx_claim_review_packet_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test \
  tests.goal687_app_engine_support_matrix_test
```

Result: 25 tests passed.

Additional stale-wording search:

```bash
rg -n 'Rejected under `--require-rt-core`|Graph, facility|graph, facility|polygon overlap/Jaccard.*reject|no OptiX/NVIDIA RT-core surface today|accepted partial claim modes|Current accepted partial modes|claim paths\. Current accepted' README.md docs/rtdl_feature_guide.md docs/release_facing_examples.md docs/application_catalog.md docs/tutorials
```

Result: no matches.

## Boundary

This is a documentation consistency goal. It does not change runtime behavior,
does not promote held apps, and does not replace the Goal937 claim-review
packet or the support matrix as the source of truth.
