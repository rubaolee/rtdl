# Goal1031 Local Baseline Smoke Runner

Date: 2026-04-26

Smoke mode intentionally scales --copies down and only checks local command health. It is not same-scale baseline evidence and does not authorize speedup claims.

## Summary

- mode: `smoke`
- entries: `4`
- failed entries: `0`
- optional dependency gap entries: `0`
- status: `ok`

## Results

| App | Status | Commands | Failed | Optional gaps | Elapsed total (s) |
|---|---|---:|---:|---:|---:|
| `outlier_detection` | `ok` | 3 | 0 | 0 | 7.126844 |
| `dbscan_clustering` | `ok` | 3 | 0 | 0 | 0.470639 |
| `service_coverage_gaps` | `ok` | 3 | 0 | 0 | 0.488034 |
| `event_hotspot_screening` | `ok` | 3 | 0 | 0 | 0.564421 |

## Command Details

### `outlier_detection`

- status: `ok`, elapsed: `0.208268s`, summary: `{'json_parse_status': 'ok', 'app': 'outlier_detection', 'backend': 'cpu', 'copies': 50, 'point_count': 400, 'matches_oracle': True, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'output_mode': 'density_count', 'summary_mode': 'scalar_threshold_count_oracle', 'outlier_count': 100}`
- status: `ok`, elapsed: `0.125953s`, summary: `{'json_parse_status': 'ok', 'app': 'outlier_detection', 'backend': 'embree', 'copies': 50, 'point_count': 400, 'matches_oracle': True, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'output_mode': 'density_count', 'summary_mode': 'scalar_threshold_count_oracle', 'outlier_count': 100}`
- status: `ok`, elapsed: `6.792622s`, summary: `{'json_parse_status': 'ok', 'app': 'outlier_detection', 'backend': 'scipy', 'copies': 50, 'point_count': 400, 'matches_oracle': True, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'output_mode': 'density_count', 'summary_mode': 'scipy_ckdtree_threshold_count', 'outlier_count': 100}`

### `dbscan_clustering`

- status: `ok`, elapsed: `0.106130s`, summary: `{'json_parse_status': 'ok', 'app': 'dbscan_clustering', 'backend': 'cpu', 'copies': 50, 'point_count': 400, 'matches_oracle': True, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'output_mode': 'core_count', 'summary_mode': 'scalar_threshold_count_oracle', 'core_count': 350}`
- status: `ok`, elapsed: `0.107139s`, summary: `{'json_parse_status': 'ok', 'app': 'dbscan_clustering', 'backend': 'embree', 'copies': 50, 'point_count': 400, 'matches_oracle': True, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'output_mode': 'core_count', 'summary_mode': 'scalar_threshold_count_oracle', 'core_count': 350}`
- status: `ok`, elapsed: `0.257370s`, summary: `{'json_parse_status': 'ok', 'app': 'dbscan_clustering', 'backend': 'scipy', 'copies': 50, 'point_count': 400, 'matches_oracle': True, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'output_mode': 'core_count', 'summary_mode': 'scipy_ckdtree_threshold_count', 'core_count': 350}`

### `service_coverage_gaps`

- status: `ok`, elapsed: `0.117818s`, summary: `{'json_parse_status': 'ok', 'app': 'service_coverage_gaps', 'backend': 'cpu', 'copies': 50, 'household_count': 200, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'rt_core_accelerated': False, 'covered_household_count': 150}`
- status: `ok`, elapsed: `0.116058s`, summary: `{'json_parse_status': 'ok', 'app': 'service_coverage_gaps', 'backend': 'embree', 'copies': 50, 'household_count': 200, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'rt_core_accelerated': False, 'covered_household_count': 150}`
- status: `ok`, elapsed: `0.254158s`, summary: `{'json_parse_status': 'ok', 'app': 'service_coverage_gaps', 'backend': 'scipy', 'copies': 50, 'household_count': 200, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'rt_core_accelerated': False, 'covered_household_count': 150}`

### `event_hotspot_screening`

- status: `ok`, elapsed: `0.140546s`, summary: `{'json_parse_status': 'ok', 'app': 'event_hotspot_screening', 'backend': 'cpu', 'copies': 50, 'event_count': 300, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'rt_core_accelerated': False}`
- status: `ok`, elapsed: `0.168072s`, summary: `{'json_parse_status': 'ok', 'app': 'event_hotspot_screening', 'backend': 'embree', 'copies': 50, 'event_count': 300, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'rt_core_accelerated': False}`
- status: `ok`, elapsed: `0.255804s`, summary: `{'json_parse_status': 'ok', 'app': 'event_hotspot_screening', 'backend': 'scipy', 'copies': 50, 'event_count': 300, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'rt_core_accelerated': False}`

