# Gemini Task: Review Goal1722/Goal1723 Goal1660 Manifest and Artifact Consolidation

Please perform a read-only independent Gemini review of the Goal1660 follow-up work after the Goal1718/Goal1720 pod findings.

## Context

- Goal1718 proved the original Goal1660 manifest over-planned v1.0 rows: current v1.6.11 ran 28/28 planned rows, but tagged v1.0 only ran 4/28 with the original command shape because many legacy scripts rejected `--backend`.
- Goal1720 adapted the v1.0 OptiX-only rows by dropping unsupported `--backend optix`, producing 12 additional v1.0 OptiX artifacts.
- Goal1722 updates `scripts/goal1660_v1_6_11_vs_v1_0_perf_matrix.py` so the manifest now records 16 real comparable rows and 12 current-only unsupported v1.0 Embree rows instead of fabricating decorative v1.0 Embree baselines.
- Goal1723 consolidates the 16 comparable artifact pairs without computing or publishing speedups.

## Files To Review

- `scripts/goal1660_v1_6_11_vs_v1_0_perf_matrix.py`
- `tests/goal1660_v1_6_11_vs_v1_0_perf_matrix_test.py`
- `docs/reports/goal1660_v1_6_11_vs_v1_0_perf_matrix_2026-05-10.json`
- `docs/reports/goal1660_v1_6_11_vs_v1_0_perf_matrix_2026-05-10.md`
- `docs/reports/goal1722_goal1660_manifest_reality_correction_after_v1_0_pod_adapter_2026-05-12.md`
- `tests/goal1722_goal1660_manifest_reality_correction_test.py`
- `docs/reports/goal1723_goal1660_comparable_artifact_consolidation_2026-05-12.json`
- `docs/reports/goal1723_goal1660_comparable_artifact_consolidation_2026-05-12.md`
- `tests/goal1723_goal1660_comparable_artifact_consolidation_test.py`
- Supporting evidence: `docs/reports/goal1718_goal1660_cross_version_pod_attempt_2026-05-12.md`, `docs/reports/goal1720_goal1660_v1_0_optix_adapter_completion_2026-05-12.md`

## Required Checks

1. Confirm the manifest now has `planned_row_count=16` and `blocked_or_excluded_row_count=20`.
2. Confirm the 12 legacy OptiX-only v1.0 rows have `v1_0_command_shape=legacy_optix_only_without_backend_selector` and their v1.0 commands do not include `--backend`.
3. Confirm the 12 unsupported v1.0 Embree rows are `current_only_v1_0_missing_engine_selector`, with `compare_current=True` and `compare_v1_0=False`.
4. Confirm Goal1723 counts 16 artifact pairs and identifies the boundary rows: polygon-set Jaccard diagnostic chunk config, facility skip-validation payload, and robot collision `validated=false`.
5. Confirm no speedup/release/tag claim is authorized.

## Validation Command

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1723_goal1660_comparable_artifact_consolidation_test tests.goal1722_goal1660_manifest_reality_correction_test tests.goal1660_v1_6_11_vs_v1_0_perf_matrix_test tests.goal1718_goal1660_cross_version_pod_attempt_test tests.goal1720_goal1660_v1_0_optix_adapter_completion_test -q
```

## Output

Write the review to:

`docs/reviews/goal1724_gemini_review_goal1722_1723_goal1660_manifest_and_artifacts_2026-05-12.md`

Use verdicts from `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`. State explicitly that this is an independent Gemini/Antigravity review distinct from Codex.
