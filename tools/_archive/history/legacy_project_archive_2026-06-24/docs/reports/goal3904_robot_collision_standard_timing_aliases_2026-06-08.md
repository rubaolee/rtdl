# Goal3904 Robot-Collision Standard Timing Aliases

## Purpose

Goal3902 exposed a measurement gap: the robot-collision benchmark payload was
valid and already contained phase timings, but the generic scale-runner timing
extractor reported `timing_scalar_count = 0` because the app used historical
names such as `total_run_seconds` and `phase_timing_seconds`.

Goal3904 adds a backward-compatible `benchmark_timing_sec` alias block to the
robot-collision prepared benchmark payload.

## Change

The app now keeps the existing fields unchanged:

- `app_lowering_seconds`
- `tail_medians.total_run_seconds`
- `tail_medians.phase_timing_seconds`
- per-run `total_run_seconds`
- per-run `phase_timing_seconds`

It additionally emits:

- `benchmark_timing_sec.app_lowering_sec`
- `benchmark_timing_sec.tail_total_run_sec`
- `benchmark_timing_sec.probe_reference_sec` when a probe reference is run
- `benchmark_timing_sec.tail_phase_<phase>_sec` for each tail phase median

These names are intentionally generic and app-layer only. No native source file,
native ABI, primitive contract, partner policy, or engine behavior changed.

## Interpretation

This is an instrumentation repair, not a performance optimization. It lets the
Goal3901 scale-runner timing extractor see the robot-collision hot path using
the same suffix policy as the other benchmark apps.

The next full scale packet should therefore move the robot row from
`timing_scalar_count = 0` to a positive count without changing the app result.

## Boundary

Goal3904 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, AMD performance wording, automatic partner/backend
selection, or app-specific native-engine logic.

This is an internal benchmark instrumentation cleanup.
