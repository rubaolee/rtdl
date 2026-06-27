# Goal1036 Claude Review

Date: 2026-04-26
Verdict: **ACCEPT**

## Facts Verified

### 1. `expected_tiled_density_rows` used as oracle for `density_summary` and `density_count`

Confirmed in `examples/rtdl_outlier_detection_app.py` lines 429–432:

```python
oracle_rows = (
    expected_tiled_density_rows(copies=copies)
    if output_mode in {"density_summary", "density_count"}
    else brute_force_outlier_rows(case["points"])
)
```

Also confirmed at line 390 (`density_count` non-optix/scipy branch builds `oracle_scalar_rows` via `expected_tiled_density_rows`) and line 408 (`density_summary` fallback assigns `density_rows = expected_tiled_density_rows(copies=copies)`). The O(N²) `brute_force_outlier_rows` is correctly bypassed in both compact modes.

### 2. Test oracle isolation

`tests/goal1036_outlier_density_count_oracle_test.py` contains two tests:

- `test_density_count_uses_closed_form_oracle_not_bruteforce`: patches `brute_force_outlier_rows` to raise `AssertionError`, runs `run_app("cpu", copies=2000, output_mode="density_count")`, asserts `matches_oracle=True`, `outlier_count=4000`, `summary_mode="scalar_threshold_count_oracle"`. Pass confirms `brute_force_outlier_rows` is never called in `density_count` mode.
- `test_full_mode_still_uses_bruteforce_oracle`: patches `brute_force_outlier_rows` with a mock returning `expected_tiled_density_rows(copies=1)`, runs `run_app("cpu", copies=1, output_mode="full")`, asserts `mock.assert_called_once()`. Confirms full mode still routes through the brute-force oracle.

Both tests are structurally sound and cover the regression of interest.

### 3. Scale-ramp report: 20000 copies passes, no public speedup or RTX claim

`docs/reports/goal1036_all_ready_apps_20000_after_outlier_fix_2026-04-26.md` shows `outlier_detection` at 20000 copies for all three backends returning `status: ok` and `matches_oracle: True` (outlier_count=40000). The report boundary section explicitly states: "It does not authorize speedup claims, and same-scale public comparisons still require review." No RTX or public performance claim appears anywhere in the reports or app code.

## Summary

All three stated facts are present and correct in the repository. The fix correctly replaces the O(N²) brute-force oracle with the closed-form `expected_tiled_density_rows` in `density_summary` and `density_count` modes, the oracle isolation is unit-tested with both positive and negative coverage, and the scale evidence is appropriately bounded.
