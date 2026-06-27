# Goal1036 Outlier Density-Count Oracle Fix

Date: 2026-04-26

## Scope

Goal1036 fixes the `outlier_detection` local baseline bottleneck found during Goal1035. The `density_count` path already avoided neighbor-row materialization for CPU, Embree, and SciPy, but its oracle check still used `brute_force_outlier_rows()` unless `output_mode == density_summary`.

That accidentally reintroduced O(N^2) work into the scalar `density_count` path and hid the backend timing signal.

## Code Change

File changed:

- `examples/rtdl_outlier_detection_app.py`

Behavior changed:

- `output_mode == density_count` now uses `expected_tiled_density_rows(copies=...)` for oracle rows, the same closed-form tiled oracle already used by `density_summary`.
- `output_mode == full` still uses `brute_force_outlier_rows()` because full row semantics require the brute-force oracle.

Regression test:

- `tests/goal1036_outlier_density_count_oracle_test.py`

The test patches `brute_force_outlier_rows()` to fail and verifies that `density_count` at `copies=2000` still passes correctness with the closed-form oracle.

## Evidence

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests/goal1036_outlier_density_count_oracle_test.py \
  tests/goal1035_local_baseline_scale_ramp_test.py
```

Result: `6 tests OK`.

After the fix, outlier-only scale ramp:

| Copies | CPU (s) | Embree (s) | SciPy (s) | Status |
|---:|---:|---:|---:|---|
| 2000 | 0.159692 | 0.137149 | 0.484763 | `ok` |
| 20000 | 0.313782 | 0.314325 | 0.941071 | `ok` |

All four baseline-ready apps at `copies=20000`:

| App | CPU (s) | Embree (s) | SciPy (s) | Status |
|---|---:|---:|---:|---|
| `outlier_detection` | 0.365416 | 0.304603 | 1.045236 | `ok` |
| `dbscan_clustering` | 0.318811 | 0.311104 | 0.943645 | `ok` |
| `service_coverage_gaps` | 2.141152 | 0.362919 | 0.767360 | `ok` |
| `event_hotspot_screening` | 5.895585 | 0.552202 | 1.292635 | `ok` |

Artifacts:

- `docs/reports/goal1036_outlier_density_count_after_oracle_fix_2026-04-26.md`
- `docs/reports/goal1036_outlier_density_count_after_oracle_fix_2026-04-26.json`
- `docs/reports/goal1036_all_ready_apps_20000_after_outlier_fix_2026-04-26.md`
- `docs/reports/goal1036_all_ready_apps_20000_after_outlier_fix_2026-04-26.json`

## Engineering Conclusion

The previous outlier app-level timing anomaly was not an Embree/RT limitation. It was an app oracle bug in the `density_count` baseline path. Removing the unnecessary brute-force oracle makes local same-command baselines practical again.

The post-fix 20000-copy run gives useful internal local timing shape for the four baseline-ready apps. It does not by itself authorize public speedup language.

## Boundary

This is a correctness and local-baseline execution fix. It does not authorize public speedup claims, release authorization, or NVIDIA RT-core claims. Public RTX wording still requires cloud RTX same-semantics evidence and review.
