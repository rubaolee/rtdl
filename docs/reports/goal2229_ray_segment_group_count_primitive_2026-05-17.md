# Goal2229: Generic Ray/Segment Group Count Primitive

Status: implemented locally, OptiX pod build/probe passed, pending external review.

## Purpose

Goal2229 adds the first RayJoin-inspired primitive that is still app-agnostic:

`rtdl_optix_run_ray_segment_group_count_2d`

The engine receives only:

- finite 2-D rays,
- finite 2-D segments,
- one caller-owned `uint32` group id per segment.

It returns one row per intersecting `(ray_id, group_id)` pair:

- `ray_id`
- `group_id`
- `hit_count`
- `parity`

This is intentionally not named after PIP, RayJoin, polygons, datasets, maps, or spatial joins. App-specific meaning remains in Python or partner code.

## Design

The first implementation reuses the existing OptiX segment-pair traversal path:

1. Convert each finite `RtdlRay2D` into a finite probe segment from `(ox, oy)` to `(ox + dx * tmax, oy + dy * tmax)`.
2. Run the existing OptiX segment-pair intersection traversal against the caller-supplied target segments.
3. Map target `segment_id` to the supplied `segment_group_id`.
4. Aggregate exact candidate rows on the host into count/parity rows keyed by `(ray_id, group_id)`.

This keeps the ABI narrow and makes the primitive immediately testable without adding a second custom OptiX shader before the semantics are reviewed.

## Boundary

This goal does not authorize:

- a public RayJoin speedup claim,
- a public PIP speedup claim,
- a v2.0 release claim,
- a claim that all group reductions are device-resident,
- a claim that this is the final optimized grouped ray/segment implementation.

The current implementation still performs host aggregation after OptiX traversal. The next optimization target is a device-resident grouped reduction or bounded/streaming group accumulator once this generic row contract is accepted.

## Correctness Contract

- The primitive counts exact finite ray/segment intersections as exposed by the existing OptiX segment-pair path and host exact refinement.
- `parity` is exactly `hit_count & 1`.
- Segment ids must be unique because group lookup is keyed by `segment_id`.
- Duplicate `ray_id` values are aggregated under the same output key; callers that need per-input-row identity should provide unique ray ids.
- Point-in-shape or spatial-join boundary rules, including half-open vertex handling, are not baked into the engine. Users can encode those policies by choosing input segments/rays or applying Python/partner post-processing.

## Files

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/optix_runtime.py`
- `tests/goal2229_ray_segment_group_count_primitive_test.py`

## Validation Plan

Local:

- Python compile check for `src/rtdsl/optix_runtime.py`.
- Static Goal2229 gate for ABI, wrapper, report boundary, and app-agnostic naming.

Pod:

- Build `librtdl_optix.so` from current `main`.
- Run a small functional probe with finite rays and grouped segments.
- Compare output with a Python exact reference for count and parity.
- Record hardware, commit, command, and artifact path before making any performance statement.

## Validation Executed

Local Windows:

```text
$env:PYTHONPATH='src;.'; py -3 -m py_compile src\rtdsl\optix_runtime.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2229_ray_segment_group_count_primitive_test
Ran 4 tests: OK
```

RTX pod:

- SSH: `root@69.30.85.202 -p 22064`
- Key: local RTDL working pod key
- Pod checkout: `/root/rtdl_goal2198_launcher/rtdl`
- Base commit during patch validation: `c4279f6d`
- Clean pushed commit validation: `2b32f876`
- OptiX SDK: `/root/vendor/optix-sdk`
- CUDA prefix: `/usr/local/cuda-12.8`

Build:

```text
timeout 600 make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
```

Result: build completed and produced `build/librtdl_optix.so`.

Functional probe:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so python3 /root/goal2229_probe.py
```

Probe input:

- ray `1`: finite horizontal ray from `(0, 0)` through `tmax=10`
- ray `2`: finite horizontal ray from `(0, 2)` through `tmax=10`
- segments `10` and `11`: group `7`, both intersect ray `1`
- segment `12`: group `8`, intersects ray `1`
- segment `13`: group `8`, intersects neither ray

Observed output:

```json
[
  {"group_id": 7, "hit_count": 2, "parity": 0, "ray_id": 1},
  {"group_id": 8, "hit_count": 1, "parity": 1, "ray_id": 1}
]
```

The probe assertion compared this output to the exact expected rows and passed.

Pod static gate:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal2229_ray_segment_group_count_primitive_test
Ran 4 tests: OK
```

Clean pushed-commit rerun:

```text
git fetch origin main
git reset --hard origin/main
git rev-parse --short HEAD
2b32f876

timeout 600 make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2229_ray_segment_group_count_primitive_test \
  tests.goal2231_ray_segment_group_count_2ai_consensus_test
Ran 7 tests: OK

PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal2198_launcher/rtdl/build/librtdl_optix.so \
  python3 /root/goal2229_probe.py
[
  {"group_id": 7, "hit_count": 2, "parity": 0, "ray_id": 1},
  {"group_id": 8, "hit_count": 1, "parity": 1, "ray_id": 1}
]
```
