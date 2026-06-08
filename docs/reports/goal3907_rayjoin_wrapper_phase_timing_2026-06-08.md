# Goal3907 RayJoin Wrapper Phase Timing

## Purpose

Goal3906 identified RayJoin as the next wrapper-heavy benchmark row: its
representative script reports per-contract hot medians, but its full wrapper
elapsed time is still about nine seconds on the A5000 packet.

Goal3907 adds standard `wrapper_phase_timing_sec` fields around the RayJoin
representative script's major sub-probes:

- data directory resolution
- PIP one-shot probe
- LSI/overlay probe
- PIP batch probe
- total wrapper time

## Change

The change is instrumentation-only in
`scripts/goal3866_rayjoin_representative_scale_profile.py`. It does not change
the benchmark contracts, route recommendations, counts, native engine ABI,
partner selection policy, or public claim boundary.

The new payload field is:

`wrapper_phase_timing_sec`

with keys:

- `data_dir_resolve_sec`
- `pip_one_shot_probe_sec`
- `lsi_overlay_probe_sec`
- `pip_batch_probe_sec`
- `profile_total_sec`

These names use the standard `_sec` suffix so Goal3901's generic timing
extractor can pick them up automatically.

## Boundary

Goal3907 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, AMD performance wording, automatic partner/backend
selection, or app-specific native-engine logic.

This is an internal RayJoin measurement-instrumentation step, not a public performance comparison and not a release packet.
