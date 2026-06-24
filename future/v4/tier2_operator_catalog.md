# V4 Tier-2 Operator Catalog

Status: V4 development catalog, not a release announcement

V4's performance path is a catalog of generic fused RT operators. These are not
application-identity kernels. They are reusable continuation operators exposed
through Python GPU-array front doors.

## Measured Torch CUDA Surfaces

| Operator | API surface | Inputs | Outputs | Evidence |
| --- | --- | --- | --- | --- |
| Fixed-radius count threshold | `v4_fixed_radius_count_threshold_2d_device_arrays` | Torch device point columns | Torch device `query_ids`, `neighbor_counts`, `threshold_flags` | `future/v4/evidence/v4_section8_device_array_frontdoor_result_2026-06-24.json` |
| Closest-hit grouped argmin | `v4_closest_hit_grouped_argmin_3d_device_arrays` | Torch device triangle, ray, group, value, and index columns | Torch device `group_has_value`, `group_index`, `group_value` | `future/v4/evidence/v4_section8_closest_hit_grouped_argmin_device_frontdoor_result_2026-06-24.json` |
| Ray/triangle any-hit flags | `v4_ray_triangle_any_hit_flags_2d_device_arrays` | Torch device triangle columns, triangle AABBs, and ray columns | Torch device `any_hit_flags` | `future/v4/evidence/v4_section8_any_hit_flags_device_frontdoor_result_2026-06-24.json` |

## Common Boundary

All measured surfaces keep Python row objects and host result-table downloads
out of the hot path. They are V4 development evidence only.

Not authorized by this catalog:

- V4 release
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX claims
- CuPy performance claims
- application-specific native engine claims

## Next Catalog Requirements

Before V4 can be called complete, this catalog still needs:

- a release decision record after external review
- external review of the operator/callback planner boundary in `future/v4/callback_and_operator_planning.md`
- a reviewed GPU run of `scripts/v4_catalog_regression_gate.py --mode gpu`

The V4.0 versus V4.x scope boundary is defined in
`future/v4/v4_0_scope_gate.md` and checked by `scripts/v4_scope_gate.py`.
Catalog examples are checked by `scripts/v4_catalog_regression_gate.py`.

The complex-callback boundary is now represented by:

- `src/rtdsl/v4_operator_catalog.py`
- `future/v4/examples/operator_callback_planning.py`
- `future/v4/callback_and_operator_planning.md`

The boundary is intentionally conservative: scalar Numba device callbacks are
only Tier-3 spike candidates, while action-shaped callbacks are rejected for
V4.0 rather than exposed as raw OptiX hooks.
