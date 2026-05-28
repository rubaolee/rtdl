# Goal2670: v2.5 Segmented Min/Max Reference Contract

Status: reference/descriptor contract only, no partner kernel yet.

Date: 2026-05-27

## Purpose

RayDB count and sum mapped cleanly to the first v2.5 grouped continuations, but
RayDB `min` and `max` were blocked because the v2.5 contract did not yet define
generic segmented min/max semantics.

This goal adds reference semantics for:

- `segmented_min_f64`
- `segmented_max_f64`

It does not add Triton or Numba kernels. Partner implementations remain a
future CUDA-pod task.

## Contract

Inputs:

- `group_ids:int64`
- `values:float64`
- `group_count:int`

Outputs:

- `group_ids:int64` for groups that have at least one row;
- `mins:float64` or `maxes:float64`;
- `missing_group_ids:int64` for groups with no rows.

NaN values are rejected so the reference contract stays deterministic and does
not inherit backend-specific NaN ordering behavior.

## RayDB Integration

`describe_raydb_v2_5_partner_continuation(mode)` now maps:

| RayDB mode | v2.5 continuation plan |
| --- | --- |
| `count` | `segmented_count_i64` |
| `sum` | `segmented_sum_f64` |
| `min` | `segmented_min_f64` |
| `max` | `segmented_max_f64` |
| `avg_as_sum_count` | `segmented_sum_f64` + `segmented_count_i64` |

Count/sum use the existing Triton/Numba preview descriptors. Min/max use
generic partner descriptor-only specs until kernels exist.

## Boundary

This does not authorize:

- public speedup claims;
- benchmark promotion;
- RT traversal replacement;
- app-specific native engine logic;
- claiming Triton/Numba min/max execution before kernels and pod evidence.

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2669_v2_5_raydb_continuation_plan_test
```

## Next Work

The next local work can define Triton/Numba min/max design constraints, but
actual implementation quality and performance require CUDA pod validation.
