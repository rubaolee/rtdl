# Goal2655 Benchmark RT-Core Speedup Summary

Status: internal summary. This is not public speedup wording and not a
whole-application performance claim.

## Purpose

This report gives the compact benchmark-app view requested after Goal2654:
combine RayDB `count` and `sum` into one app row, and state how each benchmark
uses OptiX/RT relative to the Embree CPU RT baseline.

## Summary Table

| Benchmark app | Current RT-vs-Embree speedup | How OptiX/RT is used | Boundary |
| --- | ---: | --- | --- |
| Hausdorff / X-HD-style | 3.29x | Prepared target-point traversal for fixed-radius/nearest-witness threshold work. | Threshold decision only; exact witness paths need separate same-contract rows. |
| Spatial RayJoin-style | 38.36x | Generic spatial traversal over prepared shapes/segments for PIP/LSI/overlay-seed candidates. | Scoped spatial relation summary; not full RayJoin or full overlay materialization. |
| RT-DBSCAN-style | 12.71x | Generic 3-D fixed-radius RT traversal for core/count evidence, adjacency/chunk streams, or grouped streams; CuPy/Python labels components. | No DBSCAN-native ABI; cluster semantics stay in app/partner code. |
| Robot collision | 5.29x | Prepared static triangle scene; batched query segment/geometry any-hit probes return collision flags. | Static screening only, not a planner or swept solver. |
| RayDB-style grouped aggregate | 27.67x count; 104.00x sum | Rows become generic triangles; query predicates become dense `+Z` rays; OptiX hits are deduplicated and reduced by group. | Generated 2M fixture, steady-state prepared-query phase only; no whole-app, DBMS, authors-code, or public claim. |
| Barnes-Hut / RT-BarnesHut-style | 4.55x | Prepared node-coverage / expanded-AABB point-membership candidate discovery. | Python owns opening decisions and force math; no native Barnes-Hut force ABI. |
| LibRTS-style spatial index | 29.95x | Generic prepared 2-D AABB index for point/range contains/intersects count queries. | Count-only internal slice, not full mutable LibRTS reproduction. |
| RTNN neighbor search | 172.14x | Prepared 3-D fixed-radius RT traversal for ranked-neighbor summary evidence. | Ranked-summary contract only, not full RTNN paper-system reproduction. |
| Triangle counting | 107.16x | Graph relations are mapped to generic rays and triangles; OptiX counts intersections for RT-Graph-style summaries. | Synthetic/backend-query contract; paper-scale datasets still need segmented/streamed lowering. |
| Bounded contact witness / contact-manifold | 26.29x | Generic AABB broadphase candidate rows plus bounded witness collection. | Exact contact refinement remains app-owned; no collision/contact native ABI. |

## Interpretation

Yes, this list is strong internal evidence that the benchmark portfolio is using
RT-friendly work and that the OptiX path benefits from NVIDIA RT hardware for
the measured exact subpaths:

- every promoted benchmark app has a current Embree-vs-OptiX comparison row;
- every current primary row shows OptiX faster than Embree;
- the app contracts are all expressed through RT-shaped generic primitives such
  as rays, triangles, AABBs, fixed-radius hits, any-hit/count summaries,
  grouped reductions, and bounded collection;
- the native engine remains app-agnostic: app semantics stay in Python/partner
  code.

The wording still needs discipline. The evidence strongly suggests
RT-hardware acceleration for these measured OptiX paths, but it does not by
itself prove:

- whole-application speedups;
- public benchmark claims;
- speedups over CUDA author implementations;
- speedups over DBMS systems;
- universal speedups for every input shape;
- true zero-copy execution.

## Correct Claim Shape

Allowed internal wording:

```text
Across the current promoted benchmark apps, the measured OptiX/RTDL path beats
the same-contract Embree baseline for every accepted primary benchmark row.
Because these paths are expressed as RT-shaped generic primitives and run
through OptiX, the portfolio provides strong internal evidence that RTDL is
successfully exposing workloads that benefit from NVIDIA RT hardware.
```

Not allowed without a separate review packet:

```text
RTDL universally accelerates these whole applications, beats all author CUDA
implementations, or provides public benchmark speedups.
```

## Source Reports

- `docs/reports/goal2654_all_benchmark_app_perf_comparison_refresh_2026-05-27.md`
- `docs/reports/goal2653_raydb_benchmark_closeout_2026-05-27.md`
- `docs/reports/goal2653_raydb_closeout_3ai_consensus_2026-05-27.md`
- `docs/application_catalog.md`
