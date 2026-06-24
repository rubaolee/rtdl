# Goal3701 Segment-Pair One-Pass Exact Count Pipeline

Date: 2026-06-07

## Purpose

Goal3700 moved exact segment-pair refinement from the host to a CUDA kernel, but it still required:

1. an OptiX candidate-count pass,
2. an OptiX candidate-write pass,
3. a CUDA exact-refine pass over the emitted candidate records.

Goal3701 implements the stronger generic path for scalar counts:

```text
one OptiX traversal pass -> exact double predicate in any-hit -> scalar count
```

## Change

Updated:

- `src/native/optix/rtdl_optix_workloads.cpp`
- `scripts/goal3612_rayjoin_safe_mixed_route_composite.py`

The prepared segment-pair scalar-count route now uses a dedicated app-agnostic exact-count pipeline:

- the RT traversal still discovers segment AABB candidates,
- the any-hit stage runs the same double-precision segment intersection predicate shape used by the host exact-refine contract,
- the any-hit stage increments a scalar exact count only for exact-valid hits,
- no candidate row table is materialized,
- no candidate rows are downloaded,
- row/witness mode remains unchanged.

The high-level RayJoin helper metadata was also updated from the stale `host_double_exact_refine_after_optix_candidates` wording to the current `device_double_exact_count_during_optix_anyhit` wording.

## Boundary

This is a generic segment-pair primitive improvement, not a RayJoin-specific engine path.

It does not authorize:

- release,
- default-route promotion,
- RTDL-beats-RayJoin claims,
- RayJoin paper reproduction claims,
- public speedup claims,
- broad RT-core claims,
- true zero-copy claims.

## Required Pod Evidence

Before accepting the path:

- build OptiX from the committed source on an NVIDIA pod,
- prove focused tests pass,
- prove the same-source LSI scalar count remains `20860`,
- record phase timings,
- compare against Goal3698/Goal3700 timing,
- keep all claim-boundary flags false.

