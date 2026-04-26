# Goal1031 Local Baseline Smoke Runner

Date: 2026-04-26

Smoke mode intentionally scales --copies down and only checks local command health. It is not same-scale baseline evidence and does not authorize speedup claims.

## Summary

- mode: `smoke`
- entries: `4`
- failed entries: `0`
- optional dependency gap entries: `2`
- status: `ok_with_optional_dependency_gaps`

## Results

| App | Status | Commands | Failed | Optional gaps | Elapsed total (s) |
|---|---|---:|---:|---:|---:|
| `outlier_detection` | `ok` | 3 | 0 | 0 | 0.471403 |
| `dbscan_clustering` | `ok` | 3 | 0 | 0 | 0.341099 |
| `service_coverage_gaps` | `ok_with_optional_dependency_gaps` | 3 | 0 | 1 | 0.401894 |
| `event_hotspot_screening` | `ok_with_optional_dependency_gaps` | 3 | 0 | 1 | 0.367001 |

## Command Details

### `outlier_detection`

- status: `ok`, elapsed: `0.203658s`, summary: `{'json_parse_status': 'ok', 'app': 'outlier_detection', 'backend': 'cpu', 'copies': 50, 'point_count': 400, 'matches_oracle': True, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'output_mode': 'density_count', 'summary_mode': 'scalar_threshold_count_oracle', 'outlier_count': 100}`
- status: `ok`, elapsed: `0.138874s`, summary: `{'json_parse_status': 'ok', 'app': 'outlier_detection', 'backend': 'embree', 'copies': 50, 'point_count': 400, 'matches_oracle': True, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'output_mode': 'density_count', 'summary_mode': 'scalar_threshold_count_oracle', 'outlier_count': 100}`
- status: `ok`, elapsed: `0.128871s`, summary: `{'json_parse_status': 'ok', 'app': 'outlier_detection', 'backend': 'scipy', 'copies': 50, 'point_count': 400, 'matches_oracle': True, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'output_mode': 'density_count', 'summary_mode': 'scalar_threshold_count_oracle', 'outlier_count': 100}`

### `dbscan_clustering`

- status: `ok`, elapsed: `0.118042s`, summary: `{'json_parse_status': 'ok', 'app': 'dbscan_clustering', 'backend': 'cpu', 'copies': 50, 'point_count': 400, 'matches_oracle': True, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'output_mode': 'core_count', 'summary_mode': 'scalar_threshold_count_oracle', 'core_count': 350}`
- status: `ok`, elapsed: `0.115504s`, summary: `{'json_parse_status': 'ok', 'app': 'dbscan_clustering', 'backend': 'embree', 'copies': 50, 'point_count': 400, 'matches_oracle': True, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'output_mode': 'core_count', 'summary_mode': 'scalar_threshold_count_oracle', 'core_count': 350}`
- status: `ok`, elapsed: `0.107553s`, summary: `{'json_parse_status': 'ok', 'app': 'dbscan_clustering', 'backend': 'scipy', 'copies': 50, 'point_count': 400, 'matches_oracle': True, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'output_mode': 'core_count', 'summary_mode': 'scalar_threshold_count_oracle', 'core_count': 350}`

### `service_coverage_gaps`

- status: `ok`, elapsed: `0.128030s`, summary: `{'json_parse_status': 'ok', 'app': 'service_coverage_gaps', 'backend': 'cpu', 'copies': 50, 'household_count': 200, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'rt_core_accelerated': False, 'covered_household_count': 150}`
- status: `ok`, elapsed: `0.149721s`, summary: `{'json_parse_status': 'ok', 'app': 'service_coverage_gaps', 'backend': 'embree', 'copies': 50, 'household_count': 200, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'rt_core_accelerated': False, 'covered_household_count': 150}`
- status: `optional_dependency_unavailable`, elapsed: `0.124143s`, summary: `{'json_parse_status': 'not_json'}`

### `event_hotspot_screening`

- status: `ok`, elapsed: `0.128226s`, summary: `{'json_parse_status': 'ok', 'app': 'event_hotspot_screening', 'backend': 'cpu', 'copies': 50, 'event_count': 300, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'rt_core_accelerated': False}`
- status: `ok`, elapsed: `0.126388s`, summary: `{'json_parse_status': 'ok', 'app': 'event_hotspot_screening', 'backend': 'embree', 'copies': 50, 'event_count': 300, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'rt_core_accelerated': False}`
- status: `optional_dependency_unavailable`, elapsed: `0.112387s`, summary: `{'json_parse_status': 'not_json'}`

