# Goal1035 Local Baseline Scale Ramp

Date: 2026-04-26

This scale-ramp runner collects incremental local same-command health and timing evidence. It does not authorize speedup claims, and same-scale public comparisons still require review.

## Summary

- copies_list: `[50, 500]`
- timeout_sec: `180.0`
- rows: `24`
- status: `ok`

## Results

| App | Copies | Backend | Status | Elapsed (s) | Summary |
|---|---:|---|---|---:|---|
| `outlier_detection` | 50 | `cpu` | `ok` | 0.186331 | `{'app': 'outlier_detection', 'backend': 'cpu', 'copies': 50, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'outlier_count': 100}` |
| `outlier_detection` | 50 | `embree` | `ok` | 0.177767 | `{'app': 'outlier_detection', 'backend': 'embree', 'copies': 50, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'outlier_count': 100}` |
| `outlier_detection` | 50 | `scipy` | `ok` | 0.420793 | `{'app': 'outlier_detection', 'backend': 'scipy', 'copies': 50, 'matches_oracle': True, 'summary_mode': 'scipy_ckdtree_threshold_count', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'outlier_count': 100}` |
| `dbscan_clustering` | 50 | `cpu` | `ok` | 0.112348 | `{'app': 'dbscan_clustering', 'backend': 'cpu', 'copies': 50, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'core_count': 350}` |
| `dbscan_clustering` | 50 | `embree` | `ok` | 0.117141 | `{'app': 'dbscan_clustering', 'backend': 'embree', 'copies': 50, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'core_count': 350}` |
| `dbscan_clustering` | 50 | `scipy` | `ok` | 0.282614 | `{'app': 'dbscan_clustering', 'backend': 'scipy', 'copies': 50, 'matches_oracle': True, 'summary_mode': 'scipy_ckdtree_threshold_count', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'core_count': 350}` |
| `service_coverage_gaps` | 50 | `cpu` | `ok` | 0.140088 | `{'app': 'service_coverage_gaps', 'backend': 'cpu', 'copies': 50, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'covered_household_count': 150}` |
| `service_coverage_gaps` | 50 | `embree` | `ok` | 0.137208 | `{'app': 'service_coverage_gaps', 'backend': 'embree', 'copies': 50, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'covered_household_count': 150}` |
| `service_coverage_gaps` | 50 | `scipy` | `ok` | 0.288517 | `{'app': 'service_coverage_gaps', 'backend': 'scipy', 'copies': 50, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'covered_household_count': 150}` |
| `event_hotspot_screening` | 50 | `cpu` | `ok` | 0.126764 | `{'app': 'event_hotspot_screening', 'backend': 'cpu', 'copies': 50, 'native_continuation_active': False, 'native_continuation_backend': 'none'}` |
| `event_hotspot_screening` | 50 | `embree` | `ok` | 0.134039 | `{'app': 'event_hotspot_screening', 'backend': 'embree', 'copies': 50, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count'}` |
| `event_hotspot_screening` | 50 | `scipy` | `ok` | 0.284459 | `{'app': 'event_hotspot_screening', 'backend': 'scipy', 'copies': 50, 'native_continuation_active': False, 'native_continuation_backend': 'none'}` |
| `outlier_detection` | 500 | `cpu` | `ok` | 1.136126 | `{'app': 'outlier_detection', 'backend': 'cpu', 'copies': 500, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'outlier_count': 1000}` |
| `outlier_detection` | 500 | `embree` | `ok` | 1.032579 | `{'app': 'outlier_detection', 'backend': 'embree', 'copies': 500, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'outlier_count': 1000}` |
| `outlier_detection` | 500 | `scipy` | `ok` | 1.254146 | `{'app': 'outlier_detection', 'backend': 'scipy', 'copies': 500, 'matches_oracle': True, 'summary_mode': 'scipy_ckdtree_threshold_count', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'outlier_count': 1000}` |
| `dbscan_clustering` | 500 | `cpu` | `ok` | 0.136154 | `{'app': 'dbscan_clustering', 'backend': 'cpu', 'copies': 500, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'core_count': 3500}` |
| `dbscan_clustering` | 500 | `embree` | `ok` | 0.119881 | `{'app': 'dbscan_clustering', 'backend': 'embree', 'copies': 500, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'core_count': 3500}` |
| `dbscan_clustering` | 500 | `scipy` | `ok` | 0.289070 | `{'app': 'dbscan_clustering', 'backend': 'scipy', 'copies': 500, 'matches_oracle': True, 'summary_mode': 'scipy_ckdtree_threshold_count', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'core_count': 3500}` |
| `service_coverage_gaps` | 500 | `cpu` | `ok` | 0.126025 | `{'app': 'service_coverage_gaps', 'backend': 'cpu', 'copies': 500, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'covered_household_count': 1500}` |
| `service_coverage_gaps` | 500 | `embree` | `ok` | 0.123295 | `{'app': 'service_coverage_gaps', 'backend': 'embree', 'copies': 500, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'covered_household_count': 1500}` |
| `service_coverage_gaps` | 500 | `scipy` | `ok` | 0.275051 | `{'app': 'service_coverage_gaps', 'backend': 'scipy', 'copies': 500, 'native_continuation_active': False, 'native_continuation_backend': 'none', 'covered_household_count': 1500}` |
| `event_hotspot_screening` | 500 | `cpu` | `ok` | 0.147528 | `{'app': 'event_hotspot_screening', 'backend': 'cpu', 'copies': 500, 'native_continuation_active': False, 'native_continuation_backend': 'none'}` |
| `event_hotspot_screening` | 500 | `embree` | `ok` | 0.159383 | `{'app': 'event_hotspot_screening', 'backend': 'embree', 'copies': 500, 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count'}` |
| `event_hotspot_screening` | 500 | `scipy` | `ok` | 0.346461 | `{'app': 'event_hotspot_screening', 'backend': 'scipy', 'copies': 500, 'native_continuation_active': False, 'native_continuation_backend': 'none'}` |

## Boundary

This scale-ramp runner collects incremental local same-command health and timing evidence. It does not authorize speedup claims, and same-scale public comparisons still require review.

