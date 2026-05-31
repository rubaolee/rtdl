# Goal2873 v2.5 Partner Conformance Matrix

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

Goal2868 external review feedback correctly warned that support labels and
descriptor rows are not the same thing as per-operation conformance evidence.
Goal2873 adds a separate partner x operation conformance index so the v2.5
packet can distinguish:

- reference-contract coverage;
- pod CUDA runtime smoke evidence;
- CUDA-gated smoke tests that still need current pod indexing;
- descriptor-only CuPy interop rows;
- unsupported fail-closed cells;
- explicit runtime conformance gaps.

This is intentionally stricter than the support matrix. A partner can be
supported as a preview and still remain a release blocker until runtime
conformance evidence is recorded.

## Implementation

Added:

- `src/rtdsl/v2_5_partner_conformance_matrix.py`
- `tests/goal2873_v2_5_partner_conformance_matrix_test.py`

Updated:

- `src/rtdsl/__init__.py`
- `src/rtdsl/v2_5_internal_readiness.py`

The readiness packet now validates `partner_conformance_matrix` and requires
this report, so the conformance matrix cannot drift as a loose document.

## Current Coverage

The matrix covers every v2.5 continuation operation for every declared partner:
`python_reference`, `triton`, `numba`, and `cupy_conformance`.

Important rows:

- Triton tie-break and ranked-summary risks are tied to Goal2872 pod CUDA
  smoke evidence:
  - `grouped_argmin_f64`
  - `grouped_argmax_f64`
  - `grouped_topk_f64`
- Triton float/vector smoke covered by Goal2872:
  - `segmented_sum_f64`
  - `grouped_vector_sum_f64x2`
- Triton edge components point at Goal2779 pod evidence.
- Triton count, min/max, compact, and bounded collect still have CUDA-gated
  tests but need current pod-indexed conformance records before any release
  packet treats them as closed.
- Numba preview rows for `segmented_count_i64` and `segmented_sum_f64` remain
  explicit runtime conformance gaps; Goal2666 only proves descriptors and lazy
  import boundaries.
- CuPy is descriptor-only for generic continuation rows except the scoped
  event-ordered grouped hit-stream consumer proven by Goals2771-2772.

## Boundary

Goal2873 is not a v2.5 release authorization, not a public speedup claim, not a
broad RT-core claim, not a whole-app speedup claim, not a true-zero-copy claim,
and not package-install wording.

The matrix deliberately reports `release_conformance_complete: false` and keeps
runtime gaps as release blockers. This is the right shape for an internal
hardening packet: honest, indexed, and hard to overread.

## Validation

Local validation:

```text
py -3 -m unittest tests.goal2873_v2_5_partner_conformance_matrix_test

Ran 7 tests in 0.314s
OK
```

Expanded validation should include the recent v2.5 readiness chain:

```text
py -3 -m unittest \
  tests.goal2873_v2_5_partner_conformance_matrix_test \
  tests.goal2872_triton_tie_break_conformance_smoke_test \
  tests.goal2871_hit_stream_torch_carrier_seam_authority_guard_test \
  tests.goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_test \
  tests.goal2869_v2_5_readiness_indexes_front_door_bypass_audit_test \
  tests.goal2867_v2_5_app_facing_front_door_bypass_audit_test \
  tests.goal2865_current_head_packet_after_front_doors_test \
  tests.goal2863_v2_5_readiness_indexes_front_doors_test \
  tests.goal2861_v2_5_generic_partner_front_door_completion_test \
  tests.goal2855_v2_5_current_canonical_harness_packet_runner_test \
  tests.goal2853_v2_5_readiness_next_actions_refresh_test \
  tests.goal2843_v2_5_execution_path_policy_test \
  tests.goal2806_v2_5_internal_readiness_packet_test \
  tests.goal2789_neutral_buffer_torch_carrier_reconciliation_test \
  tests.goal2775_hit_stream_neutral_seam_reconciliation_test

Ran 74 tests in 2.154s
OK (skipped=5)
```

Pod validation from pushed `main`:

```text
commit: 82d2dc98
scope: tests.goal2873_v2_5_partner_conformance_matrix_test

Ran 7 tests in 0.170s
OK
```

Expanded pod readiness/conformance slice:

```text
scope:
  tests.goal2873_v2_5_partner_conformance_matrix_test
  tests.goal2872_triton_tie_break_conformance_smoke_test
  tests.goal2871_hit_stream_torch_carrier_seam_authority_guard_test
  tests.goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_test
  tests.goal2869_v2_5_readiness_indexes_front_door_bypass_audit_test
  tests.goal2867_v2_5_app_facing_front_door_bypass_audit_test
  tests.goal2865_current_head_packet_after_front_doors_test
  tests.goal2863_v2_5_readiness_indexes_front_doors_test
  tests.goal2861_v2_5_generic_partner_front_door_completion_test
  tests.goal2855_v2_5_current_canonical_harness_packet_runner_test
  tests.goal2853_v2_5_readiness_next_actions_refresh_test
  tests.goal2843_v2_5_execution_path_policy_test
  tests.goal2806_v2_5_internal_readiness_packet_test
  tests.goal2789_neutral_buffer_torch_carrier_reconciliation_test
  tests.goal2775_hit_stream_neutral_seam_reconciliation_test

Ran 74 tests in 2.011s
OK
```

## Codex Verdict

`accept-with-boundary`
