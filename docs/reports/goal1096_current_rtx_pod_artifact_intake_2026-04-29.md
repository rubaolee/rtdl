# Goal1096 Current RTX Pod Artifact Intake

Date: 2026-04-29

Overall status: `ready_for_2ai_review_not_public_claim`

This intake checks copied Goal1084 and Goal1093 artifacts only. It does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.

## Summary

- expected artifacts: `3`
- present artifacts: `3`
- missing artifacts: `0`
- blocked rows: `0`
- timing below floor: `0`
- public speedup claims authorized: `0`

## Rows

| App | Path | Phase | Artifact | Review status | RTX phase | Reason |
| --- | --- | --- | --- | --- | ---: | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared_recentered` | `same_scale_validation_and_timing` | `present` | `validation_and_timing_passed` | `0.135054` | facility artifact proves oracle parity and timing floor |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `depth8_contract_validation` | `present` | `validation_passed` | `0.007582` | Barnes-Hut artifact proves depth-8 oracle parity |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `depth8_20m_timing_repeat` | `present` | `timing_floor_passed` | `0.230636` | Barnes-Hut timing artifact passes timing floor |

## Boundary

This intake checks copied Goal1084 and Goal1093 artifacts only. It does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.
