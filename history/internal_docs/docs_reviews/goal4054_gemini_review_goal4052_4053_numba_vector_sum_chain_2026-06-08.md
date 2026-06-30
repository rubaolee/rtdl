# Independent Gemini Review: Goal4052/4053 Numba Presegmented Vector Sum Chain

Date: 2026-06-08
Reviewer: Gemini CLI
Verdict: `accept`

## Overview

This review covers **Goal4052** (Numba Presegmented Vector Sum Chain) and **Goal4053** (Numba Presegmented Vector Sum Prepared Session). These goals address a runtime bottleneck in the Numba partner continuation path for grouped vector sums by introducing an offset-based kernel and a prepared session mechanism to minimize host-side overhead and redundant validation.

## Required Checks

### 1. Genericity and Scope
- **Check:** Verify Goal4052 is generic and avoids app-specific logic.
- **Finding:** **Pass.** The implementation in `src/rtdsl/numba_partner_continuation.py` adds `run_numba_grouped_vector_sum_f64x2_by_offsets` which operates on generic `row_offsets`, `values_x`, and `values_y`. No Barnes-Hut or force-law logic is present in the runtime or adapters. The `claim_boundary` in descriptors and metadata explicitly restricts the scope to generic continuation.

### 2. Safety Defaults
- **Check:** Verify `validate_row_offsets=True` is the default and no-validation is explicit.
- **Finding:** **Pass.** 
  - `run_numba_grouped_vector_sum_f64x2_by_offsets` and the corresponding front-door adapters in `src/rtdsl/partner_adapters.py` and `src/rtdsl/v2_8_segmented_typed_stream_adapter.py` all default to `validate_row_offsets=True`.
  - The `validate_row_offsets=False` path is only accessible via explicit caller request and is recorded in metadata (e.g., `v2_5_numba_row_offset_validation_host_sync_used`).

### 3. Prepared Sessions
- **Check:** Verify Goal4053 validates neutral handoff once and reuses output columns.
- **Finding:** **Pass.**
  - `prepare_grouped_vector_sum_2d_partner_columns_session` performs `validate_v2_6_neutral_partner_handoff` once during preparation.
  - The session metadata records `per_run_neutral_handoff_validation_used: False` and `output_columns_reused: True`.
  - Replay via `run_numba_prepared_grouped_vector_sum_f64x2_by_offsets` skips validation and allocation, using the buffers prepared in the session.

### 4. Pod Evidence Consistency
- **Check:** Verify performance claims and result correctness.
- **Finding:** **Pass.**
  - **Goal4052 Evidence:** Pod probe shows the Numba offset kernel is ~2.55x to 2.65x faster than the atomic-by-group kernel. One-shot adapter overhead is visible but doesn't invalidate the kernel win.
  - **Goal4053 Evidence:** Prepared sessions show ~3.77x to 3.89x speedup over the atomic path and ~3.79x to 9.09x speedup over the one-shot adapter (increasing with group count).
  - **Correctness:** Results in both probes match the reference atomic implementation (`matches_atomic: true`).

### 5. Claim Boundaries
- **Check:** Verify claim-boundary flags remain false and no overclaims.
- **Finding:** **Pass.** All relevant authorization flags (`rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `public_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, `release_authorized`) are explicitly set to `False` in the code and verified in the pod probe metadata. The `claim_boundary` text clearly states that these are preview integrations and do not authorize public claims.

## Verdict Rationale

The implementation successfully provides a generic, safe, and high-performance continuation path for Numba. By separating kernel execution from per-call validation and allocation, Goal4053 provides the necessary runtime substrate for efficient presegmented streams without violating architectural boundaries or claim policies. The evidence provided is thorough and internally consistent.

I recommend **accepting** both goals.
