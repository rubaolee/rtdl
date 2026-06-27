# V4 Goal4716 Custom Predicate Early-Exit Productization Evidence

- status: `passed`
- api surface: `v4_ray_triangle_custom_predicate_early_exit_3d_numba`
- measured catalog surface count: `10`
- primary V4/V3 focused geomean: `3.608025018751732`
- min primary V4/V3 row: `1.9761904761904763`

## Catalog Row

- operator: `ray_triangle_custom_predicate_early_exit`
- measured partners: `('numba',)`
- accepted callback shapes: `('pure_boolean_numba_cabi_device_function', 'boolean_numba_cabi_device_function')`
- accepted actions: `('terminate_on_first_accept', 'filter_accept_flags')`
- comparison class: `operator_pushdown_vs_materialized_device_fallback`

## Boundaries

- release authorized: `False`
- whole-app speedup claim authorized: `False`
- arbitrary callback authorized: `False`
- raw OptiX callback authorized: `False`

Goal4716 productizes the focused Goal4715 win as a V4 measured operator-pushdown surface. It does not authorize release.
