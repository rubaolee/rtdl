# Call For Review: V4 Goal4738 RayDB Hot-Path Materialization Boundary Repair

Please review:

- `future/v4/v4_goal4738_raydb_hotpath_materialization_boundary_repair_2026-06-26.md`
- `future/v4/evidence/v4_goal4738_raydb_hotpath_materialization_boundary_repair_2026-06-26.json`
- `examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `tests/v4_goal4732_raydb_device_output_route_test.py`
- `future/v4/evidence/v4_goal4738_raydb_hotpath_20260626/summary.json`
- `future/v4/evidence/v4_goal4738_raydb_hotpath_20260626/raw/v4_current_raydb_style.json`
- `tests/v4_goal4738_raydb_hotpath_repair_test.py`

## Context

Goal4732 repaired RayDB route binding but left V4/V3.0.2 hot at `0.954x`.
Goal4738 found that the native V4 device-output traversal was not slower; the
regression came from Python row presentation inside the measured hot window.

After repair:

- V4/V2.14 hot: `1.1031164464050043`
- V4/V3.0.2 hot: `1.1048050187116953`
- correctness parity: true
- V4 row presentation in measured timing: `0.0`
- result materialization after hot path: recorded separately

## Questions For Reviewer

1. Is the root cause correct?
2. Is it valid for `--summary-only-iterations` to measure the V4 device-output
   hot path and materialize rows after timing for correctness?
3. Does this repair remain generic app-frontdoor/runtime work rather than an
   app-specific native kernel?
4. Is the result correctly classified as modest RayDB repair, not formal
   high-performance RayDB evidence?
5. Are the non-authorization boundaries sufficient?

## Requested Verdict Labels

- `accept_goal4738_raydb_regression_cleared`
- `accept_with_required_amendments`
- `reject_goal4738_invalid_timing_boundary`

## Non-Authorization

This review must not authorize final V4 tag, public speed claims, RayDB
high-performance claims, all-benchmark speedups, geomean headlines, automatic
partner selection, app-specific native kernels, true-zero-copy wording, or broad
V4-over-V3 wording.
