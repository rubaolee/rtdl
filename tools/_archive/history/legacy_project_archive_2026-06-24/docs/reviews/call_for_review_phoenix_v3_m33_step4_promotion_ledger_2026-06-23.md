# Call For Review: Phoenix V3 M33 Step-4 Promotion Ledger

Date: 2026-06-23
Status: `request_m33_external_review_not_release`

This review asks whether M33 correctly classifies the current
`prepared_execution_session_runner` helpers after M31/M32. It does not ask for
release authorization, all-app POD authorization, public speedup wording, broad
V3-over-V2 wording, or V4 work.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
```

## Patch Scope

Code/tests:

- `src/rtdsl/prepared_execution.py`
- `examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_librts_aabb_count_runner_test.py`
- `tests/v3_phoenix_m30_m33_review_bundle_gate_test.py`
- `scripts/run_test_matrix.py`

Reports:

- `docs/reports/phoenix_v3_m31_prepared_session_family_audit_inventory_2026-06-23.md`
- `docs/reports/phoenix_v3_m32_continuation_core_audit_surface_2026-06-23.md`
- `docs/reports/phoenix_v3_m33_prepared_session_step4_promotion_ledger_2026-06-23.md`
- `docs/reports/phoenix_v3_post_m22_step_alignment_and_next_work_2026-06-23.md`

Review packets / blocked review record:

- `docs/reviews/call_for_review_phoenix_v3_m31_shared_runner_audit_surface_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m32_continuation_core_audit_surface_2026-06-23.md`
- `docs/reviews/external_review_blocked_phoenix_v3_m32_gemini_interim_review_2026-06-23.md`
- `docs/reviews/external_review_blocked_phoenix_v3_m33_gemini_interim_review_2026-06-23.md`

## Change Summary

M33 records all 11 current prepared-session helper families:

- seven are Step-4 ready by local audit;
- one is a blocked Set-A seed;
- three are blocked Set-B controls.

The blocked entries are:

- fixed-radius self-query device-column helper: blocked Set-A seed;
- AABB range-intersection rows: blocked Set-B control;
- AABB native query-handle counts: blocked Set-B control;
- OptiX AABB prepared-query-set counts: blocked Set-B control.

These helpers may report `runtime_executed=true`, but tests now require their
M31/M32 audits to remain `incomplete_step3_audit` /
`incomplete_step4_continuation_audit` until real runtime-trunk, internal
residency, no-hot-host-stage, continuation-contract, and focused-gain-gate
facts exist.

The three AABB helpers now also report `set_a_probe_candidate=false` and
`set_b_control_candidate=true`, matching the M27 LibRTS/AABB Set-B triage.
The LibRTS app wrapper propagates those fields into the prepared-runner payload
so benchmark reports preserve the Set-B control classification.
M31 and M32 audit payloads also echo the same classification fields.

The M30-M33 review bundle now has a dedicated gate test that preserves
non-authorization wording, checks referenced packet paths, and prevents local
matrix evidence from being misread as external consensus.

## Validation

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_prepared_execution_session_runner_test
Ran 34 tests
OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_release_wording_gate_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test
Ran 39 tests
OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_librts_aabb_count_runner_test \
  tests.v3_release_wording_gate_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test
Ran 42 tests
OK
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

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 112
Ran 588 tests in 73.714s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m30_m33_bundle_gate_final_20260623_122007.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m30_m33_bundle_gate_final_20260623_122007.stderr.txt
```

The full matrix is local contract/gate evidence only. It is not external
consensus, POD evidence, release authorization, all-app authorization, or a
public performance claim.

Gemini interim review was retried for the updated M32 and M33 packets and remained
blocked by `IneligibleTierError` / `UNSUPPORTED_CLIENT`; it is not consensus.

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_m30_m33_review_bundle_gate_test \
  tests.v3_phoenix_external_verdict_intake_test \
  tests.v3_release_wording_gate_test
Ran 14 tests
OK
```

## Reviewer Questions

1. Is M33's ready/control classification aligned with the Phoenix V3
   trunk-first redesign?
2. Is it correct to keep the runner-shaped blocked entries blocked even though
   they report `runtime_executed=true`?
3. Are the missing facts sufficient grounds to prevent Step-3/Step-4 promotion?
4. Does M33 avoid app-specific optimization and preserve the runtime-capability
   focus?
5. Should M31/M32/M33 be reviewed together before any focused POD rerun or
   all-app reconsideration?
6. Does this packet authorize release, public speedup claims, broad
   V3-over-V2 claims, all-app POD spend, true-zero-copy wording, automatic
   partner selection, or V4 work?

## Requested Verdict Labels

Choose exactly one:

- `accept_m33_step4_promotion_ledger`
- `accept_with_amendments`
- `blocked_needs_code_or_classification_changes`
- `reject_m33_wrong_direction`

Include blocking findings, required amendments if any, explicit answers to the
six questions, and an explicit non-authorization block.
