# Goal3778 - Numba Grouped Vector-Sum Front Door

Date: 2026-06-07

## Purpose

Goal3778 closes a partner-choice gap for the generic grouped vector-sum
continuation:

`grouped_vector_sum_f64x2`

Earlier v2.x work exposed this operation through Torch, Triton preview, and
CuPy paths, but Numba was not an executable front-door partner for the same
generic contract. That was inconsistent with the project direction: users
should be able to choose a supported partner explicitly when they need custom
continuation logic.

## What Changed

This goal adds:

- `describe_numba_grouped_vector_sum_f64x2()`;
- `run_numba_grouped_vector_sum_f64x2(...)`;
- a Numba CUDA kernel that independently sums paired `float64` components per
  integer group id;
- `partner="numba"` support in `partner_group_vector_sum_2d_by_key(...)`;
- `partner="numba"` support in `grouped_vector_sum_2d_partner_columns(...)`;
- support-matrix promotion of `grouped_vector_sum_f64x2` into
  `V2_5_NUMBA_PREVIEW_OPERATIONS`;
- typed-stream front-door compatibility through
  `execute_grouped_vector_sum_typed_stream_partner_columns(...)`.

The input/output contract stays app-agnostic:

| Field | Type |
| --- | --- |
| `group_ids` | `int64[row_count]` |
| `values_x` | `float64[row_count]` |
| `values_y` | `float64[row_count]` |
| `group_count` | nonnegative integer |
| `sum_x` | `float64[group_count]` |
| `sum_y` | `float64[group_count]` |

Group ids are validated with the existing Numba device-resident error-flag
mode. Invalid group ids fail closed before a successful result is accepted.

## Boundary

This goal does not add force law, Barnes-Hut math, N-body policy, app-specific
native-engine logic, hidden partner dispatch, RT-core traversal replacement, or
user shader injection.

This goal does not authorize release action, public speedup wording, true
zero-copy wording, broad RT-core wording, whole-app acceleration wording, AMD
hardware claims, or paper-reproduction claims.

The result is a generic partner-continuation front door. It helps apps such as
Barnes-Hut express vector accumulation through a user-selected Numba partner,
but the app still owns the meaning of the vector components.

## Validation

Local validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3778_numba_grouped_vector_sum_front_door_test tests.goal2696_v2_5_partner_support_matrix_test tests.goal2781_grouped_vector_sum_adapter_test tests.goal3169_barnes_hut_grouped_vector_typed_stream_front_door_test
```

Pod evidence will be recorded in:

`docs/reports/goal3778_numba_grouped_vector_sum_front_door_a5000.json`

The pod artifact must remain scoped as Numba CUDA functional evidence on NVIDIA
hardware. It is not AMD HIPRT evidence and not a performance claim.
