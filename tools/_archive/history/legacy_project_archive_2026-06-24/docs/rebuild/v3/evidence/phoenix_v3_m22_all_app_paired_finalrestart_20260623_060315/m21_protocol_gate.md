# Phoenix V3 M21 All-App Protocol Gate Result

Status: `protocol_fail_invalid_or_out_of_scope`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## Documented Values

| Metric | Value |
| --- | ---: |
| Overall geomean V3 vs V2.14 | 1.049x |
| Set-A geomean V3 vs V2.14 | 1.013x |
| Set-A apps over 1.05x | 2 |
| Set-B geomean V3 vs V2.14 | 1.210x |
| Same-metric rows | 51 |

## Protocol Failures

| Bar | Actual | Threshold |
| --- | ---: | ---: |
| `barnes_hut_app_geomean_floor` | 0.831x | 0.900x |
| `new_app_level_severe_regression_floor` | 0.831x | 0.900x |

## Scope / Correctness Failures

```json
{
  "correctness_failures": [
    {
      "failed": 1,
      "gate": "suite_status",
      "reason": "failed_rows",
      "suite": "current_goal2636_stress"
    },
    {
      "failed": 2,
      "gate": "suite_status",
      "reason": "failed_rows",
      "suite": "v2_14_goal2626_large"
    },
    {
      "failed": 2,
      "gate": "suite_status",
      "reason": "failed_rows",
      "suite": "v2_14_goal2636_stress"
    }
  ],
  "scope_failures": []
}
```

## Watch Alerts

```json
[
  {
    "actual": 0.8029638936724112,
    "policy": "flag and report without rationalization; do not silently treat as success",
    "row_id": "goal2626_large|librts_spatial_index|aabb_index_all_count_only|optix|librts_optix_aabb_index",
    "threshold": 0.95,
    "watch_row": "librts_optix_aabb_index_watch_row"
  }
]
```

## Interpretation

run is invalid/out-of-scope for performance claims
