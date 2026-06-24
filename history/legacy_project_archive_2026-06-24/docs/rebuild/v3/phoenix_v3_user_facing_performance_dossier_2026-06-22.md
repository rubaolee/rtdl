# Phoenix V3 User-Facing Performance Dossier

Date: 2026-06-22
Status: `redo_required`

This dossier is the current user-facing performance map for Phoenix V3. It is
not release authorization. It exists so users, reviewers, and successor agents
can see what V3 actually proves, what it does not prove, and where each claim
can be reproduced.

## Bottom Line

Phoenix V3 is not authorized as a public major release:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
blocking_reasons:
  - broad_v2x_performance_not_proven
  - serious_all_app_paired_evidence_failed_release_bar
  - current_scoped_13_row_surface_not_v3_major_release
```

The honest V3 performance story is:

- V3 fixes important V2.14 route-health and runability failures.
- V3 does not prove a broad same-row speedup over V2.14.
- V3 has thirteen exact M7-qualified or supplemental row-scoped capability
  rows across nine generic capability families, but this is internal evidence.
- Public wording must stay blocked because the completed serious all-app
  paired benchmark did not prove reusable RTRDL language/runtime improvement over V2.x.

The completed serious same-RT-hardware V2.14 comparison is the controlling
broad-speed answer:

```text
same_metric_comparison_count: 52
V3 faster by >5%: 12
Within +/-5%: 35
V3 slower by >5%: 5
Geomean V3 speedup vs V2.14: 1.012x
expected_promoted_app_count: 10
actual_promoted_app_count: 10
missing_promoted_apps: []
primary_metric_source_mismatch_count: 0
release_consideration_eligible: false
not a major broad speedup claim
```

That is route-health progress and mostly timing parity. This is not a major
broad speedup claim, so it is not enough for V3 to exist as a major release.

The preregistered release bar was much higher:

```text
overall_geomean_v3_speedup_vs_v2 >= 1.20x
at least 8 of 10 app geomeans > 1.05x
no app geomean < 0.95x without accepted explanation
```

The actual serious result failed that bar:

```text
overall_geomean_v3_speedup_vs_v2: 1.012x
app_geomeans_gt_1.05x: 1 of 10
app_geomeans_lt_0.95x: 2 of 10
```

App geomeans from the serious paired run:

```text
barnes_hut: 0.844x
contact_manifold: 1.017x
hausdorff_xhd: 1.149x
librts_spatial_index: 0.937x
raydb_style: 1.046x
robot_collision: 0.993x
rt_dbscan: 0.988x
rtnn: 1.003x
spatial_rayjoin: 1.027x
triangle_counting: 0.987x
```

## What V3 Solves For Users

V2.x proved that RTDL could expose useful RT-shaped computation, but users had
to read too much project history to know which routes were real. Phoenix V3 is
supposed to be the runtime repair:

- one Python-hosted RTDL programming surface;
- explicit backend and partner boundaries;
- row-scoped prepared execution evidence instead of whole-app slogans;
- serious benchmark rows with raw artifacts, hardware, and commands;
- negative and no-go rows explained before they can mislead users.

The benchmark apps are not the product. They exist to force RTRDL runtime and
language capabilities to become real. The current result is a useful evidence
surface, not yet a V3 release.

## Hardware Scope

Primary performance evidence is scoped to:

```text
NVIDIA RTX 4000 Ada Generation
driver 550.127.05
single RTX pod
```

Secondary machine work confirms documentation, tests, and source-tree health,
but does not authorize broad multi-GPU performance portability.

## Current 13-Row Surface

The table below contains 13 exact current rows. All 13 rows are row-scoped or
supplemental; rows that mention device-column input are not true zero-copy
product capability.

```text
13 exact current rows
all 13 rows are row-scoped or supplemental
not true zero-copy product capability
```

| Capability | Row id | Evidence-backed result | User boundary |
| --- | --- | --- | --- |
| `grouped_reduction` | `grouped_reduction_sum_scalar_broadcast_repeat100_262144` | 262,144 rows / 1,024 groups, actual repeat=100: 200.353x hot prepared loop and 27.917x cold-plus-loop OptiX over Embree. | Row-scoped prepared grouped-sum only. Not whole RayDB/database speedup and not V3-over-V2. |
| `grouped_reduction` | `grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups` | CuPy device-column grouped sum, 262,144 rows / 1,024 groups: 3.599x cold-plus-loop over host-packed OptiX and 100.019x same-contract context over Embree. | Not true zero-copy. Not whole-app or pure backend-only wording. |
| `grouped_reduction` | `grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups` | CuPy device-column grouped sum, 524,288 rows / 2,048 groups: 73.586x cold-plus-loop over host-packed OptiX and 174.645x same-contract context over Embree. | Not true zero-copy. Mostly input-path collapse plus prepared execution, not a universal database claim. |
| `aabb_candidate_stream` | `aabb_candidate_stream_all_count_only_float32_32768` | 32,768 indexed boxes plus 32,768 point and box queries: 814.339x query and 132.753x wall OptiX over RTDL Embree. | Native float32-inclusive generic AABB row. Not LibRTS paper/authors-code timing and not V2 speedup wording. |
| `aabb_candidate_stream` | `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50` | Native query-handle range-intersection rows: 1.719x cold-plus-collect wall and 1.867x query-total OptiX over Embree. | Exact row only. Not Contact Manifold solver or broad AABB-index wording. |
| `aabb_candidate_stream` | `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50` | Native query-handle range-intersection rows: 1.637x cold-plus-collect wall and 1.743x query-total OptiX over Embree. | Exact row only. Not scale-generalized beyond the reviewed jittered-grid contract. |
| `component_union` | `component_union_clustered3d_65536_524288_repeat5_row_scoped` | RTDBSCAN component signature route: 1.102x to 1.236x end-to-end OptiX over same-contract Embree on zero-noise four-cluster synthetic clustered3d rows. | Modest row-scoped win. Numba continuation still dominates; not full DBSCAN, paper, noisy-data, or whole-app speedup. |
| `prepared_graph_chunk` | `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream` | Triangle prepared graph chunk: 347.232x hot query and 6.342x wall OptiX over Embree on the exact 80,000-clique non-graph stream row. | Synthetic non-graph output-stream row. Not graph database, RT-Graph paper, M113 graph capture, or full Triangle app claim. |
| `ranked_summary` | `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02` | RTNN ranked summary: 7.889x hot query, 1.315x cold-plus-query, and 3.761x runner-wall over a CuPy uniform-grid CUDA-core reference across 50 prepared repeated queries. | Prepared repeat50 amortization only. Not one-shot RTNN, general nearest-neighbor, or paper-equivalent claim. |
| `aggregate_frontier` | `aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped` | Generic aggregate-tree fused weighted-vector sum, Numba CUDA partner: 45.493 ms wall-repeat median at 131,072 bodies, 4.082x faster than CPU/Numba fused baseline. | Partner route, not RT-core. 13.591x over the current OptiX frontier-emission route is supporting no-go metadata only. |
| `threshold_summary` | `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped` | Hausdorff threshold summary at 1,048,576 points per side: query mean 1.639x, phase-total mean 1.240x, weakest phase-total 1.224x OptiX over Embree. | Threshold decision only. Not full Hausdorff witness materialization, other thresholds, or X-HD reproduction. |
| `collision_flag_stream` | `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped` | Robot collision flag stream: tail prepared query mean 5.086x, total-run window mean 5.075x, conservative no-probe wrapper mean 1.171x OptiX over Embree. | Sampled flag-stream row. Not full robot planning, exact solid collision, continuous collision, or zero-copy. |
| `point_location_topology_stream` | `point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7` | Spatial public-county default path: 1.080599 ms median, stable exact row count 47,262, 1.755x over current prefilter-zero route and 1.727x faster than the RayJoin author Query timer. | Bounded supplemental capability row. Public speedup, RTDL-beats-RayJoin, paper reproduction, true zero-copy, and release wording remain unauthorized. |

Rows outside this list are internal, blocked, no-go, historical, or future work
unless a focused packet and review promotes them.

## All Benchmark App Verdict

| App | Current V3 verdict |
| --- | --- |
| `raydb_style` | Three exact grouped-sum rows are M7-qualified. Count rows and whole RayDB/database speedup remain blocked. |
| `librts_spatial_index` | Three generic AABB candidate-stream rows are M7-qualified. LibRTS authors-code and paper-equivalent wording remain blocked. |
| `rt_dbscan` | One exact component-signature row is M7-qualified with modest 1.102x to 1.236x same-contract speedup. Full DBSCAN and paper wording remain blocked. |
| `triangle_counting` | One exact prepared-graph chunk row is M7-qualified. Graph database and paper reproduction claims remain blocked. |
| `rtnn` | One prepared repeat50 ranked-summary row is M7-qualified. One-shot and general nearest-neighbor claims remain blocked. |
| `barnes_hut` | One explicit Numba CUDA partner row is M7-qualified. The RTDL/OptiX frontier-emission route remains no-go; no RT-core claim is authorized. |
| `hausdorff_xhd` | One large threshold-summary row is M7-qualified. Full Hausdorff and witness materialization claims remain blocked. |
| `robot_collision` | One no-probe flag-stream row is M7-qualified. Full collision/planning claims remain blocked. |
| `spatial_rayjoin` | One bounded topology-stream supplemental row closes capability breadth. Public Spatial RayJoin speedup and RTDL-beats-RayJoin wording remain blocked. |
| `contact_manifold` | Boundary lesson only, not M7: query is 1.235x and collect-k is 2.759x, but wall timing is 0.803x, so OptiX is slower on the wall path. |

## Why Some Big Numbers Are Not Release Claims

Several historical or candidate rows contain spectacular ratios. They are not
safe release claims unless the exact reviewed row says so:

- `30489.613x` Spatial overlay-seed is hot prepared internal evidence, not
  whole RayJoin or paper reproduction.
- `1483.603x` RTDBSCAN all-app reading was superseded by same-contract reruns;
  the current approved RTDBSCAN row is only 1.102x to 1.236x.
- `13.591x` Barnes-Hut over current RTDL/OptiX is supporting no-go metadata
  because the OptiX frontier-emission route is already rejected.
- Contact Manifold has query and collect-k wins, but OptiX wall timing is
  slower, so no M7 row is authorized.

## Reproduction Entrypoints

Use these artifacts before quoting any result:

```text
docs/rebuild/v3/v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md
docs/rebuild/v3/phoenix_v3_serious_v2x_paired_benchmark_2026-06-22.md
docs/rebuild/v3/evidence/phoenix_v3_serious_v2x_paired_20260622_074100/summary.json
docs/rebuild/v3/v3_claim_grade_all_benchmark_results_2026-06-20.md
docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json
docs/rebuild/v3/phoenix_v3_objective_conformance_gate_2026-06-22.json
docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json
docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md
```

The current local health matrix is:

```text
docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_serious_paired_conclusion_sync_20260622.json
106 modules / 509 tests OK
```

The matrix proves local source health. It does not authorize release.

## V3 Redo Rule

V3 can exist only if serious benchmark-app stress tests prove reusable RTRDL
runtime improvements over V2.x. App-specific patches do not count. A 1.01x-style
geomean does not count.

## Non-Claims

Do not claim:

- Do not claim V3 released or complete.
- Do not claim C ABI, embedding, public SDK/package, or multi-language host support.
- V3 is released or complete;
- V3 broadly beats V2.x;
- V3 automatically selects the fastest backend or partner;
- all benchmark apps are solved end to end;
- Spatial RayJoin public speedup or RTDL-beats-RayJoin;
- LibRTS, RayJoin, RT-Graph, RTNN, X-HD, or other paper reproduction;
- true zero-copy product capability;
- C ABI, embedding, or external-runtime claims;
- package-install readiness or broad hardware portability.

## Goal-Level Decision Audit

Decision: keep a single user-facing Phoenix V3 performance dossier, but mark it
`redo_required` because the 13-row surface and V2.14 comparison do not yet prove
the major-version runtime performance case.

1. Was I foolish? Yes.
2. If yes, what actions made the decision foolish? The foolish action would be
   to turn the 13 rows into major-release or broad-speedup wording.
3. Was there another path? Yes. I could keep evidence scattered across row
   packets and ask every reviewer to reconstruct the surface manually. That
   repeats the old deep-sea-docs failure.
4. Can I now try a different path? Yes. This dossier gives one bounded map:
   exact rows, exact numbers, exact boundaries, and the runtime redo still
   required.

