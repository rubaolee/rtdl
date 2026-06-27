# Goal3697 Segment-Pair Precision-Guard Native Candidate Policy

Date: 2026-06-07

## Purpose

Goal3693 localized the same-source RayJoin LSI mismatch to one endpoint-near segment pair that exact arithmetic includes but float32 candidate arithmetic can drop. Goal3696 made the desired behavior executable at the Python contract layer.

Goal3697 applies the first generic OptiX candidate-policy repair.

## Change

Updated:

- `src/native/optix/rtdl_optix_core.cpp`
- `tests/goal2169_optix_lsi_device_conservative_exact_filter_test.py`

The generic `seg_intersect_conservative_candidate(...)` path now uses:

```cpp
const float slack = 1.0e-3f;
```

instead of:

```cpp
const float slack = 1.0e-4f;
```

The change is intentionally narrow:

- only the generic segment-pair conservative candidate predicate changes,
- host-side exact refinement remains the final authority,
- no app-specific branch or RayJoin/CDB vocabulary was added,
- native ABI names are unchanged.

## Why This Is The Right First Repair

The localized missing pair has:

```text
exact t ~=  0.00007568719169345676
float t ~= -0.00018010620260611176
```

The old `1e-4` guard could still reject this pair in the low-precision candidate predicate. The new `1e-3` guard should emit it as a candidate so exact refinement can keep or reject it using the existing double-precision final check.

## Boundary

This report is a static/native-policy implementation note until pod evidence proves the route.

It does not authorize:

- release,
- default-route promotion,
- RTDL-beats-RayJoin claims,
- RayJoin paper reproduction claims,
- public speedup claims,
- broad RT-core claims,
- true zero-copy claims.

## Required Pod Evidence

Before treating this repair as accepted, rerun the same-source LSI pair-set probe on an NVIDIA pod and require:

- RayJoin pair count `20860`,
- RTDL normalized pair count `20860`,
- missing count `0`,
- extra count `0`,
- query timing recorded with phase telemetry,
- claim boundaries still false.

