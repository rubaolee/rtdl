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

The offset kernel launches one CUDA block per group and reduces rows in
`row_offsets[group]:row_offsets[group + 1]`. It avoids cross-group global
atomic adds and records:

- `v2_5_numba_presegmented_offsets_used: True`
- `v2_5_numba_adapter_kernel: numba_grouped_vector_sum_offsets_f64x2_kernel`
- `v2_5_numba_global_atomic_add_used: False`
- `v2_6_neutral_handoff_validation_status: accept`

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

