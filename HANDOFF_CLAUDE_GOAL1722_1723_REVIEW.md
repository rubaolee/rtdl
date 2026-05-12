# Claude Task: Independent Review of Goal1722/Goal1723

Please perform a read-only independent Claude review of the Goal1660 manifest correction and artifact consolidation after the Goal1718/Goal1720 pod findings.

## Context

- Goal1718 showed the original Goal1660 v1.6.11-vs-v1.0 manifest over-planned v1.0 rows: current ran 28/28, but v1.0 only ran 4/28 with the original command shape because many legacy v1.0 scripts rejected `--backend`.
- Goal1720 adapted v1.0 OptiX-only rows by dropping unsupported `--backend optix`, producing 12 more v1.0 OptiX artifacts.
- Goal1722 updated the manifest generator and tests so unsupported v1.0 Embree rows are current-only instead of fake planned baselines.
- Goal1723 consolidated the 16 real comparable artifact pairs and documented boundary rows without computing speedups.

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
- Supporting: `docs/reports/goal1718_goal1660_cross_version_pod_attempt_2026-05-12.md`, `docs/reports/goal1720_goal1660_v1_0_optix_adapter_completion_2026-05-12.md`

## Required Checks

1. Confirm the manifest has `planned_row_count=16` and `blocked_or_excluded_row_count=20`.
2. Confirm 12 v1.0 OptiX rows use `legacy_optix_only_without_backend_selector`, keep `compare_v1_0=True`, and do not include `--backend`.
3. Confirm 12 unsupported v1.0 Embree rows use `current_only_v1_0_missing_engine_selector`, keep `compare_current=True`, and keep `compare_v1_0=False`.
4. Confirm Goal1723 records 16 artifact pairs, 15 clean parity-flag rows, and three boundary rows: polygon-set Jaccard diagnostic chunk config, facility skip-validation payload, and robot collision `validated=false`.
5. Confirm no release, tag, or public speedup wording is authorized.

## Validation Command

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1723_goal1660_comparable_artifact_consolidation_test tests.goal1722_goal1660_manifest_reality_correction_test tests.goal1660_v1_6_11_vs_v1_0_perf_matrix_test tests.goal1718_goal1660_cross_version_pod_attempt_test tests.goal1720_goal1660_v1_0_optix_adapter_completion_test -q
```

## Output

Write the review to:

`docs/reviews/goal1725_claude_review_goal1722_1723_goal1660_manifest_and_artifacts_2026-05-12.md`

Use verdicts from `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`. State explicitly that this is an independent Claude review distinct from Codex and Gemini.
