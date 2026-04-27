# Goal1035 Local Baseline Scale Ramp

Date: 2026-04-26

This scale-ramp runner collects incremental local same-command health and timing evidence. It does not authorize speedup claims, and same-scale public comparisons still require review.

## Summary

- copies_list: `[2000, 20000]`
- timeout_sec: `180.0`
- rows: `6`
- status: `ok`

## Results

| App | Copies | Backend | Status | Elapsed (s) | Summary |
|---|---:|---|---|---:|---|
| `outlier_detection` | 2000 | `cpu` | `ok` | 0.159692 | `{'app': 'outlier_detection', 'backend': 'cpu', 'copies': 2000, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'outlier_count': 4000}` |
| `outlier_detection` | 2000 | `embree` | `ok` | 0.137149 | `{'app': 'outlier_detection', 'backend': 'embree', 'copies': 2000, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'outlier_count': 4000}` |
| `outlier_detection` | 2000 | `scipy` | `ok` | 0.484763 | `{'app': 'outlier_detection', 'backend': 'scipy', 'copies': 2000, 'matches_oracle': True, 'summary_mode': 'scipy_ckdtree_threshold_count', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'outlier_count': 4000}` |
| `outlier_detection` | 20000 | `cpu` | `ok` | 0.313782 | `{'app': 'outlier_detection', 'backend': 'cpu', 'copies': 20000, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'outlier_count': 40000}` |
| `outlier_detection` | 20000 | `embree` | `ok` | 0.314325 | `{'app': 'outlier_detection', 'backend': 'embree', 'copies': 20000, 'matches_oracle': True, 'summary_mode': 'scalar_threshold_count_oracle', 'native_continuation_active': True, 'native_continuation_backend': 'embree_threshold_count', 'outlier_count': 40000}` |
| `outlier_detection` | 20000 | `scipy` | `ok` | 0.941071 | `{'app': 'outlier_detection', 'backend': 'scipy', 'copies': 20000, 'matches_oracle': True, 'summary_mode': 'scipy_ckdtree_threshold_count', 'native_continuation_active': False, 'native_continuation_backend': 'none', 'outlier_count': 40000}` |

## Boundary

This scale-ramp runner collects incremental local same-command health and timing evidence. It does not authorize speedup claims, and same-scale public comparisons still require review.

