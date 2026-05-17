# Goal2238: Generic Closed-Shape Membership Primitive

Status: implemented and validated on the RTX pod; pending external review.

## Purpose

Goal2233 and Goal2235 showed that generic ray/segment grouped parity is correct
but not the right performance shape for RayJoin-style point-location workloads.
Even after prepared scene reuse and compact odd-parity output, the generic
boundary-crossing path still has to compute many boundary segment intersections
before it can emit sparse positive memberships.

Goal2238 adds a generic closed-shape membership surface:

`rtdl_optix_run_point_closed_shape_membership_2d`

Python exposes it as:

`closed_shape_membership_2d_optix(points, shapes, result_mode="positive_hits")`

## Design

The public ABI uses only generic terms:

- point
- closed shape
- shape id
- membership
- positive rows

The returned row is:

- `point_id`
- `shape_id`
- `membership`

This is intentionally not named after RayJoin, PIP, counties, maps, GIS layers,
or spatial joins. App meaning stays in Python/partner code.

## Implementation Note

This first implementation wraps the existing optimized OptiX closed-boundary
candidate/predicate path and converts the legacy internal row into the new
generic public row:

- legacy internal row field: `polygon_id`
- generic public row field: `shape_id`
- legacy internal row field: `contains`
- generic public row field: `membership`

That keeps the new public surface app-agnostic while avoiding the much slower
ray/segment grouped-parity route for workloads that need compact positive
closed-shape memberships.

## Boundary

This goal does not authorize:

- a v2.0 release claim,
- a broad RayJoin speedup claim,
- a broad PIP speedup claim,
- a full RayJoin reproduction claim,
- a claim that all closed-shape workflows are optimized,
- a claim that the old internal closed-boundary implementation has been fully
  renamed or rewritten internally.

It is not a v2.0 release claim and not a full RayJoin reproduction claim. It is
a narrow app-agnostic public primitive that gives users the compact output
shape needed for point/closed-shape membership programs.

## Validation Plan

Local:

```text
$env:PYTHONPATH='src;.'; py -3 -m py_compile src\rtdsl\optix_runtime.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2238_closed_shape_membership_primitive_test
```

Pod:

```text
timeout 600 make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
PYTHONPATH=src:. python3 -m unittest tests.goal2238_closed_shape_membership_primitive_test
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so \
  python3 /root/goal2238_closed_shape_membership_probe.py
```

RayJoin-style probe:

- Compare `closed_shape_membership_2d_optix(..., result_mode="positive_hits")`
  against the legacy optimized positive row set.
- Expect exact row equality.
- Expect the same performance class as the optimized closed-boundary path, not
  the slower ray/segment grouped-parity path.

Any speed statement must stay scoped to this exact primitive and probe.

## Validation Executed

Local Windows:

```text
$env:PYTHONPATH='src;.'; py -3 -m py_compile src\rtdsl\optix_runtime.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2238_closed_shape_membership_primitive_test
Ran 6 tests: OK
```

RTX pod:

- SSH: `root@69.30.85.202 -p 22064`
- Pod checkout: `/root/rtdl_goal2198_launcher/rtdl`
- Base commit during patch validation: `198ba220`
- OptiX SDK: `/root/vendor/optix-sdk`
- CUDA prefix: `/usr/local/cuda-12.8`

```text
git fetch origin main
git reset --hard origin/main
git apply /root/goal2238_mod.patch
timeout 600 make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
PYTHONPATH=src:. python3 -m unittest tests.goal2238_closed_shape_membership_primitive_test
Ran 6 tests: OK
```

Small functional probe:

```json
[
  {"membership": 1, "point_id": 1, "shape_id": 10},
  {"membership": 1, "point_id": 3, "shape_id": 11}
]
```

## RayJoin-Style Timing Probe

Command:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so \
  N=10000 REPEATS=5 timeout 420 python3 /root/goal2238_rayjoin_closed_shape_probe.py
```

The probe prepacked points and shapes once before timing the primitive, so the
numbers measure the closed-shape membership call rather than repeated Python
shape encoding.

Observed payload:

```json
{
  "closed_shape_median_sec": 0.03738784417510033,
  "closed_shape_over_legacy_ratio": 0.9708922128019587,
  "closed_shape_rows": 879,
  "legacy_median_sec": 0.03850874863564968,
  "legacy_rows": 879,
  "limit": 10000,
  "repeats": 5,
  "row_match": true
}
```

Interpretation:

- The new generic wrapper matched the legacy optimized positive row set exactly.
- The generic wrapper is in the same performance class as the legacy optimized
  path on this probe.
- It is much faster than the ray/segment grouped-parity path from Goal2235
  (`0.282348` seconds median for compact odd parity on the same 10,000-query
  workload).

This supports the design conclusion: point/closed-shape membership should not be
lowered through boundary-segment grouped parity when the user wants compact
membership rows. The correct generic primitive shape is closed-shape membership
or a future caller-supplied predicate path.

## Pushed-Commit Pod Rerun

After the Goal2240 consensus commit was pushed, the RTX pod was reset to
`origin/main` at `b6bbba120c86697454cbf876113fbbf965755282`, rebuilt from Git,
and rerun without local patches:

```text
timeout 600 make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2238_closed_shape_membership_primitive_test \
  tests.goal2240_closed_shape_membership_2ai_consensus_test
Ran 9 tests: OK
```

The same functional probe returned the two expected positive membership rows,
and the timing probe produced:

```json
{
  "closed_shape_median_sec": 0.03516587242484093,
  "closed_shape_over_legacy_ratio": 0.8500515311435861,
  "closed_shape_rows": 879,
  "legacy_median_sec": 0.041369106620550156,
  "legacy_rows": 879,
  "limit": 10000,
  "repeats": 5,
  "row_match": true
}
```
