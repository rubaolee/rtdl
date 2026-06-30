# Goal1072 Claude Review

Date: 2026-04-28
Reviewer: Claude Sonnet 4.6 (claude-sonnet-4-6)
Verdict: **ACCEPT**

## Scope

Review of Goal1072 as a superseding pod-batch plan that follows from Goal1071 scale-up evidence.
Files reviewed: `scripts/goal1072_post_scale_up_rtx_pod_batch.py`,
`tests/goal1072_post_scale_up_rtx_pod_batch_test.py`,
`docs/reports/goal1072_post_scale_up_rtx_pod_batch_2026-04-28.md`,
`docs/reports/goal1071_rtx_pod_scale_up_result_2026-04-28.md`,
`docs/handoff/REFRESH_LOCAL_2026-04-13.md`.

## Findings

### 1. Goal1071 scale rows correctly adopted — PASS

- Facility timing row: `--copies 2500000`, `source_goal: "Goal1071"`, `source_evidence` points to
  `goal1071_scale_up_probes/facility_coverage_threshold_2_5m_timing.json`.
  This matches the 2.5M-copy probe that produced 0.111742 s median (floor passed) in Goal1071.
- Robot timing row: `--pose-count 36000000`, `source_goal: "Goal1071"`, `source_evidence` points to
  `goal1071_scale_up_probes/robot_prepared_pose_flags_36m_timing.json`.
  This matches the 36M-pose probe that produced 0.102610 s median (floor passed) in Goal1071.
  The 32M near-miss (0.098737 s) was correctly not used.

### 2. Barnes-Hut excluded for benchmark-contract redesign — PASS

- `excluded_rows[0].app == "barnes_hut_force_app"`, `exclusion_status: "blocked_contract_reframe_required"`.
- Exclusion reason correctly cites the four one-level quadtree nodes and the 0.004204 s median from the 1M-body Goal1068 run.
- `next_move` field defers cloud time until a richer traversal contract is designed.
- The generated shell runner contains no `barnes_hut_node_coverage` commands (test confirms).

### 3. Validation/timing separation preserved — PASS

Each of the two apps carries exactly two rows:

| Phase | `--skip-validation` | `requires_validation` | `timing_floor_sec` |
| --- | --- | --- | --- |
| `correctness_validation` | absent (`False`) | `True` | `None` |
| `large_timing_repeat` | present (`True`) | `False` | `0.100` |

The `valid` field enforces this invariant programmatically: it checks that no validation row
carries `--skip-validation` and that no timing row lacks a floor. Both checks pass.
Validation rows source correctness evidence from Goal1068 at small scale, which is appropriate —
oracle parity does not require 2.5M copies.

### 4. Public RTX speedup claims not authorized — PASS

- `boundary` field: "does not authorize public RTX speedup claims" (exact string required by test).
- Preconditions: "Treat this as evidence collection only; no public wording changes are authorized."
- Each manifest row calls `rt.rtx_public_wording_status(app)` and records the current status
  without modifying it.
- Shell runner emits no wording-promotion commands.

### 5. Supersession linkage correct — PASS

`supersedes` lists both `goal1068_next_rtx_pod_efficiency_batch_2026-04-28.json` and
`goal1070_goal1068_artifact_intake_after_pod_2026-04-28.json`, which are the two artifacts
that documented the original failed-floor batch and its intake.

### 6. Test coverage adequate — PASS

Three test methods cover:
- Manifest structure and `valid == True` (all summary counts, excluded app, boundary strings).
- Per-row validation/timing policy (skip-validation flag, floor value, source_goal, scale values,
  source_evidence path prefix).
- CLI end-to-end: JSON, markdown, and shell outputs; `"valid": true` in stdout; absence of
  `barnes_hut_node_coverage` in runner.

### 7. Shell runner safety — PASS

Runner guards on `RTDL_SOURCE_COMMIT` (exits 2 if empty), runs `nvidia-smi` for environment
record, and emits a copy-back reminder before exit. This is consistent with claim-grade
artifact collection discipline.

## Issues

None blocking. One minor observation: the `valid` boolean is checked by the test as a
field read from the manifest dict, which is correct, but a downstream intake script should
independently re-verify the structural invariants rather than trust the cached `valid` flag
— consistent with how Goal1070 operated on Goal1068 outputs. This is a note for the intake
author, not a defect in Goal1072 itself.

## Verdict

**ACCEPT**

Goal1072 correctly supersedes the Goal1068 pod batch. It adopts the exact Goal1071 scale-up
rows (facility 2.5M, robot 36M), excludes Barnes-Hut with a clear contract-redesign rationale,
enforces validation/timing separation at both the manifest and test levels, and carries explicit
boundary language prohibiting public RTX speedup claims. No structural defects found.
