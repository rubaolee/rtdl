# Goal 1495: COLLECT_K_BOUNDED Device-Pointer ABI Contract

## Verdict

`goal1495_collect_k_device_pointer_abi_contract_defined`

## Proposed ABI

```c
int rtdl_optix_collect_k_bounded_i64_device(uint64_t candidate_rows_device_ptr, size_t candidate_count, size_t row_width, uint64_t rows_out_device_ptr, size_t row_capacity, size_t* emitted_count_out, uint32_t* overflowed_out, uint64_t* h2d_transfers_out, uint64_t* d2h_transfers_out, uint64_t* internal_device_transfers_out, char* error_out, size_t error_size)
```

## Required Behavior

- `validate_nonzero_device_pointers_when_counts_are_nonzero`
- `fail_closed_on_output_overflow_before_partial_success_claim`
- `preserve_goal1492_deduplicated_lexicographic_reference_rows`
- `record_transfer_accounting_even_when_zero`
- `do_not_allocate_hidden_host_content_buffers_for_candidate_rows`

## Minimum Acceptance Tests

- `goal1492_fixture_same_rows_no_overflow`
- `goal1492_fixture_capacity_two_overflow_fail_closed`
- `wrong_row_width_rejected`
- `null_device_input_rejected_when_candidate_count_nonzero`
- `null_device_output_rejected_when_row_capacity_nonzero`
- `goal1493_intake_accepts_measured_result_only_after_green_preflight`

## Claim Boundary

Goal1495 defines a proposed device-pointer ABI contract for future OptiX COLLECT_K_BOUNDED work. It does not implement the native symbol, does not run OptiX, does not prove true zero-copy, and does not authorize public speedup wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
