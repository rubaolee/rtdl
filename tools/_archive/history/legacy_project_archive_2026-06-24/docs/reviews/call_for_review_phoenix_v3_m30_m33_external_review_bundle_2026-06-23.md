# Call For Review: Phoenix V3 M30-M33 Runtime-Trunk Audit Bundle

Date: 2026-06-23
Status: `request_m30_m33_external_review_bundle_not_release`

This bundled review asks whether the current Phoenix V3 trunk-first work should
continue along the M30-M33 line:

- M30: RTNN repeat50 prepared runner as a second Set-A candidate under the
  post-M22/M29 framing;
- M31: shared Step-3 runner/residency audit surface;
- M32: shared Step-4 continuation-core audit surface;
- M33: promotion ledger classifying all current prepared-session helpers.
- M34 local addendum while awaiting external review: prepared-session surface
  ledger gate, which found and fixed one public export drift
  (`run_fixed_radius_threshold_reached_count_2d_prepared_session` was in the
  ledger but missing from `prepared_execution.__all__`).

It does not ask for release authorization, all-app POD authorization, public
speedup wording, broad V3-over-V2 wording, true-zero-copy wording, automatic
partner selection, V4 work, C ABI work, or embedding work.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
v4_work_authorized: false
```

## Required Context

Read these first:

- `docs/handoff/HANDOFF_PHOENIX_V3_REDESIGN_START_AT_STEP_0_2026-06-22.md`
- `docs/rebuild/v3/proposed_v3_redesign_build_the_runtime_trunk_first_2026-06-22.md`
- `docs/reviews/claude_phoenix_v3_external_review_2026-06-22.md`
- `docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md`
- `docs/reports/phoenix_v3_post_m22_step_alignment_and_next_work_2026-06-23.md`

Controlling fact: M22 all-app remains failed for release purposes. Focused
runtime-trunk progress does not erase that result and does not authorize all-app
rerun.

## Packets To Review

- `docs/reviews/call_for_review_phoenix_v3_m30_second_set_a_rtnn_prepared_runner_facts_only_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m31_shared_runner_audit_surface_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m32_continuation_core_audit_surface_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m33_step4_promotion_ledger_2026-06-23.md`

Supporting reports:

- `docs/reports/phoenix_v3_m30_second_set_a_candidate_rtnn_prepared_runner_2026-06-23.md`
- `docs/reports/phoenix_v3_m31_shared_runner_step3_audit_surface_2026-06-23.md`
- `docs/reports/phoenix_v3_m31_prepared_session_family_audit_inventory_2026-06-23.md`
- `docs/reports/phoenix_v3_m32_continuation_core_audit_surface_2026-06-23.md`
- `docs/reports/phoenix_v3_m33_prepared_session_step4_promotion_ledger_2026-06-23.md`
- `docs/reports/phoenix_v3_m34_prepared_session_surface_ledger_gate_2026-06-23.md`

Codex local self-review, not external consensus:

- `docs/reviews/codex_phoenix_v3_m30_m33_bundle_local_self_review_2026-06-23.md`

Gemini attempted M30, M31, M32, M33, this M30-M33 bundle, and the final
M30-M33 bundle after the review-bundle gate as interim reviews, but all failed
at authentication/client eligibility with `IneligibleTierError` /
`UNSUPPORTED_CLIENT`; those attempts are not consensus. Final blocked record:

- `docs/reviews/external_review_blocked_phoenix_v3_m30_m33_bundle_final_gemini_interim_review_2026-06-23.md`

## Current Local Validation

Dedicated review-bundle gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_m30_m33_review_bundle_gate_test \
  tests.v3_phoenix_external_verdict_intake_test \
  tests.v3_release_wording_gate_test
Ran 14 tests
OK
```

Prepared-session public surface ledger gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_session_surface_ledger_gate_test \
  tests.v3_phoenix_m30_m33_review_bundle_gate_test \
  tests.v3_phoenix_prepared_execution_session_runner_test
Ran 39 tests
OK
```

```text
PYTHONPATH=src;. py -3 scripts/v3_phoenix_prepared_session_surface_ledger_gate.py
status: pass
public_helper_count: 11
ledger_row_count: 11
step4_ready: 7
blocked_set_a_seed: 1
blocked_set_b_control: 3
missing_from_ledger: []
stale_ledger_rows: []
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_rtnn_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_evidence_test \
  tests.v3_phoenix_triangle_runner_m18_pod_ab_test \
  tests.v3_phoenix_m18_triangle_runner_harness_packet_test \
  tests.v3_phoenix_m16_triangle_runner_wiring_test \
  tests.v3_phoenix_barnes_hut_runner_parity_pod_ab_test \
  tests.v3_phoenix_step1_rtdbscan_trunk_probe_report_test \
  tests.v3_phoenix_rayjoin_point_location_runner_pod_ab_test \
  tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_librts_aabb_count_runner_test \
  tests.v3_release_wording_gate_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test
Ran 91 tests
OK
```

Windows emitted the known local warning:

```text
Could not find platform independent libraries <prefix>
```

The warning did not prevent tests from passing.

Full local V3 rebuild matrix after M34 also passes:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 113
Ran 590 tests in 73.107s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m34_final_20260623_130102.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m34_final_20260623_130102.stderr.txt
```

That matrix result is local contract/gate evidence only. It does not authorize
release, all-app POD spend, public speedup claims, broad V3-over-V2 claims,
true-zero-copy wording, automatic partner selection, V4 work, C ABI work, or
embedding work.

## Questions

1. Does M30 make RTNN a valid second Set-A candidate for continued focused
   review under the trunk-first plan, without becoming a release claim?
2. Is M31's shared Step-3 audit strict enough to distinguish runner execution
   from real residency-default readiness?
3. Is M32's Step-4 continuation-core audit strict enough to distinguish
   runner-callable continuation nodes from route prose?
4. Is M33's classification correct: seven local-audit-ready families, one
   blocked Set-A seed, and three blocked Set-B controls?
5. Is the AABB correction right: AABB helpers now report
   `set_a_probe_candidate=false` and `set_b_control_candidate=true`, and the
   LibRTS wrapper propagates those fields?
6. Is the M34 surface-ledger correction right: every public
   `prepared_execution.__all__` prepared-session helper is now present in the
   M33 ledger exactly once, and the threshold-reached helper is now exported?
7. Should the next work continue non-all-app trunk hardening and focused
   evidence only, or is there a blocking defect that must be fixed first?
8. Does this bundle authorize release, all-app POD spend, public speedup claims,
   broad V3-over-V2 claims, true-zero-copy wording, automatic partner
   selection, V4 work, C ABI work, or embedding work?

## Requested Verdict Labels

Choose exactly one:

- `accept_m30_m33_continue_trunk_first`
- `accept_with_amendments`
- `blocked_needs_code_or_classification_changes`
- `reject_m30_m33_wrong_direction`

Include blocking findings, required amendments if any, explicit answers to the
eight questions, and an explicit non-authorization block.
