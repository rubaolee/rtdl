# Goal3984 Resident Hot-Query Summary Contract

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal3983 showed that simply increasing RayDB row count and robot-collision query geometry does not make the representative hot-path metrics claim-grade. The actual OptiX hot calls stay very short, while setup, packing, prepared-query construction, wrapper time, and JSON payload size dominate the observable process wall time.

Goal3984 adds an explicit resident high-repeat hot-query summary contract for those short rows.

## What Changed

- RayDB-style primitive-first prepared OptiX now accepts `--summary-only-iterations`.
- Robot collision prepared modes now accept `--summary-only-runs`.
- Both switches are opt-in. Default CLI output remains unchanged for ordinary tutorials and examples.
- RayDB records `metadata.prepared_iteration_wall_summary` and `metadata.prepared_phase_timing_summary`.
- Robot records `run_summary` plus compact prepared-run and prepared-query index summaries.
- The current benchmark scale registry now points the two short rows at aggregate hot-path totals rather than tiny per-call medians:
  - RayDB: `metadata.prepared_phase_timing_summary.native_call_wall.total_sec`
  - Robot collision: `run_summary.phase_timing_seconds.traversal.total_sec`

## Why This Exists

The prior short-row probes taught us that wrapper elapsed is a pod-budget signal, not a hot-path metric. If a single resident OptiX query completes in microseconds, making the input larger is often the wrong calibration knob. The better measurement contract is:

1. Prepare resident scene/query/payload state once.
2. Run many independent hot queries under the same prepared contract.
3. Suppress per-iteration JSON arrays.
4. Report both median and total hot-path timing summaries.
5. Keep setup, wrapper elapsed, and validation separated from performance claims.

This is not a loader or OptiX SDK issue. The Goal3975/3976 helper chain already proved the fresh pod toolchain works.

## Current-Scale Registry Update

The registry changes only the two known short rows:

| App | New repeat protocol | Representative hot-path metric |
| --- | --- | --- |
| `raydb_style` | `--repeat 5000 --warmup 50 --summary-only-iterations` | `metadata.prepared_phase_timing_summary.native_call_wall.total_sec` |
| `robot_collision` | `--repeats 50000 --warmup 100 --summary-only-runs` | `run_summary.phase_timing_seconds.traversal.total_sec` |

`hot_path_duration_target_sec=1.0` is a calibration target, not a release claim.

## Claim Boundary

This work does not authorize public speedup wording, broad RT-core speedup wording, true-zero-copy wording, release wording, or paper-reproduction wording. Wrapper elapsed remains pod-budget evidence. The representative metrics are internal current-scale hot-path timing summaries used to make pod evidence less noisy and less JSON-heavy.

## Next Validation

Run the current ten-app scale profile on the RTX pod after this contract lands. The expected improvement is not necessarily faster absolute app runtime; the expected improvement is better measurement quality for the two short rows: seconds-level aggregate hot-path summaries without dumping huge per-iteration payloads.
