# Call For Review: Goal2877 v2.5 Conformance Closure And Current Packet

Date: 2026-05-31

Please write an independent external review to:

- `docs/reviews/goal2877_<reviewer>_review_v2_5_conformance_closure_and_current_packet_2026-05-31.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

## Scope To Review

Review the work from `82d2dc98` through `f1ba66c3`:

- Goal2873: `docs/reports/goal2873_v2_5_partner_conformance_matrix_2026-05-31.md`
- Goal2874: `docs/reports/goal2874_triton_preview_current_pod_conformance_backfill_2026-05-31.md`
- Goal2875: `docs/reports/goal2875_numba_runtime_conformance_smoke_2026-05-31.md`
- Goal2876: `docs/reports/goal2876_current_packet_after_partner_conformance_closure_2026-05-31.md`
- Source: `src/rtdsl/v2_5_partner_conformance_matrix.py`
- Source: `src/rtdsl/v2_5_internal_readiness.py`
- Tests:
  - `tests/goal2873_v2_5_partner_conformance_matrix_test.py`
  - `tests/goal2874_triton_preview_current_pod_conformance_backfill_test.py`
  - `tests/goal2875_numba_runtime_conformance_smoke_test.py`
  - `tests/goal2876_current_packet_after_partner_conformance_closure_test.py`
  - `tests/goal2865_current_head_packet_after_front_doors_test.py`
- Pod artifacts:
  - `docs/reports/goal2876_current_packet_after_conformance_pod/goal2855_summary.json`
  - the seven child JSON files in the same directory.

## Claims To Verify

1. The new partner conformance matrix is materially different from the support
   matrix: it indexes partner x operation evidence and does not merely relabel
   unsupported or descriptor-only rows.
2. Triton preview operations now have pod-backed runtime conformance rows:
   Goal2872 for tie/ranked and ordered float smoke, Goal2779 for edge
   components, and Goal2874 for count/min/max/compact/bounded-collect backfill.
3. Numba fallback rows are no longer descriptor-only: Goal2875 records runtime
   CUDA conformance for `segmented_count_i64` and `segmented_sum_f64`, including
   invalid group-id fail-closed behavior.
4. CuPy remains descriptor-only except the scoped event-ordered grouped
   hit-stream consumer from Goals2771-2772. Do not accept any broader CuPy
   generic-kernel claim.
5. `v2_5_partner_conformance_matrix()` correctly reports
   `preview_runtime_conformance_complete: true`,
   `runtime_conformance_gap_count: 0`, and `release_blocker_count: 0`, while
   keeping `release_conformance_complete: false` and all public claim flags
   false.
6. Goal2876 is a clean seven-app current packet after conformance closure:
   `all_pass: true`, seven artifacts, source commit
   `cb9345bea472ac1167e8c289050146cc4fae30aa`, `source_dirty: []`,
   `dirty_artifacts: {}`, and no claim-boundary violations.
7. The self-dirty failed attempts are honestly documented and not used as
   accepted evidence.
8. The readiness packet now points at the Goal2876 current canonical runner
   summary and still does not authorize v2.5 release, public speedup wording,
   broad RT-core wording, whole-app wording, true-zero-copy wording, package
   install wording, or Triton preview auto-selection.

## Commands To Reproduce The Unit Gate

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2876_current_packet_after_partner_conformance_closure_test \
  tests.goal2875_numba_runtime_conformance_smoke_test \
  tests.goal2874_triton_preview_current_pod_conformance_backfill_test \
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
```

Expected pod result already recorded in Goal2876:

```text
Ran 89 tests in 2.511s
OK
```

## One-Sentence Reviewer Prompt

Please review Goals2873-2876 from `82d2dc98` through `f1ba66c3` and write `docs/reviews/goal2877_<reviewer>_review_v2_5_conformance_closure_and_current_packet_2026-05-31.md`, specifically auditing whether the partner x operation conformance matrix, Numba/Triton/CuPy evidence boundaries, and the clean seven-app Goal2876 packet are correct without authorizing v2.5 release or public performance claims.
