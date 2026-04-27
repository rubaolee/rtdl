# Goal1035 Local Baseline Scale Ramp

Date: 2026-04-26

This scale-ramp runner collects incremental local same-command health and timing evidence. It does not authorize speedup claims, and same-scale public comparisons still require review.

## Summary

- copies_list: `[20000]`
- timeout_sec: `180.0`
- rows: `12`
- status: `ok`

## Results

| App | Copies | Backend | Status | Elapsed (s) | Summary |
|---|---:|---|---|---:|---|
| `outlier_detection` | 20000 | `cpu` | `ok` | 0.365416 | `{'app': 'outlier_detection', 'backend': 'cpu', 'copies': 20000, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'outlier_count': 40000}` |
| `outlier_detection` | 20000 | `embree` | `ok` | 0.304603 | `{'app': 'outlier_detection', 'backend': 'embree', 'copies': 20000, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'outlier_count': 40000}` |
| `outlier_detection` | 20000 | `scipy` | `ok` | 1.045236 | `{'app': 'outlier_detection', 'backend': 'scipy', 'copies': 20000, 'matches_oracle': True, 'summary_mode': 'scipy_ckdtree_threshold_count', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'outlier_count': 40000}` |
| `dbscan_clustering` | 20000 | `cpu` | `ok` | 0.318811 | `{'app': 'dbscan_clustering', 'backend': 'cpu', 'copies': 20000, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'core_count': 140000}` |
| `dbscan_clustering` | 20000 | `embree` | `ok` | 0.311104 | `{'app': 'dbscan_clustering', 'backend': 'embree', 'copies': 20000, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'core_count': 140000}` |
| `dbscan_clustering` | 20000 | `scipy` | `ok` | 0.943645 | `{'app': 'dbscan_clustering', 'backend': 'scipy', 'copies': 20000, 'matches_oracle': True, 'summary_mode': 'scipy_ckdtree_threshold_count', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'core_count': 140000}` |
| `service_coverage_gaps` | 20000 | `cpu` | `ok` | 2.141152 | `{'app': 'service_coverage_gaps', 'backend': 'cpu', 'copies': 20000, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'covered_household_count': 60000}` |
| `service_coverage_gaps` | 20000 | `embree` | `ok` | 0.362919 | `{'app': 'service_coverage_gaps', 'backend': 'embree', 'copies': 20000, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'covered_household_count': 60000}` |
| `service_coverage_gaps` | 20000 | `scipy` | `ok` | 0.767360 | `{'app': 'service_coverage_gaps', 'backend': 'scipy', 'copies': 20000, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'covered_household_count': 60000}` |
| `event_hotspot_screening` | 20000 | `cpu` | `ok` | 5.895585 | `{'app': 'event_hotspot_screening', 'backend': 'cpu', 'copies': 20000, 'native_continuation_active': False, 'native_continuation_backend': 'none'}` |
| `event_hotspot_screening` | 20000 | `embree` | `ok` | 0.552202 | `{'app': 'event_hotspot_screening', 'backend': 'embree', 'copies': 20000, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count'}` |
| `event_hotspot_screening` | 20000 | `scipy` | `ok` | 1.292635 | `{'app': 'event_hotspot_screening', 'backend': 'scipy', 'copies': 20000, 'native_continuation_active': False, 'native_continuation_backend': 'none'}` |

## Boundary

This scale-ramp runner collects incremental local same-command health and timing evidence. It does not authorize speedup claims, and same-scale public comparisons still require review.

