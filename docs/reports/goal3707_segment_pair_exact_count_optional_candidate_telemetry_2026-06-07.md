# Goal3707 Segment-Pair Exact Count Optional Candidate Telemetry

Date: 2026-06-07

## Purpose

Goal3705 brought same-source RayJoin LSI timing close to RayJoin by preparing both segment sets and using one-pass exact count. The remaining native hot path still performed an atomic candidate-event count for diagnostics.

Goal3707 makes that candidate-event telemetry optional for the exact-count pipeline so a future route can choose the lean form when evidence supports it.

## Change

Updated:

- `src/native/optix/rtdl_optix_workloads.cpp`

The exact-count any-hit program now checks:

```text
if (params.candidate_event_count != nullptr)
```

before incrementing the candidate-event counter.

The generic non-prepared-left scalar count route keeps telemetry enabled. After the Goal3708 negative pod probe, the selected prepared-left scalar-count route also keeps telemetry enabled because disabling it did not improve timing and removed useful diagnostics. The optional no-telemetry path remains available as a controlled implementation hook, not the selected route.

## Boundary

This is not an app-specific shortcut. It is a generic performance/telemetry tradeoff:

- exact emitted count remains authoritative,
- candidate-event count is diagnostic only,
- row/witness mode remains unchanged,
- no RayJoin/CDB branch or vocabulary is added.

This report requires pod evidence before any telemetry-disabled route is accepted as a selected performance path. Goal3708 records that the first prepared-left telemetry-disabled probe was negative and is not selected.

It does not authorize release, public speedup claims, RTDL-beats-RayJoin claims, RayJoin paper reproduction claims, broad RT-core claims, or true-zero-copy claims.
