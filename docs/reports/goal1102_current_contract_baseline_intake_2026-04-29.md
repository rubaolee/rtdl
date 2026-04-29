# Goal1102 Current-Contract Baseline Intake

Date: 2026-04-29

Overall status: `waiting_for_baseline_artifacts`

Artifact set complete: `false`

Valid: `true`

Valid meaning: The intake schema and no-claim guard are structurally valid. Use artifact_set_complete and overall_status to determine whether baseline artifacts are actually present and ready for review.

Goal1102 intakes current-contract non-OptiX baseline artifacts only. It does not authorize public RTX speedup claims. Even a fully OK intake still requires 2+ AI review and a separate public wording gate.

## Summary

| Metric | Value |
| --- | ---: |
| `row_count` | `4` |
| `ok_count` | `3` |
| `missing_count` | `0` |
| `blocked_count` | `1` |
| `public_speedup_claim_authorized_count` | `0` |

## Rows

| Name | Status | Native query median (s) | Issues |
| --- | --- | ---: | --- |
| `facility_cpu_oracle` | `ok` | 8.996513 |  |
| `facility_embree` | `ok` | 29.806781 |  |
| `barnes_hut_validation_embree` | `ok` | 0.010342 |  |
| `barnes_hut_timing_embree` | `blocked` | 53.904498 | radius mismatch |

## Boundary

Goal1102 intakes current-contract non-OptiX baseline artifacts only. It does not authorize public RTX speedup claims. Even a fully OK intake still requires 2+ AI review and a separate public wording gate.
