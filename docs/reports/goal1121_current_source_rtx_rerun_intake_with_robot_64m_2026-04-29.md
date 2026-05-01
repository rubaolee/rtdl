# Goal1118 Current-Source RTX Rerun Intake

Date: 2026-04-29

Valid: `false`

Goal1118 intakes Goal1116 current-source RTX rerun artifacts. It does not run cloud, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.

## Summary

| Metric | Value |
| --- | ---: |
| `row_count` | `5` |
| `valid_row_count` | `5` |
| `missing_row_count` | `0` |
| `source_commits` | `['21fa036881bf9a0c806f69c15727d87b482ccfcf', '2ba7ae0']` |
| `same_source_commit` | `False` |
| `runner_log_exists` | `True` |
| `public_speedup_claim_authorized` | `False` |

## Rows

| App | Phase | Exists | Valid | Source commit | Median query sec | Findings |
| --- | --- | --- | --- | --- | ---: | --- |
| `facility_knn_assignment` | `same_scale_validation_and_timing` | `True` | `True` | `21fa036881bf9a0c806f69c15727d87b482ccfcf` | `0.111619` |  |
| `robot_collision_screening` | `correctness_validation` | `True` | `True` | `21fa036881bf9a0c806f69c15727d87b482ccfcf` | `0.006429` |  |
| `robot_collision_screening` | `large_timing_repeat` | `True` | `True` | `2ba7ae0` | `0.178698` |  |
| `barnes_hut_force_app` | `correctness_validation` | `True` | `True` | `21fa036881bf9a0c806f69c15727d87b482ccfcf` | `0.007977` |  |
| `barnes_hut_force_app` | `large_timing_repeat` | `True` | `True` | `21fa036881bf9a0c806f69c15727d87b482ccfcf` | `0.222256` |  |

## Boundary

Goal1118 intakes Goal1116 current-source RTX rerun artifacts. It does not run cloud, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.
