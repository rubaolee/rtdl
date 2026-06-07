# Goal3707 Segment-Pair Exact Count Optional Candidate Telemetry

Date: 2026-06-07

## Purpose

Goal3705 brought same-source RayJoin LSI timing close to RayJoin by preparing both segment sets and using one-pass exact count. The remaining native hot path still performed an atomic candidate-event count for diagnostics.

Goal3707 makes that candidate-event telemetry optional for the exact-count pipeline.

## Change

Updated:

- `src/native/optix/rtdl_optix_workloads.cpp`

The exact-count any-hit program now checks:

```text
if (params.candidate_event_count != nullptr)
```

before incrementing the candidate-event counter.

The generic non-prepared-left scalar count route keeps telemetry enabled. The prepared-left scalar count route disables candidate-event telemetry for the hot path and records `raw_candidate_count = 0` as an explicit "not collected" value.

## Boundary

This is not an app-specific shortcut. It is a generic performance/telemetry tradeoff:

- exact emitted count remains authoritative,
- candidate-event count is diagnostic only,
- row/witness mode remains unchanged,
- no RayJoin/CDB branch or vocabulary is added.

This report requires pod evidence before the telemetry-disabled route is accepted.

It does not authorize release, public speedup claims, RTDL-beats-RayJoin claims, RayJoin paper reproduction claims, broad RT-core claims, or true-zero-copy claims.

