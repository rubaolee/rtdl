# Claude Task: Independent Review of Goal1726 Boundary Companion Evidence

Please perform a read-only independent Claude review of Goal1726 and the updated Goal1723 consolidation.

## Context

Goal1723 previously found three boundary rows in the 16 real Goal1660 comparable artifact pairs:

- `facility_knn_assignment/optix`: timing row used `--skip-validation`.
- `robot_collision_screening/optix`: timing row had `validated=false`.
- `polygon_set_jaccard/optix`: timing row used diagnostic-only Jaccard chunking.

Goal1726 adds companion pod evidence for those three rows without rewriting the original timing artifacts:

- Facility current/v1.0 validation companions both report `matches_oracle=true` and threshold count `80000`.
- Robot current/v1.0 validation companions both report `validated=true`, `matches_oracle=true`, collision count `3840`.
- Jaccard current/v1.0 public-safe chunk companions both report `status=pass`, `parity_vs_cpu=true`, `chunk_policy.public_safe=true`, `chunk_copies=1024`.

## Files To Review

- `docs/reports/goal1726_goal1660_boundary_companion_evidence_2026-05-12.md`
- `tests/goal1726_goal1660_boundary_companion_evidence_test.py`
- `docs/reports/goal1723_goal1660_comparable_artifact_consolidation_2026-05-12.json`
- `docs/reports/goal1723_goal1660_comparable_artifact_consolidation_2026-05-12.md`
- `tests/goal1723_goal1660_comparable_artifact_consolidation_test.py`
- The six companion JSON artifacts named `docs/reports/goal1726_*_optix.json`

## Required Checks

1. Confirm Goal1723 now reports 16 artifact pairs, 16 clean parity-or-companion rows, 3 companion resolutions, and 0 unresolved boundaries.
2. Confirm the original timing-artifact boundary notes remain visible and are not erased.
3. Confirm each companion artifact pair supports the claimed resolution.
4. Confirm no release, tag, or public speedup claim is authorized.

## Validation Command

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1726_goal1660_boundary_companion_evidence_test tests.goal1723_goal1660_comparable_artifact_consolidation_test tests.goal1722_goal1660_manifest_reality_correction_test tests.goal1660_v1_6_11_vs_v1_0_perf_matrix_test tests.goal1718_goal1660_cross_version_pod_attempt_test tests.goal1720_goal1660_v1_0_optix_adapter_completion_test -q
```

## Output

Write the review to:

`docs/reviews/goal1727_claude_review_goal1726_boundary_companion_evidence_2026-05-12.md`

Use verdicts from `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`. State explicitly that this is an independent Claude review distinct from Codex and Gemini.
