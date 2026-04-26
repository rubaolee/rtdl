# Goal1031 Local Baseline Smoke Runner

Date: 2026-04-26

Smoke mode intentionally scales --copies down and only checks local command health. It is not same-scale baseline evidence and does not authorize speedup claims.

## Summary

- mode: `smoke`
- entries: `2`
- failed entries: `0`
- optional dependency gap entries: `2`
- status: `ok_with_optional_dependency_gaps`

## Results

| App | Status | Commands | Failed | Optional gaps | Elapsed total (s) |
|---|---|---:|---:|---:|---:|
| `service_coverage_gaps` | `ok_with_optional_dependency_gaps` | 3 | 0 | 1 | 0.475356 |
| `event_hotspot_screening` | `ok_with_optional_dependency_gaps` | 3 | 0 | 1 | 0.333774 |

## Command Details

### `service_coverage_gaps`

- status: `ok`, elapsed: `0.248556s`, summary: `{'json_parse_status': 'ok', 'app': 'service_coverage_gaps', 'backend': 'cpu', 'copies': 50, 'household_count': 200, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'rt_core_accelerated': False, 'covered_household_count': 150}`
- status: `ok`, elapsed: `0.119007s`, summary: `{'json_parse_status': 'ok', 'app': 'service_coverage_gaps', 'backend': 'embree', 'copies': 50, 'household_count': 200, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'rt_core_accelerated': False, 'covered_household_count': 150}`
- status: `optional_dependency_unavailable`, elapsed: `0.107793s`, summary: `{'json_parse_status': 'not_json'}`

### `event_hotspot_screening`

- status: `ok`, elapsed: `0.114430s`, summary: `{'json_parse_status': 'ok', 'app': 'event_hotspot_screening', 'backend': 'cpu', 'copies': 50, 'event_count': 300, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'rt_core_accelerated': False}`
- status: `ok`, elapsed: `0.115422s`, summary: `{'json_parse_status': 'ok', 'app': 'event_hotspot_screening', 'backend': 'embree', 'copies': 50, 'event_count': 300, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'rt_core_accelerated': False}`
- status: `optional_dependency_unavailable`, elapsed: `0.103923s`, summary: `{'json_parse_status': 'not_json'}`

