# Goal1068 Claude Review

Date: 2026-04-28
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **PASS**

---

## Scope

Review of Goal1068 next RTX pod efficiency batch. Files examined:

- `scripts/goal1068_next_rtx_pod_efficiency_batch.py`
- `tests/goal1068_next_rtx_pod_efficiency_batch_test.py`
- `docs/reports/goal1068_next_rtx_pod_efficiency_batch_2026-04-28.json`
- `docs/reports/goal1068_next_rtx_pod_efficiency_batch_2026-04-28.md`
- `scripts/goal1068_next_rtx_pod_efficiency_batch_runner.sh`
- `docs/reports/goal1067_two_ai_consensus_2026-04-28.md`
- `docs/reports/goal1067_scale_contract_repair_audit_2026-04-28.json` (gate artifact)

---

## Criteria Assessment

### 1. Correctly combines Goal1062 facility/robot rows with reviewed Goal1067 Barnes-Hut 1M candidate

**PASS.**

The manifest contains exactly 6 rows across 3 apps:

- `facility_knn_assignment` (2 rows, source `Goal1062`)
- `robot_collision_screening` (2 rows, source `Goal1062`)
- `barnes_hut_force_app` (2 rows, source `Goal1067`)

The function `_goal1067_barnes_ready()` reads the Goal1067 audit JSON and requires all of:
- `payload["valid"] == True` — confirmed present in Goal1067 JSON
- `barnes["decision"] == "pod_candidate_after_review"` — confirmed
- `barnes["recommended_cloud_scale"]["body_count"] == 1_000_000` — confirmed

The overall `valid` field in the generated manifest is gated on `barnes_ready` being true. The generated JSON reports `"goal1067_barnes_ready": true` and `"valid": true`, consistent with the Goal1067 two-AI consensus (`ACCEPTED`, pod candidate at 1M bodies).

The Barnes-Hut 1M timing row uses `--body-count 1000000` as recommended. The Barnes-Hut validation row uses `--body-count 200000`, matching Goal1067's prescription to "run one smaller validated RTX pass before large timing repeats."

### 2. Keeps validation rows without --skip-validation

**PASS.**

All three `correctness_validation` rows have `"contains_skip_validation": false` in the generated JSON. The `valid` computation checks `not validation_skip` where `validation_skip` is the list of validation-phase rows whose commands include `--skip-validation`. That list is empty. The check is structural (scanning the actual command list), not a separate declared flag, so it cannot drift.

### 3. Gives timing rows a 0.100s floor

**PASS.**

All three `large_timing_repeat` rows have `"timing_floor_sec": 0.1` in the generated JSON. The `valid` computation checks both `not timing_without_floor` and `all(row["timing_floor_sec"] == 0.100 for row in timing_rows)`. Both conditions are satisfied. No timing row omits or undercuts the 100 ms floor.

### 4. Preserves no-cloud/no-public-speedup/no-release boundaries

**PASS.**

The `boundary` field reads: "Goal1068 prepares a larger one-pod evidence batch for facility, robot, and Barnes-Hut. It does not run cloud, does not create resources, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims."

This language covers all four required prohibitions: no cloud, no public speedup, no release, and no wording change. The `global_preconditions` list additionally states "Treat this as evidence collection only; no public wording changes are authorized by this runner." The runner script header also states the cloud/speedup-claim boundary. Both `current_public_wording_status` fields for facility and robot rows read `public_wording_blocked`; Barnes-Hut reads `public_wording_not_reviewed`. Neither is promoted.

### 5. Adequate tests

**PASS.**

Three test methods provide good coverage of the key invariants:

- `test_batch_combines_goal1062_and_reviewed_barnes_candidate` — verifies `valid=True`, `goal1067_barnes_ready=True`, counts (6 rows, 3 apps, 3 validation, 3 timing), empty `validation_rows_with_skip_validation`, empty `timing_rows_without_floor`, and both boundary clauses ("does not run cloud", "does not authorize public RTX speedup claims").
- `test_rows_have_correct_validation_and_timing_policy` — iterates all three apps, checks that validation rows have no `--skip-validation` and timing rows do have it plus `timing_floor_sec == 0.100`. Also checks Barnes-Hut body counts (200000 in validation, 1000000 in timing) and `source_goal == "Goal1067"` for the timing row.
- `test_cli_writes_manifest_markdown_and_runner` — end-to-end subprocess test writing to a temp directory; verifies `"valid": true` in stdout, `row_count == 6` in the JSON, key strings in the markdown, and `RTDL_SOURCE_COMMIT`/`nvidia-smi`/`Goal1068 complete` in the shell runner.

One minor gap: no test explicitly checks that facility and robot rows carry `source_goal == "Goal1062"`. This is non-blocking because the correctness of those rows is structurally enforced by the hardcoded row definitions, and the app-level count check (3 apps) would catch a source-goal substitution that changed the row set.

---

## Notes

- `_goal1067_barnes_ready()` will raise on a missing or malformed Goal1067 artifact rather than returning `valid: false`. Fail-loud is the appropriate behavior here given this is a gating precondition.
- The runner script enforces `set -euo pipefail` and hard-fails if `RTDL_SOURCE_COMMIT` is empty, which correctly prevents collecting uncredited artifacts.
- The validation run for each app precedes its large timing run in the runner ordering, which is the correct sequencing.
- No Hausdorff rows are included; this is correct per Goal1067 which blocked Hausdorff with `decision: blocked_scale_contract_not_repaired`.

---

## Verdict

**PASS.** All five review criteria are satisfied. The batch correctly gates on the Goal1067 two-AI consensus, keeps all validation rows clean of `--skip-validation`, enforces the 0.100 s timing floor on all timing rows, preserves all no-cloud/no-public-speedup/no-release boundaries, and has three test methods with adequate structural coverage.
