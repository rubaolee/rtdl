# Goal2579 LibRTS Benchmark Reproduction Status

## Current Status

LibRTS is now promoted from intake to an active RTDL research benchmark app. The
current benchmark covers the core point/range spatial-index contracts and has
authors-code evidence, but it does not reproduce the paper's headline speedups.

## What Is Done

| Area | Status | Evidence |
| --- | --- | --- |
| Paper/app intake | done | `goal2574_librts_spatial_index_benchmark_intake_2026-05-24.md` |
| Predicate semantics | done | `point_contains`, `range_contains`, `range_intersects`; range-contains fixed as indexed box contains query box |
| RTDL CPU oracle | done | `cpu_reference` and `cpu_reference_wkt` modes |
| WKT interchange | done | `emit_wkt` plus WKT load-back into CPU oracle |
| Authors executable runner | done | `scripts/goal2574_librts_external_runner.py` |
| Authors-code query timing | done for bounded synthetic slices | Goal2575 high-selectivity rows and Goal2578 paper-like uniform rows |
| Authors-code mutation correctness | done for authors GTest cases | Goal2577 update/delete/delete-compact pod evidence |
| RTDL primitive extracted from app | done as CPU reference | `AABB_INDEX_QUERY_2D`, `prepare_aabb_index_2d`, `query_aabb_index_2d` |

## What Is Not Done

| Paper claim area | Missing work | Why not claim yet |
| --- | --- | --- |
| `85.1x` point-query speedup | Boost R-tree / LBVH / cuSpatial baselines on paper datasets | We only timed authors LibRTS code, not competitor baselines |
| `94.0x` range-contains speedup | Same baseline matrix on real-world datasets | Current rows are synthetic WKT fixtures |
| `11.0x` range-intersects speedup | Same baseline matrix at controlled selectivity | We have selectivity insight, not baseline speedup evidence |
| PIP `3.8x` over RayJoin | Real PIP app and RayJoin/cuSpatial comparison | Current benchmark intentionally focuses on point/range index contracts |
| Native RTDL AABB index | Embree/OptiX prepared AABB query implementation | Current RTDL primitive is CPU reference only |
| Mutation performance | timed insert/delete/update throughput | Current evidence is authors-code correctness tests only |

## Main Design Insight For RTDL

This app pressure is not "LibRTS support." It is a general behavior:

`prepared AABB index + point/box query streams + exact predicate refinement + count-first outputs`

That behavior is now represented by `AABB_INDEX_QUERY_2D`. The next RTDL
runtime target should be a native prepared AABB query primitive, not a
paper-specific or app-specific native symbol.

## Recommended Next Engineering Target

Implement a prepared native `AABB_INDEX_QUERY_2D` path in this order:

1. CPU reference is already present and test-backed.
2. Embree count-only backend for point contains, range contains, and range intersects.
3. OptiX count-only backend with prepared indexed AABB state and query streams.
4. Exact same result contract across CPU/Embree/OptiX on WKT fixtures.
5. Only after count parity is stable, consider row collection and mutation batches.

This should stay app-agnostic:

- no `LibRTS` native symbol;
- no hard-coded paper dataset names;
- no built-in point-in-polygon app logic;
- no public speedup wording until exact baselines are reproduced and reviewed.

## Current Claim Boundary

We can say:

"RTDL now includes a LibRTS-style research benchmark harness with CPU oracle,
WKT interchange, authors-code query/mutation evidence, and an extracted generic
CPU `AABB_INDEX_QUERY_2D` primitive boundary."

We cannot say:

"RTDL reproduces the LibRTS PPoPP 2025 headline speedups."

We also cannot say:

"RTDL has a native RT-core spatial index equivalent to LibRTS."
