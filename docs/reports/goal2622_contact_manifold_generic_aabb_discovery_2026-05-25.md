# Goal2622 Contact-Manifold Generic AABB Discovery Bridge

Date: 2026-05-25

Status: implemented local generic AABB broadphase row path and routed the
contact-manifold optimized path through it before exact refinement and
`COLLECT_K_BOUNDED`. This is a boundary cleanup and performance-risk reduction,
not a public speedup claim.

## Goal

Address the Goal2621 concern that the contact benchmark still used app-owned
Python full all-pairs triangle-intersection discovery before exercising the
generic bounded collection primitive.

The accepted boundary for this goal:

- The engine may own generic candidate discovery.
- The engine must not own collision, contact, manifold, robot, or physics
  semantics.
- Exact triangle-intersection refinement may remain app-owned until RTDL has a
  promoted generic exact-shape refinement primitive.
- `COLLECT_K_BOUNDED` remains responsible only for bounded row materialization
  and fail-closed overflow.

## Implemented Changes

- Added `rtdsl.aabb_intersection_pair_rows_2d(...)`.
- The helper extends `AABB_INDEX_QUERY_2D` with CPU reference row output for
  generic `(query_id, indexed_id)` 2-D AABB intersection candidate rows.
- Added contact app mode:
  `--mode aabb_broadphase_collect_k`.
- Added an adaptive AABB grid-resolution policy:
  `min(256, max(16, sqrt(grid_count)))`. Pod pressure testing showed that
  `resolution=grid_count` can explode on skinny AABB distributions because each
  box can span every cell on one axis.
- The optimized contact path is now:

```text
query triangle AABBs + scene triangle AABBs
  -> generic AABB_INDEX_QUERY_2D intersection pair rows
  -> app-owned exact triangle-intersection refinement
  -> generic COLLECT_K_BOUNDED fail-closed witness-row materialization
```

## Boundary Result

The app no longer needs to run Python exact triangle intersection over every
query/scene pair in its optimized path. It first asks RTDL for generic AABB
candidate rows, then refines only those candidates.

This still does not make exact contact discovery a native RTDL primitive. The
exact refinement remains app-owned, and contact summaries remain app-owned. The
engine sees only AABB boxes, generic pair ids, and generic bounded integer rows.

Rejected for this goal:

- No call to `collect_shape_pair_candidates_bounded` from this benchmark app.
- No collision-specific native engine symbol.
- No contact-manifold native ABI.
- No public speedup wording.

## Local Evidence

Commands run from repository root:

```bash
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode collect_k_reference --dataset tiny --witness-capacity 3
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode aabb_broadphase_collect_k --dataset tiny --witness-capacity 3
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode aabb_broadphase_collect_k --dataset grid --grid-count 512 --witness-capacity 512
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode baseline_comparison --dataset grid --grid-count 512 --witness-capacity 512 --repeat-count 3
```

Observed:

- Tiny AABB path matched the exact CPU reference:
  `((0, 10, 0), (0, 11, 1), (2, 30, 2))`.
- Grid-512 AABB path matched the exact CPU reference with 512 final rows.
- Grid-512 all-pairs count: `262144`.
- Grid-512 generic AABB candidate checks: `512`.
- Grid-512 exact refinement checks after broadphase: `512`.
- Grid-512 candidate checks avoided: `261632`.
- Grid-512 pruning ratio: `0.998046875`.
- Best local grid-512 timing over 3 repeats:
  - full Python exact CPU reference: about `5.78300075000152` seconds;
  - AABB broadphase + exact refinement + collect-k: about
    `0.013075542025035247` seconds;
  - collect-k over already materialized rows: about
    `0.0008610830118414015` seconds.

Interpretation:

- The improvement comes from removing full Python all-pairs discovery in the
  optimized benchmark path.
- The remaining time is mostly generic CPU AABB grid preparation/row
  emission overhead, not RT-core evidence.
- Native OptiX `AABB_INDEX_QUERY_2D` remains count-only for `range_intersects`;
  a native generic row emitter is the next engine step before an RT speedup
  claim can be considered.

## Tests

Added:

```text
tests/goal2622_contact_manifold_generic_aabb_discovery_test.py
```

Coverage:

- generic AABB pair-row API emits app-name-free `(query_id, indexed_id)` rows;
- contact app AABB broadphase path matches tiny exact reference;
- grid broadphase avoids full all-pairs Python refinement;
- overflow still fails closed through `COLLECT_K_BOUNDED`;
- app source does not call old shape-pair native candidate collector symbols;
- docs record the Goal2622 boundary and 3-AI consensus.

## Current Conclusion

Goal2622 resolves the immediate design problem: the promoted contact benchmark
no longer presents full app-owned Python all-pairs discovery as the optimized
path. The new path composes two generic behaviors:
`AABB_INDEX_QUERY_2D` for candidate discovery and `COLLECT_K_BOUNDED` for
bounded witness-row materialization.

Pod follow-up evidence is recorded in
`docs/reports/goal2622_contact_manifold_optix_count_boundary_pod_evidence_2026-05-25.md`.
It confirms that OptiX `AABB_INDEX_QUERY_2D` count-only `range_intersects`
matches CPU for the grid-512 AABB workload, while generic AABB row output
remains CPU-reference-only.

The benchmark remains internally promoted, but public performance wording is
still blocked until native generic AABB row output or a stronger generic exact
shape-pair refinement path is implemented and reviewed.
