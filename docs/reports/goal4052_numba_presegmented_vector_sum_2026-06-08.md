# Goal4052 Numba Presegmented Vector Sum

Date: 2026-06-08

## Purpose

Goal4052 adds a generic Numba CUDA continuation path for grouped 2-D vector
sums when the caller already has `presegmented row_offsets`.

This is a language/runtime improvement, not an app-specific Barnes-Hut patch.
The generic contract remains:

- input columns: `row_offsets:int64`, `values_x:float64`, `values_y:float64`
- optional compatibility input: `group_ids:int64`
- output columns: `sum_x:float64`, `sum_y:float64`
- operation: `grouped_vector_sum_f64x2`

## What Changed

The Numba continuation runtime now exports:

`run_numba_grouped_vector_sum_f64x2_by_offsets(...)`

The partner front door `grouped_vector_sum_2d_partner_columns(...)` keeps the
existing atomic-by-`group_ids` Numba path for unsegmented inputs, but switches
to the new offset path when `row_offsets` is provided.

The offset kernel launches one CUDA thread per group and reduces rows in
`row_offsets[group]:row_offsets[group + 1]`. This mirrors the existing CuPy
offset-path shape, avoids cross-group global atomic adds, and records:

- `v2_5_numba_presegmented_offsets_used: True`
- `v2_5_numba_adapter_kernel: numba_grouped_vector_sum_offsets_f64x2_kernel`
- `v2_5_numba_global_atomic_add_used: False`
- `v2_6_neutral_handoff_validation_status: accept`
- `v2_5_numba_row_offset_validation_host_sync_used: True|False`

The public default is `validate_row_offsets=True`. Hot resident loops may pass
`validate_row_offsets=False` only after validating or constructing a stable
`row_offsets` layout elsewhere. The switch is explicit in both
`grouped_vector_sum_2d_partner_columns(...)` and
`execute_grouped_vector_sum_typed_stream_partner_columns(...)`; it is not hidden
dispatch and does not change partner selection.

## Boundary

This goal does not add Barnes-Hut force law, app semantics, or app-specific
native engine code. It also does not authorize true zero-copy wording, public
speedup claims, RT-core speedup claims, release claims, or whole-app speedup
claims.

The expected benchmark value is a better reusable continuation substrate for
presegmented typed streams, especially streams produced by aggregate/frontier
contracts. Any Barnes-Hut performance claim still needs separate measured pod
evidence at representative scale.

## Validation

`tests.goal4052_numba_presegmented_vector_sum_test` verifies:

- the new runtime function and offset kernel exist;
- the descriptor advertises optional `row_offsets`;
- the adapter preserves the older unsegmented Numba path;
- the CUDA path matches reference values when Numba CUDA is available;
- the metadata keeps the claim boundary locked down.
