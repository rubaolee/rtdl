# Call For Review: Phoenix V3 M56 LibRTS Set-B Metadata Diagnosis

Date: 2026-06-23

Status: `review_requested_no_pod_authorization_no_release`

## Request

Review M56, which locally diagnoses the M55 LibRTS
`set_b_control_candidate_missing` failure and adds a required current-source
signature preflight to the M47 LibRTS stability protocol.

This review must decide whether the diagnosis and preflight repair are
acceptable, without authorizing a POD rerun or any release/performance claim.

## Required Inputs

- `docs/reports/phoenix_v3_m56_librts_set_b_metadata_diagnosis_and_preflight_repair_2026-06-23.md`
- `scripts/v3_phoenix_m47_librts_stability_protocol.py`
- `tests/v3_phoenix_m47_librts_stability_protocol_test.py`
- `tests/v3_phoenix_m56_librts_set_b_metadata_diagnosis_test.py`
- `scripts/run_test_matrix.py`
- `docs/reports/phoenix_v3_m55_librts_authorized_pod_run_intake_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m55_librts_authorized_pod_run_intake_recorded_review_2026-06-23.md`
- `docs/reviews/codex_claude_antigravity_phoenix_v3_m55_goal_completion_3ai_consensus_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/optix_cold_single_shot_current_s01.stdout.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/embree_32768_stress_current_s01.stdout.json`

## Facts To Audit

- M55 remains valid red/open evidence and is not rewritten.
- The sampled M55 current payloads show
  `prepared_execution_session_runner_used=true`.
- The sampled M55 current payloads show
  `productized_execution_path=prepared_execution_session_runner`.
- The sampled M55 current payloads have expected AABB primitive contracts.
- The sampled M55 current payloads lack
  `prepared_execution_session_runner_metadata.set_b_control_candidate=true`.
- Local source already contains the intended Set-B metadata markings.
- M47 preflight previously ran named test modules but did not source-sign that
  the target current root contained those exact contract fields.
- M56 adds required preflight row `current_librts_set_b_source_signature`.
- The new preflight row inspects the target current root before any measured
  sample executes.
- Focused local tests pass.

## Requested Verdict Labels

Choose exactly one:

- `accept_m56_local_diagnosis_and_preflight_repair_no_pod_authorization`
- `request_m56_changes_before_completion`
- `reject_m56_diagnosis_or_scope`

## Review Questions

1. Is the diagnosis correctly scoped: productized runner executed, but metadata
   exposure/signature was insufficient?
2. Is it acceptable to treat stale or insufficiently source-signed target root
   as an inference from copied payloads rather than a fully proven remote-file
   fact?
3. Does the new `current_librts_set_b_source_signature` preflight materially
   prevent another M55-style paid run failure before samples execute?
4. Does the repair avoid changing M55 evidence or claiming watch-row closure?
5. Are the new tests sufficient for local completion of M56?
6. Is the next allowed action external completion audit and, only later, a
   separate reviewed authorization packet if another POD run is needed?

## Non-Authorization

This review must not authorize:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no second M47 run
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
- no watch-row closure
