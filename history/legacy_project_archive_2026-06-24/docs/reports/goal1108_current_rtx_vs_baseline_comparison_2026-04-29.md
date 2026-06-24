# Goal1108 Current RTX vs Same-Contract Baseline Comparison

Date: 2026-04-29

Valid: `true`

Goal1108 computes engineering comparison ratios between existing RTX artifacts and same-contract baselines. It does not authorize public RTX speedup claims because the current artifacts are cross-host, source commits differ, and public wording review remains required.

## Summary

| Metric | Value |
| --- | ---: |
| `row_count` | `2` |
| `rtx_ok_count` | `2` |
| `baseline_ok_count` | `3` |
| `public_speedup_claim_authorized_count` | `0` |

## Rows

| App | Path | RTX median (s) | Baseline | Baseline median (s) | Engineering ratio | Public claim? | Blockers |
| --- | --- | ---: | --- | ---: | ---: | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared_recentered` | 0.135054 | `cpu_oracle` | 8.996513 | 66.61x | `false` | cross_host_comparison_not_public_claim; public_wording_review_required; source_commit_mismatch_requires_rerun_for_public_claim |
| `facility_knn_assignment` | `coverage_threshold_prepared_recentered` | 0.135054 | `embree` | 29.806781 | 220.70x | `false` | cross_host_comparison_not_public_claim; public_wording_review_required; source_commit_mismatch_requires_rerun_for_public_claim |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | 0.230636 | `embree` | 53.465870 | 231.82x | `false` | cross_host_comparison_not_public_claim; public_wording_review_required; source_commit_mismatch_requires_rerun_for_public_claim |

## Boundary

Goal1108 computes engineering comparison ratios between existing RTX artifacts and same-contract baselines. It does not authorize public RTX speedup claims because the current artifacts are cross-host, source commits differ, and public wording review remains required.
