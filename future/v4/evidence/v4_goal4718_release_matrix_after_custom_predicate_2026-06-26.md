# V4 Goal4718 Release Matrix After Custom Predicate Early-Exit

- validation: `passed`
- decision: `v4_python_edsl_operator_pushdown_release_candidate_pending_docs_and_final_review`
- measured surfaces: `10`
- V4 Python eDSL release candidate supported: `True`
- operator-pushdown workflow high-performance supported: `True`
- legacy all-app high-performance supported: `False`

## New V4 Workflow Row

- workflow: `ray_triangle_custom_predicate_early_exit_multi_hit`
- API surface: `v4_ray_triangle_custom_predicate_early_exit_3d_numba`
- claim class: `true_v4_operator_pushdown_workflow_win_candidate`
- V4/V2.14 primary geomean: `4.632757911153888`
- V4/V3.0.2 primary geomean: `4.632757911153888`
- minimum primary V4/V3.0.2 row: `2.054686620906942`
- correctness all passed: `True`
- denominator: `materialized_all_hit_ids_plus_device_predicate_reduce_fallback`

This row counts as V4 eDSL/operator-pushdown value. It does not count as
legacy all-app benchmark-suite speedup.

## Legacy Promoted-App State

- decision: `bounded_operator_v4_only__app_level_high_performance_not_supported`
- formal high-performance supported: `False`
- true V4 candidate app count: `1`
- contributing app count: `0`

## Allowed Claim If Later Gates Pass

- RTDL V4 is a Python eDSL/runtime for measured generic RT-core operator pushdown.
- The V4 front door has 10 measured generic operator/workflow surfaces.
- The constrained Numba custom predicate early-exit workflow measured 4.633x geomean versus V2.14/V3.0.2 materialized-device fallback at serious scale.
- Legacy promoted-app all-suite high-performance remains unsupported by Goal4669.

## Forbidden Claims

- broad all-app speedup
- all benchmark apps are faster
- arbitrary Python callback support
- raw OptiX callback support
- public Tier-3 support
- non-Python embedding/C ABI
- app-specific native kernels

## Non-Authorization

- V4 release is not authorized by Goal4718 alone.
- Public wording is not authorized before Goal4719 docs/examples cleanup.
- Broad all-benchmark speedup remains unauthorized.
