# Gemini Review: Goal3984/3985 Hot-Query Summary Chain

Date: 2026-06-08
Verdict: `accept`

## Summary of Work

This review covers the introduction of the resident high-repeat hot-query summary contract (Goal 3984) and its validation across the current-scale benchmark suite (Goal 3985). The primary objective was to improve the measurement quality for benchmarks that execute very quickly (the "short rows") by increasing their repetition count while suppressing the resulting large JSON payloads.

### Key Changes

1.  **Benchmark App Enhancements**:
    *   `raydb_style_benchmark_app.py`: Added `--summary-only-iterations` to suppress per-iteration `prepared_iteration_wall_sec` arrays.
    *   `robot_collision_benchmark_app.py`: Added `--summary-only-runs` to suppress the `runs` list in the JSON output.
    *   Both apps continue to provide `_numeric_series_summary` (min, max, median, total, count) for all phases, ensuring high-fidelity aggregate metrics are available.

2.  **Scale Profile Calibration**:
    *   `raydb_style_optix_count_scale_default_262k`: Increased to 5000 repeats with 50 warmups.
    *   `robot_collision_optix_scale_default_1024_no_probe_reference`: Increased to 50000 repeats with 100 warmups.
    *   Both rows now utilize the new summary-only flags.

3.  **Registry Updates**:
    *   `src/rtdsl/current_benchmark_scale_profiles.py` was updated to reflect the new commands and metrics.
    *   `representative_hot_path_metric` for these rows now correctly targets the aggregate `total_sec` of the primary hot-path phase (e.g., `traversal` or `native_call_wall`).

## Verification Results

### Artifact Analysis

The validation run on an RTX 4000 Ada pod (Goal 3985) confirms the success of the new contract:
*   **Total Pass**: All 10 benchmark apps in the suite passed (`all_pass: true`).
*   **Payload Reduction**: Despite the high repeat counts (50k for robot collision), the JSON output remains small (e.g., ~6KB for robot collision vs. what would have been multi-megabyte arrays).
*   **Measurement Quality**: The aggregate hot-path durations for the updated rows are now significant and easily measurable:
    *   `robot_collision`: Traversal `total_sec` ≈ 2.036s.
    *   `raydb_style`: Native call wall `total_sec` ≈ 3.011s.

### Automated Tests

The following focused tests were executed and passed:
*   `tests/goal3984_resident_hot_query_summary_contract_test.py`
*   `tests/goal3985_current_scale_after_hot_query_summary_test.py`

Verdict: **OK** (Ran 10 tests in 0.006s).

## Claim Boundaries

As per the project mandates and the reports reviewed, the following boundaries remain in effect:
*   **No Release Authorization**: This work is for internal scale calibration and does not authorize release actions.
*   **No Public Speedup Claims**: These measurements are for internal benchmarking and cannot be used for public-facing marketing or speedup claims.
*   **Metric Scope**: The `representative_hot_path_metric` captures the aggregate duration of the hot-path kernel; the `wrapper_elapsed_sec` remains the primary metric for pod budgeting and include loader overhead.
*   **Internal Registry**: The scale profiles and metrics remain part of an internal-only registry.

## Final Verdict

The work effectively resolves the "short row" measurement quality issue by providing a clean, compact mechanism for high-repetition benchmarking. The implementation is consistent across the target apps and the registry update is correctly calibrated.

**Verdict: `accept`**
