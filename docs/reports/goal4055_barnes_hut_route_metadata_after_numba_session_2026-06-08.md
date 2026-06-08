# Goal4055 Barnes-Hut Route Metadata After Numba Session

Date: 2026-06-08

## Purpose

Goal4055 updates the current Barnes-Hut route and adequacy metadata after
Goals4052-4053.

The technical change is narrow: Barnes-Hut now has a generic prepared Numba
grouped-vector continuation session available for presegmented typed streams.
That closes the per-call adapter overhead uncovered by Goal4052 and measured in
Goal4053.

## Scope

This does not promote Numba as the fastest full Barnes-Hut force route, does not
claim whole-app Barnes-Hut acceleration, and does not change the app-agnostic
engine boundary. CuPy remains the fastest measured exact-force continuation in
the older full-force route, while Numba is the no-RawKernel reference and now
has a prepared session for the grouped-vector stream subcontract.

The next large Barnes-Hut performance direction remains a deeper hierarchical
vector primitive design, not app-only tuning.

## Files Updated

- `src/rtdsl/current_benchmark_route_decisions.py`
- `src/rtdsl/v2_9_benchmark_adequacy.py`
- `src/rtdsl/current_benchmark_scale_profiles.py`
- `tests/goal4055_barnes_hut_route_metadata_after_numba_session_test.py`

