# RTDL V4 Front Door

Status:

```text
V4.0 tag target ready, complete Goal4756 RT-core app matrix, bounded public-tag review approved, clean wheel smoke passed
```

V4 is the Python GPU-array RT-core lane and a V2/V3 superset. Users can keep
using mature V2.14/V3 routes through the current system, and V4 adds generic
operator-pushdown surfaces for workloads that match measured operators.

Use one import:

```python
import rtdsl.v4 as rtdl_v4
```

## Complete App Matrix

Goal4756 is the current app-level benchmark boundary:

| App | V4/V2.14 hot | V4/V3.0.2 hot | Reading |
| --- | ---: | ---: | --- |
| RTDBSCAN | `0.998x` | `0.993x` | Parity/control. |
| RayDB-style | `1.113x` | `1.111x` | Modest hot gain. |
| Triangle counting | `4.360x` | `1.021x` | Material candidate. |
| LibRTS spatial index | `0.999x` | `1.002x` | Parity/control. |
| Hausdorff XHD threshold route | `1.032x` | `0.983x` | Threshold same-primitive parity/control. |
| Robot collision | `1.020x` | `1.000x` | Parity/control. |
| Contact manifold | `1.116x` | `1.477x` | Parity/control/modest gain. |
| RTNN | `1.029x` | `1.024x` | Parity/control. |
| Spatial RayJoin shape-pair | `1.000x` | `1.004x` | Serious generated-input parity/control. |
| Barnes-Hut aggregate frontier | `286.142x` | `0.993x` | Material V3/V4-over-V2.14 candidate, not a new V4-over-V3 speed claim. |

Evidence:

- `future/v4/evidence/v4_goal4756_serious_all30_generated_spatial_2026-06-26/`
- `future/v4/v4_goal4756_final_rt_core_matrix_release_readout_2026-06-26.md`

## Measured V4 Operator/Workflow Surfaces

| Surface | Partner scope | Representative result | Boundary |
| --- | --- | ---: | --- |
| Fixed-radius count-threshold | Torch CUDA | `1.697x` | Operator row, not whole-app claim. |
| Closest-hit grouped argmin | Torch CUDA | `1.257x` | Operator row. |
| Ray/triangle any-hit flags | Torch CUDA | `5.671x` | Operator row. |
| Primitive grouped-i64 reduction | Torch CUDA | `1.384x` | Operator row. |
| Point-group nearest witness | Torch CUDA | `389.707x` | Scale-dependent algorithmic win. |
| Ray/triangle any-hit weighted sum | Torch CUDA | `1.482x` | Operator row. |
| Fixed-radius graph component union | Numba | `1.203x` | Measured constrained route. |
| AABB all-ops count | RTDL native | `164.716x` | Scale-dependent indexed-control win. |
| Aggregate-frontier device columns (`v4_aggregate_frontier_device_columns_2d_prepared_runner`) | RTDL native + CuPy continuation | `310.024x` over V2.14; `0.998x` vs V3 | V2.14 host-boundary removal; no V4-over-V3 speed claim. |
| Custom predicate early-exit (`v4_ray_triangle_custom_predicate_early_exit_3d_numba`) | Numba C-ABI predicate | `4.633x` | V4-specific operator-pushdown workflow win. |

These rows have explicit denominators and partner scopes. Do not turn them into
a blanket "V4 is faster for everything" claim.

most measured operators are 1.2x-1.7x against their stated brute-force partner/CPU baselines;
point-group nearest witness and AABB all-ops are large
scale-dependent algorithmic-complexity wins. Keep those denominators attached to
the operator rows.

## Complex Callback Boundary

V4.0 does not expose raw OptiX callbacks. Complex user logic is handled by a
strict planner:

- recognized generic operators route to measured V4 surfaces;
- constrained pure Numba predicates are supported only where measured;
- arbitrary action callbacks, dynamic allocation, and variable-length mutation
  remain V4.1/Tier-3 work.

## Run The Public Examples

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 examples\v4\operator_callback_planning.py --case complex-callback
py -3 examples\v4\custom_predicate_early_exit_planning.py
py -3 examples\v4\primitive_grouped_i64_reduction_torch_device_arrays.py --dry-run
py -3 examples\v4\point_group_nearest_witness_torch_device_arrays.py --dry-run
py -3 examples\v4\ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
py -3 examples\v4\aabb_index_all_ops_count.py --dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/v4/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python examples/v4/custom_predicate_early_exit_planning.py
PYTHONPATH=src:. python examples/v4/primitive_grouped_i64_reduction_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/point_group_nearest_witness_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/aabb_index_all_ops_count.py --dry-run
```

## Non-Claims

## External Review Update

Antigravity reviewed the consolidated Gemini-style full-coverage V4 packet:

- `future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md`

Verdict:

```text
approve_close_gemini_debt_and_allow_v4_0_public_tag
```

This authorizes the bounded V4.0 public tag under the current framing. It does
not authorize broader speedup, paper-reproduction, Tier-3 callback, raw OptiX
callback, or no-copy tree-build claims. The git tag target must be a clean
committed release tree verified by clean checkout and installed-wheel smoke.

This page does not authorize:

- all benchmark apps are faster;
- broad V4-over-V2.14 speedup wording;
- broad V4-over-V3 speedup wording;
- whole-application speedup claims;
- public true-zero-copy claims;
- Tier-3 callback/PTX support claims;
- broad CuPy performance claims beyond explicitly named measurements;
- raw OptiX callback support claims;
- app-specific native engine/kernel claims;
- embedding/C-ABI claims;
- non-Python host binding claims.
