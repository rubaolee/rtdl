# RTDL v2.12 Scoped RT-Core vs Embree CPU Comparison

Status: release-facing scoped comparison; not broad speedup wording.

## Allowed Wording

RTDL v2.12 provides a source-tree, row-scoped comparison of NVIDIA OptiX/RT-core paths against Embree CPU paths for the promoted benchmark portfolio. The accepted optimized packet has no active boundary-limited rows and no contract-choice blockers; performance wording must cite the exact row and artifact.

## Comparison Table

| App / Row | Contract | Metric | Embree | OptiX | Embree / OptiX | Faster | Reading |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| barnes_hut | `prepared_fixed_radius_node_coverage_threshold_decision` | `query_fixed_radius_threshold_reached_count_sec` | 3.948736324 sec | 2.037808402 sec | 1.94x | `optix` | scoped_rt_core_value_row; same native node-coverage threshold contract; not force-vector or paper reproduction |
| contact_manifold | `native_collect_k_bounded_witness_rows` | `native_collect_elapsed_sec` | 0.000260988 sec | 0.000476252 sec | 0.55x | `embree` | embree_faster_scoped_row; prepared query/count phase only; not whole-application timing |
| hausdorff_xhd | `directed_threshold_prepared_fixed_radius_count` | `max_directed_query_fixed_radius_threshold_reached_count_sec` | 0.009892253 sec | 0.003847664 sec | 2.57x | `optix` | scoped_rt_core_value_row; prepared query/count phase only; not whole-application timing |
| LibRTS prepared AABB query | `generic_prepared_aabb_index_query_2d` | `query_median_sec` | 0.011698941 sec | 0.000622335 sec | 18.80x | `optix` | scoped_rt_core_value_row; same 1024x1024 prepared AABB query shape; query median only; scene prepare and elapsed totals are reported separately |
| raydb_style | `generic_ray_triangle_primitive_grouped_i64_reduction_3d_prepared_count` | `elapsed_sec` | 0.021954956 sec | 0.000991316 sec | 22.15x | `optix` | scoped_rt_core_value_row; same prepared grouped-reduction contract; not SQL, DBMS, or typed hit-stream handoff timing |
| robot_collision | `PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1` | `tail_total_run_sec` | 0.002454289 sec | 0.001538487 sec | 1.60x | `optix` | scoped_rt_core_value_row; same prepared-buffer compact flag contract; not continuous collision or planner timing |
| rt_dbscan | `rt_dbscan_clustered3d_count_threshold_flags_plus_numba_prepared_grid_column_signature` | `elapsed_median_sec` | 17.313535127 sec | 0.315049268 sec | 54.96x | `optix` | scoped_rt_core_value_row; same RTDL+Numba configured route with the Numba continuation held fixed |
| rtnn | `prepared_3d_fixed_radius_bounded_ranked_summary_raw_rows` | `query_median_sec` | 0.122744617 sec | 0.103778298 sec | 1.18x | `optix` | near_parity_not_rt_core_claim; same raw-row ranked-summary contract; this row is explicitly not an RT-core neighbor-search claim |
| Spatial RayJoin LSI same-stream scalar count | `lsi_same_stream_scalar_count` | `hot_query_median_ms` | 14.538773001 ms | 0.335959005 ms | 43.28x | `optix` | scoped_rt_core_value_row; RayJoin-exported same stream, scalar count output only; not RayJoin whole-system or paper-reproduction wording |
| Spatial RayJoin PIP same-stream scalar count | `pip_same_stream_scalar_count` | `hot_query_median_ms` | 14.167796995 ms | 12.033906998 ms | 1.18x | `optix` | near_parity_scoped_engineering_row; RayJoin-exported same stream, scalar count output only; not RayJoin whole-system or paper-reproduction wording |
| triangle_counting | `rt_graph_2a1_generic_ray_triangle_any_hit` | `query_median_ms` | 11.54467 ms | 0.158831477 ms | 72.69x | `optix` | scoped_rt_core_value_row; prepared query/count phase only; not whole-application timing |

## Summary

- Promoted apps covered: `10`.
- Scoped table rows: `11`.
- OptiX-faster scoped rows: `10`.
- Embree-faster scoped rows: `1`.
- Active boundary-limited rows: `0`.
- Contract-choice blockers: `0`.

## Fairness

Rows are compared only when the output contract is scoped and the optimized packet accepts the evidence. Partner work is named and held fixed where used; RT-DBSCAN uses the same Numba continuation on both sides. Contact Manifold and RTNN stay explicitly mixed rather than being folded into a broad RT-core win.

## Blocked Wording

Do not say that RT cores make every benchmark app faster, that RTDL beats RayJoin as a whole system, that the RayJoin paper is reproduced, or that these rows are whole-application speedups.

## Claim Boundary

RTDL v2.12 authorizes a source-tree release marker and row-scoped OptiX/RT-core versus Embree CPU comparison wording. It does not authorize broad RT-core speedup, whole-application speedup, package install, automatic partner selection, RTDL-beats-RayJoin, paper reproduction, Intel GPU, or general zero-copy/device-residency claims.

Validation status: `accept`.
