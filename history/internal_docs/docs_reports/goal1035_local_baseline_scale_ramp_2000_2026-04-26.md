# Goal1035 Local Baseline Scale Ramp

Date: 2026-04-26

This scale-ramp runner collects incremental local same-command health and timing evidence. It does not authorize speedup claims, and same-scale public comparisons still require review.

## Summary

- copies_list: `[2000]`
- timeout_sec: `180.0`
- rows: `12`
- status: `ok`

## Results

| App | Copies | Backend | Status | Elapsed (s) | Summary |
|---|---:|---|---|---:|---|
| `outlier_detection` | 2000 | `cpu` | `ok` | 15.258467 | `{'app': 'outlier_detection', 'backend': 'cpu', 'copies': 2000, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'outlier_count': 4000}` |
| `outlier_detection` | 2000 | `embree` | `ok` | 15.267537 | `{'app': 'outlier_detection', 'backend': 'embree', 'copies': 2000, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'outlier_count': 4000}` |
| `outlier_detection` | 2000 | `scipy` | `ok` | 16.228283 | `{'app': 'outlier_detection', 'backend': 'scipy', 'copies': 2000, 'matches_oracle': True, 'summary_mode': 'scipy_ckdtree_threshold_count', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'outlier_count': 4000}` |
| `dbscan_clustering` | 2000 | `cpu` | `ok` | 0.172229 | `{'app': 'dbscan_clustering', 'backend': 'cpu', 'copies': 2000, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'core_count': 14000}` |
| `dbscan_clustering` | 2000 | `embree` | `ok` | 0.136282 | `{'app': 'dbscan_clustering', 'backend': 'embree', 'copies': 2000, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'core_count': 14000}` |
| `dbscan_clustering` | 2000 | `scipy` | `ok` | 0.482447 | `{'app': 'dbscan_clustering', 'backend': 'scipy', 'copies': 2000, 'matches_oracle': True, 'summary_mode': 'scipy_ckdtree_threshold_count', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'core_count': 14000}` |
| `service_coverage_gaps` | 2000 | `cpu` | `ok` | 0.197649 | `{'app': 'service_coverage_gaps', 'backend': 'cpu', 'copies': 2000, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'covered_household_count': 6000}` |
| `service_coverage_gaps` | 2000 | `embree` | `ok` | 0.163576 | `{'app': 'service_coverage_gaps', 'backend': 'embree', 'copies': 2000, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'covered_household_count': 6000}` |
| `service_coverage_gaps` | 2000 | `scipy` | `ok` | 0.339601 | `{'app': 'service_coverage_gaps', 'backend': 'scipy', 'copies': 2000, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'covered_household_count': 6000}` |
| `event_hotspot_screening` | 2000 | `cpu` | `ok` | 0.283394 | `{'app': 'event_hotspot_screening', 'backend': 'cpu', 'copies': 2000, 'native_continuation_active': False, 'native_continuation_backend': 'none'}` |
| `event_hotspot_screening` | 2000 | `embree` | `ok` | 0.164967 | `{'app': 'event_hotspot_screening', 'backend': 'embree', 'copies': 2000, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count'}` |
| `event_hotspot_screening` | 2000 | `scipy` | `ok` | 0.396641 | `{'app': 'event_hotspot_screening', 'backend': 'scipy', 'copies': 2000, 'native_continuation_active': False, 'native_continuation_backend': 'none'}` |

## Boundary

This scale-ramp runner collects incremental local same-command health and timing evidence. It does not authorize speedup claims, and same-scale public comparisons still require review.

