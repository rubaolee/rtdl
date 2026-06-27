# V2/V2.x Primitives -> V4 Tier-2 Promotion Inventory

Date: 2026-06-24
Status: engineering inventory, not a release claim

## Purpose

V4 is not a rewrite from zero. The practical V4 path is to promote existing V2/V2.x app-agnostic primitives into a clean V4 Tier-2 fused operator catalog.

This inventory separates:

- primitives already promoted to a measured V4 surface
- primitives present in V2/V2.x but not yet promoted
- partner/orchestration paths that are useful fallbacks but not V4 Tier-2 fusion
- deferred Tier-3 or non-V4.0 surfaces

This document is an implementation map. It does not authorize V4 release wording, broad speedup claims, whole-app claims, raw OptiX callbacks, C ABI/embedding, or app-specific native kernels.

## Architectural Rule

Allowed in V4 Tier-2:

- generic continuation operators: count, threshold, any-hit flag, grouped count/sum/min/max/sum-count, argmin/argmax, bounded collect/top-k when they are app-name-free
- Python GPU-array front doors over those operators
- native fused kernels that keep the hot path in device/native execution

Not allowed in V4 Tier-2:

- app-identity kernels such as DBSCAN/Barnes-Hut/RayJoin as named app kernels
- raw OptiX callback exposure
- arbitrary user logic without the Tier-3 spike proving a constrained callback ABI

## Promoted To Current V4 Measured Surfaces

| V4 surface | Generic primitive | Current status | Main code |
| --- | --- | --- | --- |
| `v4_fixed_radius_count_threshold_2d_device_arrays` | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | Promoted and POD-measured for Torch CUDA. | `src/rtdsl/v4_fixed_radius.py`, `src/rtdsl/partner_adapters.py`, `src/rtdsl/optix_runtime.py` |
| `v4_closest_hit_grouped_argmin_3d_device_arrays` | `CLOSEST_HIT_GROUPED_ARGMIN_3D` | Promoted and POD-measured for Torch CUDA. | `src/rtdsl/v4_ray_triangle.py`, `src/rtdsl/optix_runtime.py` |
| `v4_ray_triangle_any_hit_flags_2d_device_arrays` | `RAY_TRIANGLE_ANY_HIT_FLAGS_2D` | Promoted and POD-measured for Torch CUDA. | `src/rtdsl/v4_ray_triangle.py`, `src/rtdsl/optix_runtime.py` |
| `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` | `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D` | Promoted and POD-measured for Torch CUDA by `goal4617`. | `src/rtdsl/v4_ray_triangle.py`, `src/rtdsl/optix_runtime.py` |
| `v4_point_group_nearest_witness_2d_device_arrays` | `POINT_GROUP_NEAREST_WITNESS_2D` | Promoted and POD-measured for Torch CUDA by `goal4618`. | `src/rtdsl/v4_point_group.py`, `src/rtdsl/optix_runtime.py` |

Current evidence is operator-level, not all-app benchmark evidence:

- `future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_32768_2026-06-24.json`

## V2/V2.x Primitive Assets Not Yet Promoted

| Candidate | Existing source | Native backing | V4 disposition |
| --- | --- | --- | --- |
| `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D` | `run_generic_ray_triangle_primitive_grouped_i64_reduction_3d`, `prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d` in `src/rtdsl/generic_primitives.py` | `rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction`, `rtdl_optix_static_triangle_scene_3d_ray_prepared_primitive_grouped_i64_reduction`, `rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction`, device-output symbol `rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction_device_outputs` | Promoted to measured V4 surface as `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` after goal4617 multi-width RTX A5000 POD evidence and external authorization. Scope: Torch CUDA, OptiX 8.0 maximum validated ABI; CuPy and OptiX 9.1 remain unmeasured. |
| `hit_stream_primitive_payload_grouped_sum_f64` | `prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d`, `run_generic_ray_triangle_event_ordered_payload_grouped_sum_3d` in `src/rtdsl/generic_primitives.py` | OptiX hit-stream producer plus CuPy grouped-sum consumer | Tier-1/V3-style fallback or comparison baseline, not primary V4 Tier-2, because it still routes through an intermediate hit stream and partner consumer. |
| `aggregate_tree_fused_weighted_vector_sum_2d` | `aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract` in `src/rtdsl/aggregate_tree_reference.py` | `rtdl_optix_prepare/run/destroy_aggregate_tree_fused_weighted_vector_sum_2d` | Rejected for V4.0 `goal4620` by Claude: kernel is Barnes-Hut / N-body force law and CUDA-only, not a generic RT-core Tier-2 operator. Do not relabel as generic weighted-vector sum. |
| `RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM_3D` | `ray_batch_any_hit_weighted_sum_device_weights` and graph-executor path in `src/rtdsl/optix_runtime.py` | `rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights_*` | Selected as current `goal4620` candidate after Claude review. Torch CUDA only; candidate evidence exists, but measured-catalog promotion is not authorized. |
| fixed-radius 3D count threshold / adjacency / grouped union | `fixed_radius_count_threshold_3d_optix_prepared_*` paths in `src/rtdsl/partner_adapters.py` and native `rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_*` symbols | OptiX 3D prepared count threshold and grouped union symbols | Candidate later Tier-2 expansion after grouped i64 reduction, especially for graph/component workloads. |
| ranked fixed-radius summaries / top-k / KNN-style summaries | native `rtdl_optix_aggregate_prepared_ranked_fixed_radius_neighbor_summaries_3d*` symbols | OptiX ranked summary / aggregate graph symbols | Candidate later, but needs a clean generic operator name and correctness/performance protocol before V4 promotion. |
| point-group threshold / nearest witness | native `rtdl_optix_count_prepared_point_group_threshold_reached_2d`, `rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns`, `rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_query_columns` | OptiX point-group threshold/witness symbols | Nearest-witness promoted to measured V4 surface as `v4_point_group_nearest_witness_2d_device_arrays` after goal4618 mixed6 RTX A5000 POD evidence and external authorization. Scope: RTDL-owned prepared search/groups, Torch CUDA query/output columns, OptiX 8.0 maximum validated ABI; CuPy and OptiX 9.1 remain unmeasured. |
| closed-shape / rayjoin / segment-shape relation symbols | many prepared point/shape/rayjoin symbols in `src/native/optix/rtdl_optix_prelude.h` | OptiX relation/geometry symbols | Deferred. Some may become generic relation operators, but they are too close to app/domain routes for immediate V4 Tier-2 promotion. |

