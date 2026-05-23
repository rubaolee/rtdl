# Goal2484 Robot Collision Prepared/Reused Execution

Date: 2026-05-21

Status: Goal2484 is complete.

## Scope

Goal2484 adds prepared-session support at the robot-collision benchmark layer
using the already approved Goal2481 generic contract:

```text
PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1
```

No native files were changed. The native Embree/OptiX engines still see only
static 3D triangles, finite 3D segment probes, group offsets, and byte flags.
Python owns the benchmark geometry, labels, transforms, grouping, and
interpretation.

## App Lowering

The 2D fixture is lowered into the generic 3D segment-probe contract by sampling
each transformed link at nine points:

- center;
- four corners;
- four edge midpoints.

Each sampled point becomes a vertical finite 3D segment from `z=1` to `z=-1`.
Static obstacle triangles are embedded into the `z=0` plane. One query group is
created per pose/link pair, in pose-major then link-major order.

This is not exact solid collision. It is a discrete sampled probe lowering that
is useful for exercising RTDL's prepared static scene plus changing query batch
runtime pattern.

Tiny fixture probe flags:

```text
[0, 0, 0, 1, 1, 1, 0, 0, 0, 1]
```

Those flags match the tiny exact 2D CPU fixture, but that match is fixture
evidence only. It is not a general exact-contact claim.

## Warmup Protocol

Goal2484 defines the repeat protocol used by Goal2485:

```text
default repeats: 7
default warmup rows: 2
reported value: median over the tail rows after warmup removal
```

In short: 7 repeats with 2 warmup rows, then tail medians over the remaining
measured rows.

The required reuse metadata is:

```text
prepared_run_indices
prepared_run_indices_strictly_increase
prepared_scene_reused
prepare_build_seconds_constant
query_input_sequences_reused
native_query_output_buffers_reused
all_measured_runs_match_probe_reference
all_run_signatures_identical
```

Current buffer status:

```text
query_input_sequences_reused: true
native_query_output_buffers_reused: false
```

The current Python ABI reuses the prepared scene and the same Python tuple
inputs, but native query/output buffers are repacked per run. This is explicitly
recorded so performance comparisons can distinguish native traversal from
Python packing.

`prepare_build_seconds_constant` means the prepared handle re-emits the same
cached prepare/build time on each run result. It is a prepared-handle reuse
metadata check, not a claim that rebuilding was repeatedly measured.

## Local Evidence

Focused checks:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
  tests.goal2484_robot_collision_prepared_reuse_test
```

Representative local Embree probe:

```text
dataset: tiny
repeats: 3
warmup: 1
prepared_run_indices: [1, 2, 3]
all_measured_runs_match_probe_reference: true
```

The Goal2484 tests also verify that the CLI emits the prepared probe payload and
that the report records the non-goals.

## Claim Boundary

Goal2484 does not claim:

- paper reproduction;
- authors-code comparison;
- public speedup;
- exact solid contact;
- continuous or swept collision;
- native robot, link, pose, planner, or collision APIs;
- native query/output buffer reuse;
- release/tag action.

## Next Step

Goal2485 uses this prepared repeat protocol to collect the bounded CPU, Embree,
and OptiX performance matrix.
