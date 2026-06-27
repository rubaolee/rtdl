# Goal1170 External Review

Date: 2026-04-30
Reviewer: Gemini CLI

## Verdict

**VERDICT: ACCEPT**

The Goal1170 implementation correctly and conservatively implements the pre-pod requirements defined in Goal1169.

## Verification Notes

- **Manifest Shape**: `scripts/goal1170_clean_source_rtx_batch_manifest.py` correctly defines 8 rows: 6 for apps where public wording is not yet reviewed and 2 clean-source replacements for ANN and robot (public wording reviewed).
- **Source Integrity**: 
    - The runner (`scripts/goal1170_clean_source_rtx_batch_runner.sh`) refuses to run if `git status --short` is non-empty.
    - The intake (`scripts/goal1170_clean_source_rtx_batch_intake.py`) rejects artifacts with "local-dirty" in the source commit.
- **Preflight Rigor**: `scripts/goal1171_clean_source_rtx_pod_preflight.py` checks for:
    - Manifest row count (8).
    - Runner dirty-tree refusal code.
    - Source cleanliness.
    - NVIDIA/CUDA/NVCC/OptiX availability.
    - GEOS library and pkg-config readiness.
- **Validation Policy**: `--skip-validation` is restricted to the two large-timing replacement rows (`ann_candidate_large_timing_replacement` and `robot_pose_count_large_timing_replacement`).
- **Runbook Flow**: `scripts/goal1172_clean_source_rtx_pod_runbook.py` defines a strict `git clone` -> `build` -> `preflight` -> `batch` sequence, ensuring no dirty local source is used.
- **Batch Efficiency**: The runner script executes all manifest rows in a single session, avoiding redundant pod overhead.
- **Boundary Enforcement**: All artifacts and scripts explicitly state they do not authorize public speedup wording by themselves, maintaining proper engineering/marketing boundaries.

## Observed Evidence

- Tests passed: `tests.goal1170_clean_source_rtx_batch_manifest_test`, `tests.goal1171_clean_source_rtx_pod_preflight_test`, `tests.goal1172_clean_source_rtx_pod_runbook_test`.
- Source review of all `scripts/goal117*` and `scripts/goal1169` files.
