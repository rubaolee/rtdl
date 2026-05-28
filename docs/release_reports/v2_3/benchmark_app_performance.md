# RTDL v2.3 Benchmark-App Performance Appendix

Status: v2.3-family internal performance appendix. This is not a new release
tag, not public speedup wording, and not a whole-application performance claim.

Date: 2026-05-27

## Scope

This appendix summarizes the current accepted Embree-vs-OptiX performance
evidence for the promoted RTDL benchmark apps. It supersedes the older v2.3
README performance wording for the benchmark table, because later v2.3-family
work added the bounded contact witness benchmark and rewrote RayDB from the old
partner-resident grouped-reduction row into a paper-shaped RT-core prepared
query row.

This is a current-evidence portfolio view. Most rows come from the Goal2634 /
Goal2637 all-benchmark matrix. RayDB rows come from Goal2652 / Goal2653. It is
therefore not a single synchronized pod sweep; it is the current accepted
per-app comparison table.

## Executive Summary

- Promoted benchmark apps: 10.
- Primary comparison rows: 11, because RayDB has distinct grouped `count` and
  grouped `sum` contracts.
- OptiX wins: 11 of 11 primary rows.
- Primary-row speedup summary on the NVIDIA RTX A5000 pod evidence: min 3.29x,
  median 27.67x, geomean 24.13x, max 172.14x.
- Correct interpretation: the measured OptiX/RTDL path beats the same-contract
  Embree baseline for every accepted primary benchmark row.
- Incorrect interpretation: RTDL universally accelerates these whole apps or
  beats CUDA author implementations, SQL engines, DBMSs, or every input shape.

## Primary Embree-vs-OptiX Rows

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

RayDB `count` and `sum` are distinct primary rows in the statistics above; they
are combined in this table for compact display because they belong to one
benchmark app.

## What This Supports

Allowed internal wording:

```text
Across the current promoted benchmark apps, the measured OptiX/RTDL path beats
the same-contract Embree baseline for every accepted primary benchmark row.
Because these paths are expressed as RT-shaped generic primitives and run
through OptiX, the portfolio provides strong internal evidence that RTDL is
successfully exposing workloads that benefit from NVIDIA RT hardware.
```

This is stronger than saying the apps merely run on an OptiX backend. The
portfolio covers RT-shaped contracts across fixed-radius search, spatial joins,
component-building workloads, collision flags, RayDB-style grouped reduction,
hierarchical candidate discovery, AABB indexing, ranked neighbor summaries,
graph triangle counting, and bounded witness collection.

## What This Does Not Support

This appendix does not authorize:

- public speedup wording;
- whole-application speedup wording;
- author-code comparison claims;
- CUDA baseline victory claims;
- SQL/DBMS performance claims;
- full paper-reproduction claims;
- package-install support claims;
- true zero-copy claims;
- claims that every input shape benefits equally.

## Source Evidence

- `docs/reports/goal2654_all_benchmark_app_perf_comparison_refresh_2026-05-27.md`
- `docs/reports/goal2655_benchmark_rt_core_speedup_summary_2026-05-27.md`
- `docs/reports/goal2653_raydb_benchmark_closeout_2026-05-27.md`
- `docs/reports/goal2653_raydb_closeout_3ai_consensus_2026-05-27.md`
- `docs/reports/goal2637_all_benchmark_perf_diffs_2026-05-27.md`
- `docs/reports/goal2643_all_benchmark_apps_detailed_report_2026-05-27.md`
- `docs/application_catalog.md`

## Release Boundary

This appendix is suitable as a v2.3-family internal benchmark-performance doc
after external review. It should not be copied into public release text unless a
separate review approves exact public wording.
