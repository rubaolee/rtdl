# RTDL v2.14 Release Package

Status: released source-tree packet for tag `v2.14`.

Version marker target: `v2.14`

## Purpose

v2.14 is the formal cleanup and benchmark-app boost release planned after the
v2.13 bridge addendum and before V3.0.

The release goal is not to claim that RT cores accelerate every benchmark app.
The goal is to ensure every promoted benchmark app has a current best-route
audit, same-contract comparison, explicit partner choice, phase-level
explanation, and public wording boundary.

## Release Thesis

RTDL v2.14 publishes only row-scoped, contract-scoped, hardware-scoped
performance statements. Each statement must name:

- benchmark app and row;
- contract;
- backend pair;
- partner policy;
- timing protocol;
- speedup direction;
- caveat.

## Required Gates

See [benchmark app boost gates](benchmark_app_boost_gates.md).
The frozen promoted row list is recorded in
[promoted benchmark inventory](promoted_benchmark_inventory.md).
The initial machine-checked gap matrix is recorded in
[Goal4379 v2.14 benchmark cleanup gap matrix](../../reports/goal4379_v2_14_benchmark_cleanup_gap_matrix_2026-06-14.md).

Fresh execution evidence is recorded in
[Goal4380 v2.14 pod benchmark execution](../../reports/goal4380_v2_14_pod_benchmark_execution_2026-06-14.md).
The final closeout matrix supersedes draft Goal4380 rows where Goal4381/Goal4383
added better evidence.
The app-author implementation strategy and raw OptiX callback boundary are
recorded in
[Goal4390 v2.14 app-author implementation strategy](../../learn/v2_14_app_author_implementation_strategy.md)
and reviewed by Claude in
[Goal4390 Claude review](../../reviews/goal4390_claude_review_v2_14_app_author_implementation_strategy_2026-06-15.md).

Minimum gates:

| Gate | Required state before release |
| --- | --- |
| App inventory | Current promoted benchmark-app list, with learner/research apps excluded from release claims. |
| Same-contract routes | OptiX/RT-core and Embree CPU rows use the same contract when compared. |
| Partner policy | Partners are named, fixed, and kept outside hidden backend differences. |
| Best-known route | No stale unoptimized artifacts drive release wording. |
| Phase explanations | Every speedup or slowdown has a plausible phase-level explanation. |
| RayJoin caveat | Author process wall, RTDL-vs-Embree, and author hot-compute parity are separated. |
| Pod evidence | Fresh current-head pod artifacts are collected and indexed for 11/11 non-overlay rows and the 2/8 available exact-ready RayJoin overlay rows. |
| Public wording | No unexplained rows, broad RT-core claims, whole-app claims, or RayJoin-paper claims. |
| App-author strategy | Users are told to choose primitives first, partners explicitly, and raw OptiX callbacks only as native implementation details behind generic primitives. |
| External review | Claude/Gemini or equivalent reviewers accept the packet boundary; Claude accepted the Goal4390 app-author strategy with boundary fixes applied. |

## Planned Documents

- `README.md`
- `benchmark_app_boost_gates.md`
- `promoted_benchmark_inventory.md`
- `public_rt_vs_embree_comparison.md`
- `benchmark_app_phase_explanations.md`
- `public_wording_boundaries.md`
- `rayjoin_author_vs_rtdl_caveat.md`
- `publication.md`
- `tag_preparation.md`
- `final_closeout.md`
- `../../learn/v2_14_app_author_implementation_strategy.md`

## Initial Release Rows

The release includes 12 release rows over 10 promoted benchmark apps. Spatial
RayJoin is split into LSI, PIP, and overlay because those are materially
different contracts.

| Row | Status |
| --- | --- |
| `hausdorff_xhd_threshold` | released as final v2.14 row-scoped evidence |
| `spatial_rayjoin_lsi` | released as row-scoped scalar-count evidence |
| `spatial_rayjoin_pip` | released as row-scoped scalar-count evidence |
| `spatial_rayjoin_overlay` | public-review-ready for the available 2/8 exact-ready subset; blocked only for full 8/8 Section 5.7 reproduction |
| `rt_dbscan_core_flags_numba_signature` | final narrow engineering row; Embree fairness fixed but total is continuation-dominated |
| `robot_collision_grouped_segment_flags` | final row as discrete sampled any-hit flags only |
| `contact_manifold_aabb_collect_k` | final row as AABB broadphase/contact-witness only |
| `raydb_style_grouped_i64_count` | released as generated RayDB-style grouped-count evidence; use per-iteration metric |
| `barnes_hut_node_coverage` | released as node-coverage evidence with force-law boundary |
| `librts_spatial_index_aabb` | released as prepared AABB-index evidence |
| `rtnn_ranked_summary` | large RTNN-shaped aggregate evidence ready for review; no paper-dataset claim |
| `triangle_counting_any_hit` | final row as large synthetic RT-Graph-shaped prepared primitive |

## Non-Claims

v2.14 does not claim:

- RT cores make every benchmark app faster;
- all rows are whole-application speedups;
- RTDL beats RayJoin as a whole system;
- RTDL reproduces the RayJoin paper;
- author-hot-compute parity for RayJoin;
- automatic partner selection;
- Intel or AMD GPU results;
- true zero-copy or complete device residency;
- V3.0 planner/device-resident execution-graph delivery.
- arbitrary raw OptiX callback exposure as the v2.14 user API.
