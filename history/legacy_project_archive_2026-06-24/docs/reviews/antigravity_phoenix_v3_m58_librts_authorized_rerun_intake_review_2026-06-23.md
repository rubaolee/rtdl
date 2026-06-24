# Antigravity Review: Phoenix V3 M58 LibRTS M57-Authorized Rerun Intake

**Date:** 2026-06-23  
**Reviewer:** Antigravity (independent external review)  
**Candidate packet:** [call_for_review_phoenix_v3_m58_librts_m57_authorized_pod_rerun_intake_2026-06-23.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reviews/call_for_review_phoenix_v3_m58_librts_m57_authorized_pod_rerun_intake_2026-06-23.md)

---

## Verdict

**accept_m58_valid_yellow_watch_rows_open_no_closure**

---

## Findings

**P0 Findings (Blockers): None**

No correctness failures, contract violations, or scope breaches were detected.

**P1 Findings (Requirements): None**

**P2 Findings (Notes):**
- **Optix Cold-Shot Performance Weakness:** The `optix_cold_single_shot` scenario continues to show a performance regression under V3. The geomean speedup is `0.979485x` (slower than V2.14 on average), with a minimum of `0.833096x` and only `3/8` samples achieving a speedup ≥ 0.95x. This remains an active stability concern.
- **Traceability of Authorization Token:** While the token is not archived directly inside `summary.json`, the execution logs and folder alignment verify that the single authorized token was consumed by the runner harness.
- **Git Revision Preflight Check:** The `current_git_revision` check returned `returncode: 128` (expected since the target sync was an archive export, not a git checkout), which is marked `required: false` in the runner config. This is not a blocker.

---

## Audit Checklist & Answers to Review Questions

**1. Was M58 within the exact M57 one-run authorization?**  
**Yes.** The execution satisfied all M57 consensus conditions:
- **Dry-run performed first:** Gated target dry-run was executed first (output saved under [phoenix_v3_m58_librts_m57_authorized_target_dry_run_20260624_0054](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/rebuild/v3/evidence/phoenix_v3_m58_librts_m57_authorized_target_dry_run_20260624_0054)) with `--run-preflight`.
- **Preconditions checked:** The dry-run preflight checks succeeded with `failed_checks=[]` and `returncode=0` on `current_librts_set_b_source_signature`.
- **Single run executed:** The execution occurred after the dry-run (output saved under [phoenix_v3_m58_librts_m57_authorized_execution_20260624_0055](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/rebuild/v3/evidence/phoenix_v3_m58_librts_m57_authorized_execution_20260624_0055)) and consumed the token exactly once.
- **Scope preserved:** Unchanged M47 scenarios (`optix_cold_single_shot`, `embree_32768_stress`), exactly 8 paired samples per scenario, and explicit Python path `/usr/bin/python3` were used.

**2. Is the target dry-run/source-signature gate evidence sufficient?**  
**Yes.** The source-signature check logs in `preflight_current_librts_set_b_source_signature.stdout.txt` record all 8 code-level signatures (`prepared_embree_count_helper_present`, `prepared_optix_query_set_helper_present`, `prepared_helpers_mark_set_b_control`, `prepared_helpers_mark_not_set_a_probe`, `prepared_optix_helper_marks_prepared_query_mode`, `librts_app_exposes_payload_set_b`, `librts_app_exposes_metadata_set_b_twice`, `librts_app_exposes_optix_prepared_query_mode`) as `true` with `"failed": []`. The preflight unit tests passed successfully.

**3. Is the execution copy-back complete enough for review?**  
**Yes.** The copied execution directory contains all required items:
- 32 measured stdout JSON files (8 samples × 2 scenarios × 2 trees)
- 39 stderr/preflight log files
- `summary.json` containing complete metrics and preflight details
- `m58_execution_driver.log` detailing the exact run order (alternating samples)

**4. Do the M47 yellow labels follow from the summary metrics and metadata?**  
**Yes.** Both scenarios are correctly labeled `yellow_stability_boundary_watch_row_open`:
- `embree_32768_stress`: Geomean speedup of `1.030501x` is slightly positive, but `2/8` samples are below the 0.95x threshold (minimum of `0.870986x`), and high inter-sample variance prevents marking it green.
- `optix_cold_single_shot`: Geomean speedup of `0.979485x` is less than 1.0x (regression), with a minimum of `0.833096x` and only `3/8` samples crossing the 0.95x threshold. It is a clear performance regression/stability issue.

**5. Is `set_b_control_candidate_missing` cleared?**  
**Yes.** Every paired sample across both scenarios reports `current_metadata_failures: []`, `current_metadata_ok: true`, and `fixture_contract_matches: true`. The M55 metadata emission failure has been fully resolved.

**6. Is neither watch row green/closed?**  
**Yes.** Neither row is green or closed. Both remain `yellow_stability_boundary_watch_row_open`. The performance numbers (especially the regression on Optix and high variance on Embree) dictate that the watch rows must remain open.

**7. What is the next allowed action?**  
The next allowed actions are:
1. Record M58 as accepted evidence intake with both LibRTS watch rows `yellow_stability_boundary_watch_row_open` (completed by this review consensus).
2. Decide whether these open watch rows represent a permanent disclaimer or an actionable performance gap that requires new implementation work (which would require a separate consensus and authorization).

---

## Non-Authorization Boundaries

This review explicitly does **NOT** authorize:
- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no second M57 run
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no watch-row closure for either LibRTS scenario
