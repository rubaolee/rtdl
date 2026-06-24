# Call For Review: Phoenix V3 M55 LibRTS Authorized POD Run Intake

Date: 2026-06-23

Status: `review_requested_no_release_no_rerun_authorization`

## Request

Review the copied M55 evidence from the single M54-authorized focused LibRTS
stability POD run.

This review must decide whether the M55 evidence should be accepted as a valid
red/watch-row-open intake, classified as setup-invalid because current metadata
was missing, or rejected for another reason.

## Required Inputs

- `docs/reports/phoenix_v3_m55_librts_authorized_pod_run_intake_2026-06-23.md`
- `docs/reviews/codex_claude_antigravity_phoenix_v3_m54_goal_completion_3ai_consensus_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m54_one_focused_librts_stability_pod_authorization_recorded_review_2026-06-23.md`
- `docs/reviews/antigravity_phoenix_v3_m54_goal_completion_audit_review_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_target_dry_run_20260623_2339/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/README.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/m55_execution_driver.log`

## Facts To Audit

- The M54 authorization allowed exactly one focused M47 LibRTS stability run.
- The target-machine dry-run used real current/V2.14 roots and Linux Python
  paths and had `failed_checks=[]`.
- The execution returned rc=0 and summary status
  `m47_librts_stability_protocol_run_complete_not_release`.
- The execution copied back 80 files including `summary.json`, `README.md`,
  preflight stdout/stderr, and all 32 measured stdout JSON files.
- Both scenarios are labeled `red_failure_watch_row_open`.
- Both scenarios have empty measured stderr and matching fixture/contract
  checks.
- Both scenarios have current metadata failure
  `set_b_control_candidate_missing`.
- `optix_cold_single_shot`: geomean `0.984404x`, median `0.979645x`, min
  `0.929253x`, pass count `6/8`.
- `embree_32768_stress`: geomean `0.931885x`, median `0.941006x`, min
  `0.801149x`, pass count `4/8`.

## Requested Verdict Labels

Choose exactly one:

- `accept_m55_valid_red_watch_rows_open_no_rerun`
- `classify_m55_setup_invalid_metadata_missing_requires_new_authorization`
- `reject_m55_evidence_incomplete_or_unsafe`

## Review Questions

1. Was the M55 execution within the exact M54 one-run authorization?
2. Is the copy-back complete enough for review?
3. Do the two red labels follow the M47 protocol rules?
4. Does `set_b_control_candidate_missing` make the run a valid red result, or a
   setup-invalid run that requires a new metadata repair and separate
   authorization?
5. Are the numerical results reported accurately without converting them into
   public speedup wording or watch-row closure?
6. What is the next allowed action?

## Non-Authorization

This review must not authorize:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no second M47 run unless the verdict explicitly says a new authorization
  packet is required and that later packet is separately approved
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
- no watch-row closure unless the reviewer explicitly accepts closure, which is
  not expected from the current red labels
