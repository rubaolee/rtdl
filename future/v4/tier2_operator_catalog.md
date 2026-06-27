# V4 Tier-2 Operator Catalog

Status: V4 Python eDSL/operator-pushdown catalog with 10 measured generic
operator/workflow rows. The current app-level boundary still does not authorize
broad legacy all-app high-performance wording.

V4's performance path is a catalog of generic fused RT operators. These are not
application-identity kernels. They are reusable continuation operators exposed
through Python front doors with explicit partner scope and explicit baselines.

## Measured Tier-2 Surfaces

| Operator | API surface | Inputs | Outputs | Partner scope | Representative ratio | Baseline / denominator | Scale |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| Fixed-radius count threshold | `v4_fixed_radius_count_threshold_2d_device_arrays` | Torch device point columns | Torch device `query_ids`, `neighbor_counts`, `threshold_flags` | Torch CUDA | `1.697x` | Torch brute-force/reference | script default fixture; repeat `7`, warmup `1` |
| Closest-hit grouped argmin | `v4_closest_hit_grouped_argmin_3d_device_arrays` | Torch device triangle, ray, group, value, and index columns | Torch device `group_has_value`, `group_index`, `group_value` | Torch CUDA | `1.257x` | Torch brute-force/reference | script default grouped-argmin fixtures; repeat `7`, warmup `1` |
| Ray/triangle any-hit flags | `v4_ray_triangle_any_hit_flags_2d_device_arrays` | Torch device triangle columns, triangle AABBs, and ray columns | Torch device `any_hit_flags` | Torch CUDA | `5.671x` | Torch brute-force/reference | `max_torch_reference_count=8192`; repeat `5`, warmup `1` |
| Primitive grouped-i64 reduction | `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` | Torch device triangle/ray columns plus prepared primitive group/value payload | Torch device `group_counts`, `group_sums`, `group_mins`, `group_maxs` | Torch CUDA | `1.384x` | Torch brute-force/reference | ray counts `32768,131072`; group widths `1,16,256`; repeat `7`, warmup `2` |
| Point-group nearest witness | `v4_point_group_nearest_witness_2d_device_arrays` | RTDL-owned prepared search/groups plus Torch device query columns | Torch device `query_ids`, `neighbor_ids`, `distances` | Torch CUDA | `389.707x` | brute-force nearest-witness reference | query counts `32768,131072`; fixtures `mixed4,mixed6`; repeat `7`, warmup `2`; scale-dependent O(n^2)-vs-BVH win |
| Ray/triangle any-hit weighted sum | `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` | Torch device triangle/ray columns plus Torch device `uint64` ray weights | Torch device `uint64[1]` weighted-hit sum scalar | Torch CUDA | `1.482x` | Torch brute-force/reference comparable route | measured shapes `32768,131072,262144,524288` |
| Fixed-radius graph component union | `v4_fixed_radius_graph_component_union_3d_device_arrays` | Numba-scoped prepared 3D clustered point route | Component label columns with canonical component signature | Numba | `1.203x` | legacy prepared-runner wall route; Embree controls recorded | clustered3d `262144` points; repeat `5`, warmup `1` |
| AABB all-ops count | `v4_aabb_index_query_2d_all_ops_count_prepared_runner` | RTDL native prepared AABB boxes and point/box queries | Count scalars for all AABB query operations | RTDL native | `164.716x` | Embree same-contract prepared AABB query control | `1000000` boxes, `1000` queries, all ops, `240` repeats; scale-dependent indexed-control win |
| Aggregate-frontier device columns | `v4_aggregate_frontier_device_columns_2d_prepared_runner` | RTDL native prepared aggregate tree and source device columns | Device-resident aggregate-frontier columns for downstream continuation | RTDL native + explicit CuPy continuation | `310.024x` hot over V2.14; `0.998x` hot versus V3.0.2 control | V2.14 OptiX host-materialized frontier plus host continuation | Barnes-Hut-shaped aggregate-frontier probe, `32768` bodies, repeat `7`, warmup `2`; V2.14 host-frontier bottleneck removal, not a V4-over-V3 speed win |
| Custom predicate early-exit | `v4_ray_triangle_custom_predicate_early_exit_3d_numba` | RTDL-generated OptiX any-hit route plus constrained Numba C-ABI boolean predicate | Accepted flags or first accepted hit under RTDL-owned action | Numba | `4.633x` serious-scale primary geomean; min primary row `2.055x` | V2.14/V3.0.2 materialized-device all-hit fallback | multi-hit ray/triangle custom predicate early-exit, `262144` and `524288` rays, repeat `5`, warmup `2`; V4 operator-pushdown workflow win, not broad all-app speedup |

There are currently no open Tier-2 candidate surfaces in the V4 front door.
The former `v4_fixed_radius_ranked_summary_3d_prepared_runner` candidate is
deferred after serious-scale evidence showed no material V4 release win.

## Important Caveats

- The ratios above are representative frozen scorecard ratios against the
  named denominators, not whole-application speedup claims.
- The later app-level V2.14/V3.0.2/V4 check did not support formal app-level
  high-performance V4 wording; use `docs/app_level_benchmark_summary.md` for
  that boundary.
- Most surfaces sit in the `1.2x-1.7x` core cluster. Point-group nearest
  witness and AABB all-ops are large scale-dependent algorithmic-complexity
  wins, not evidence of near-hand-written-OptiX kernel quality.
- Torch CUDA measurements are scoped to the validated RTX A5000 / OptiX 8.0 /
  driver 570.195.03 path unless a surface says otherwise.
- Component union is Numba-scoped operator coverage, not whole-app RTDBSCAN
  speedup wording.
- AABB all-ops is RTDL-native operator coverage with Embree as the
  same-contract-family control. It is not LibRTS paper reproduction or authors
  code comparison.
- Weighted sum is a comparable-route route win, not a pure kernel-vs-kernel
  speedup.
- Broad CuPy performance wording is not authorized. The aggregate-frontier row
  has one explicit CuPy downstream-continuation measurement and must not be
  generalized into a CuPy performance claim.
- public true-zero-copy wording is not authorized.
- Custom predicate early-exit is constrained to pure Numba C-ABI predicates and
  RTDL-owned actions such as `terminate_on_first_accept`; arbitrary Python
  callbacks and raw OptiX callbacks remain unauthorized.

## Planner Boundary

The operator/callback planner routes recognized generic operators and fails
closed otherwise.

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("grouped_i64", partner="torch")
print(plan.status)
print(plan.api_surface)
```

Scalar custom callbacks remain Tier-3 spike-only. Action-shaped callbacks that
mutate shared state, allocate dynamically, or produce variable-length output are
rejected/deferred for V4.0.

## Evidence

Detailed scorecard and validation evidence lives under `future/v4/` and
`future/v4/evidence/` for reviewers. This catalog is the current public
operator surface.

## Non-Authorization

Not authorized by this catalog:

- broad V4 speedup wording;
- broad V4-over-V2.14 speedup wording;
- whole-application speedup wording;
- all-benchmark speedup wording;
- Tier-3 callback/PTX claims;
- raw OptiX callback claims;
- CuPy performance claims;
- embedding/C-ABI claims;
- non-Python host binding claims;
- application-specific native engine claims.
