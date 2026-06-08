# Goal4053 Numba Presegmented Vector Sum Prepared Session

Date: 2026-06-08

## Purpose

Goal4052 proved that the direct Numba presegmented-offset kernel for
`grouped_vector_sum_f64x2` is faster than the older atomic-by-group Numba
kernel, but it also exposed a runtime problem: the full front door can lose the
kernel win because it pays per-call neutral-handoff validation and output
allocation/setup.

Goal4053 adds a generic prepared session for this continuation:

- `prepare_numba_grouped_vector_sum_f64x2_offsets_session(...)`
- `run_numba_prepared_grouped_vector_sum_f64x2_by_offsets(...)`
- `prepare_grouped_vector_sum_2d_partner_columns_session(...)`
- `run_grouped_vector_sum_2d_partner_columns_session(...)`

The session validates the neutral handoff once, reuses the output columns, and
replays the same generic no-atomic offset kernel over resident Numba CUDA
columns.

## Boundary

This is still a partner continuation, not RT traversal. It does not add
Barnes-Hut, force-law, or any app-specific native-engine behavior. It also does
not authorize true zero-copy wording, public speedup claims, RT-core speedup
claims, whole-app speedup claims, release claims, or automatic partner
selection.

The session currently supports `partner="numba"` only because it is closing the
specific Numba overhead uncovered by Goal4052. CuPy and Triton remain on their
existing one-shot paths unless a later goal adds matching prepared-session
support.

## Validation

`tests.goal4053_numba_presegmented_vector_sum_prepared_session_test` verifies:

- the generic prepared-session functions are exported;
- runtime and adapter source contain no Barnes-Hut or force-law terms;
- the prepared replay matches the one-shot Numba offset path when CUDA is
  available;
- metadata records `prepared_session_reused`, `output_columns_reused`, and
  `per_run_neutral_handoff_validation_used: False`;
- claim-boundary flags remain false.

