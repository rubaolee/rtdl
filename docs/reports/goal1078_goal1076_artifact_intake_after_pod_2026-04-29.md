# Goal1078 Goal1076 Barnes-Hut Rich Artifact Intake

Date: 2026-04-28

Overall status: `timing_floor_not_met`

This intake checks copied Goal1076 artifacts only. It does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.

## Summary

- expected artifacts: `2`
- present artifacts: `2`
- missing artifacts: `0`
- validation passed: `1`
- timing floor passed: `0`
- timing below floor: `1`
- blocked rows: `0`
- public speedup claims authorized: `0`

## Rows

| App | Path | Phase | Artifact | Review status | RTX phase | Reason |
| --- | --- | --- | --- | --- | ---: | --- |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `correctness_validation` | `present` | `validation_passed` | `` | Barnes-Hut rich validation artifact proves optix oracle parity |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `large_timing_repeat` | `present` | `timing_below_floor` | `0.005456` | RTX phase 0.005456s is below 0.100s floor |

## Boundary

This intake checks copied Goal1076 artifacts only. It does not run cloud, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.
