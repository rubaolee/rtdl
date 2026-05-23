# Robot Collision Study

This directory is the RTDL robot-collision benchmark-app campaign started by
Goal2479/2480.

The goal is not to clone a robotics paper implementation. The first goal is to
build a deterministic CPU reference for this app shape:

```text
static obstacle triangles + batched transformed query meshes -> compact any-hit flags
```

No robot-specific native ABI is added.

## File

| File | Role |
| --- | --- |
| `rtdl_robot_collision_benchmark_app.py` | CPU-reference app, prepared Embree/OptiX probe modes, prepared host-buffer modes, and matrix CLI for deterministic robot-collision fixtures |

## First Correctness Run

Run from the repository root:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py --dataset tiny --include-rows
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\v2_0\research_benchmarks\robot_collision\rtdl_robot_collision_benchmark_app.py --dataset tiny --include-rows
```

The tiny fixture has five deterministic two-link poses against one static
rectangular obstacle. The expected compact link flags are:

```text
[0, 0, 0, 1, 1, 1, 0, 0, 0, 1]
```

The ordering is pose-major, then link-major.

## Scaled CPU Fixture

Use the scaled fixture to exercise deterministic batching without native code:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py --dataset scaled --pose-count 32 --obstacle-count 9 --link-count 3
```

This is still a CPU reference. It is useful for contract and JSON-shape checks,
not for performance claims.

## Prepared Probe Modes

Goal2484 adds app-level lowering to the Goal2481 generic contract:

```text
PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1
```

The lowering samples each transformed link at its center, four corners, and
four edge midpoints, then emits vertical finite 3D segment probes through those
sample points. Groups remain pose-major then link-major. This is a discrete
sampled probe contract, not exact solid collision and not continuous/swept
collision.

Run a local Embree prepared repeat probe:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py --mode embree_prepared --dataset tiny --repeats 7 --warmup 2
```

Goal2488 adds prepared host-buffer modes that reuse Python-owned ctypes segment,
group-offset, and output-flag buffers across prepared-scene runs:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py --mode embree_prepared_buffers --dataset tiny --repeats 7 --warmup 2
```

The prepared-buffer modes remove repeated Python packing/allocation on the
query path. They do not claim native device-buffer reuse or true zero-copy;
OptiX still uploads query segments per run through the current native ABI.

Run a bounded matrix without OptiX:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py --matrix --dataset scaled --pose-count 64 --obstacle-count 16 --link-count 3 --repeats 7 --warmup 2 --skip-optix
```

On an NVIDIA pod with the OptiX backend built, omit `--skip-optix`.

## Current Output Contract

The app returns:

- `pose_summaries`: per-pose compact any-hit summaries;
- `link_flags`: per-pose/per-link any-hit flags;
- `compact_link_flags`: a pose-major compact `0/1` flag vector;
- optional `hit_pairs` when `--include-rows` is passed.

The future generic RTDL contract target is:

```text
prepared_static_triangles_plus_batched_transformed_query_geometry_to_compact_any_hit_flags
```

Goal2481 must decide the native/partner compact output representation. Options
include byte-per-query flags, bit-packed flags, or a typed partner/native
column. That decision should follow RTDL buffer and tensor conventions, not
robot-link convenience.

The current CPU reference is 2D. Goal2481 must explicitly decide whether the
native contract remains 2D for this lane, generalizes to 3D transformed
triangles, or needs an additional 3D CPU oracle before Embree/OptiX parity work.

## Claim Boundary

- This app implements a CPU reference path plus generic prepared Embree/OptiX
  sampled-probe paths.
- It does not authorize paper reproduction, authors-code comparison, or public
  speedup claims.
- It does not implement continuous/swept collision.
- Prepared modes implement sampled finite segment probes only; they do not
  authorize exact solid-contact wording.
- Native Embree/OptiX surfaces remain app-agnostic and use the generic grouped
  finite 3D segment any-hit contract.
- Python owns robot/link/pose/collision semantics. The future native engine
  should see only generic geometry, transformations, batching, any-hit flags,
  compact columns, and phase timing.
- Paper citation, venue, DOI, official code, and official data remain blocked
  until a later scoping goal verifies them.