## Current Candidate Targets

The current Tier-2 candidate implementation target in the V4 front door is:

- `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`

It was selected after the 3D fixed-radius No-Go and aggregate-tree rejection.
Candidate POD evidence exists for 32,768 and 131,072 rays/triangles, but
promotion to measured catalog status requires a separate completion/promotion
review.

Why grouped-i64 was targeted first:

1. It is explicitly generic: ray/triangle primitive payload grouped reduction, not an app kernel.
2. It is already backed by V2/V2.x front doors, native OptiX symbols, and tests.
3. It expands the V4 catalog beyond count-threshold / any-hit / argmin into grouped count/sum/min/max/sum-count, matching Claude's Tier-2 design.
4. It can be measured against the older V2 generic primitive and against the V3-style hit-stream + partner grouped-sum fallback.

Expected grouped-i64 V4 API shape:

```python
import rtdsl.v4 as rtdl_v4

session = rtdl_v4.prepare_primitive_grouped_i64_reduction_3d_device_arrays_v4(
    triangle_columns,
    ray_columns,
    primitive_group_ids=primitive_group_ids,
    primitive_values=primitive_values,
    group_count=group_count,
    partner="torch",
)

result = session.run(reduction="sum")
```

Grouped-i64 current status:

1. V4 Python front door is wired as a measured surface.
2. Native OptiX C ABI has a device-output symbol declaration/wrapper.
3. Python `optix_runtime` has direct device-output handoff wiring.
4. Local structure tests pass without CUDA.
5. Native rebuild passed on local Linux.
6. Local Linux GTX gate passed for `sum_count`, `min`, and `max` parity against
   both the legacy host-output primitive and an analytic fixture.
7. RTX A5000 POD gate passed for 32,768 and 131,072 rays/triangles with
   same-contract ratios of 7.933x and 22.856x against the legacy host-output
   primitive.
8. Goal4617 added multi-width RTX A5000 POD evidence for group widths 1, 16,
   and 256.
9. Claude and Antigravity authorized the measured-catalog promotion patch.

Local candidate evidence:

- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_lx1_local_gate_2026-06-24.md`
- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_lx1_local_gate_8192_32768_2026-06-24.json`
- `future/v4/evidence/v4_primitive_grouped_i64_torch_device_arrays_example_result_2026-06-24.json`

POD candidate evidence:

- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_primitive_grouped_i64_torch_device_arrays_example_result_pod_2026-06-24.json`

Required acceptance gates:

1. Correctness parity against CPU/reference rows for at least `count`, `sum`, `min`, `max`, and `sum_count`.
2. Hot path metadata must say no Python row objects and no host materialization in the measured run.
3. V4 catalog and planner must expose it as a measured Tier-2 operator only
   after POD evidence, external review, and release decision.
4. The implementation must not call it RayDB/Barnes-Hut/etc.
5. The comparison must include the older hit-stream + partner continuation where feasible, because V4's thesis is fused operator promotion, not just a prettier wrapper.

Point-group nearest-witness current status:

1. V4 Python front door is wired as a candidate surface.
2. It routes RTDL-owned prepared search/groups plus Torch CUDA query columns to
   direct Torch CUDA output columns.
3. RTX A5000 POD repeat gate passed at 32,768 and 131,072 query points with
   correctness parity.
4. The include-candidates GPU catalog gate passed with all nine examples,
   including both candidate examples.
5. It is not a true-zero-copy claim: native prepared search/group data are
   RTDL-owned; the direct device-array contract covers query and output columns.
6. Goal4618 added `mixed6` diagonal hit/no-hit POD evidence.
7. Claude and Antigravity authorized the measured-catalog promotion patch.

Point-group candidate evidence:

- `future/v4/evidence/v4_point_group_nearest_witness_candidate_pod_smoke_8192_2026-06-24.md`
- `future/v4/evidence/v4_point_group_nearest_witness_candidate_pod_smoke_8192_2026-06-24.json`
- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.md`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.json`

## Known Current Gap

This inventory is not yet a complete native-symbol census. It is enough to pick the next correct V4 implementation target, but a full release-quality V4 primitive map should later include every exported OptiX/Embree/Vulkan primitive and classify it as:

- measured V4 Tier-2
- V4 Tier-2 candidate
- Tier-1 fallback/comparison only
- Tier-3 spike candidate
- deferred/non-V4.0
