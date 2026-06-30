# Goal2482 Robot Collision Embree Contract Prototype

Date: 2026-05-21

## Decision

Goal2482 implements the first Embree prototype for the Goal2481 contract:

```text
PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1
```

Contract shape:

```text
prepared static 3D triangle scene
+ grouped finite 3D segment probes
-> byte-per-query-group `uint8` flags
```

This remains a generic RTDL primitive path, not a native robot-collision API.
Python owns benchmark geometry generation, transforms, grouping, interpretation,
and any exact or paper-specific fallback.

## Implemented Surface

Native Embree exports added:

```text
rtdl_embree_static_triangle_scene_3d_create
rtdl_embree_static_triangle_scene_3d_grouped_segment_any_hit_flags
rtdl_embree_static_triangle_scene_3d_destroy
```

Python API added:

```text
PreparedEmbreeStaticTriangleScene3D
prepare_embree_static_triangle_scene_3d
run_embree_grouped_segment_any_hit_flags_3d
```

The Python wrapper validates the contract before native traversal:

- static input must be 3D triangles;
- static triangle coordinates must be finite;
- static triangles must have non-zero area;
- segment endpoint coordinates must be finite;
- zero-length query segments are rejected before native traversal;
- group offsets must start at zero, be monotonic, fit `uint32`, and end at the
  segment count;
- output flags are returned as one Python integer per `uint8` group flag.

## Correctness Evidence

Goal2482 adds a full 3D CPU probe oracle fixture, separate from the 2D Goal2480
application seed. The fixture includes full-float64 input coordinates and locks
the expected flags:

```text
flags = [1, 0, 1, 0, 1]
```

The Embree result matches the 3D CPU oracle under the same contract:

```text
backend: embree
contract: PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1
flag_format: uint8_byte_per_query_group
segment_count: 5
group_count: 5
triangle_count: 1
prepared_reused: true
```

Representative local run metadata:

```text
prepare_build:      0.00021729199988840264 s
query_pack:         0.00012429199978214456 s
traversal:          0.000002041 s
output_postprocess: 0.000003208000180165982 s
```

The exact timings above are smoke-fixture timings only. They are not performance
claims.

## Prepared Reuse

This section records prepared scene reuse evidence.

The native handle owns the prepared Embree scene. Repeated Python calls reuse the
same handle and only repack query segments and offsets. The test verifies the
first and second runs return identical flags and report increasing
`prepared_run_index` values:

```text
first prepared_run_index:  1
second prepared_run_index: 2
```

## Precision Metadata

The Python result records the current precision boundary:

```text
host_input: float64
embree_bvh_bounds: float32
native_intersection_callback: float64
coordinate_narrowing_recorded: true
```

This satisfies the Goal2481 requirement to record backend coordinate narrowing.

## Native App-Agnostic Boundary

Goal2482 does not add application vocabulary to active native Embree/OptiX code.
The native interface uses only generic scene, triangle, segment, group, hit, and
flag concepts.

Native vocabulary scan:

```text
rg -n "\b(robot|collision|link|pose|joint|kinematic|kinematics|planner)\b" \
  src/native/embree src/native/optix
```

Result:

```text
no matches
```

## Validation Commands

Local Embree version:

```text
embree_version (4, 4, 1)
```

Compile check:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m py_compile \
  src/rtdsl/embree_runtime.py \
  src/rtdsl/__init__.py \
  tests/goal2482_robot_collision_embree_contract_test.py
```

Implementation-facing Goal2482 tests:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
  tests.goal2482_robot_collision_embree_contract_test.Goal2482RobotCollisionEmbreeContractTest.test_cpu_oracle_fixture_locks_goal2481_contract \
  tests.goal2482_robot_collision_embree_contract_test.Goal2482RobotCollisionEmbreeContractTest.test_embree_matches_3d_cpu_oracle_and_returns_contract_metadata \
  tests.goal2482_robot_collision_embree_contract_test.Goal2482RobotCollisionEmbreeContractTest.test_prepared_embree_scene_reuses_handle_across_runs \
  tests.goal2482_robot_collision_embree_contract_test.Goal2482RobotCollisionEmbreeContractTest.test_python_packer_rejects_invalid_segments_before_native_traversal \
  tests.goal2482_robot_collision_embree_contract_test.Goal2482RobotCollisionEmbreeContractTest.test_active_native_targets_remain_free_of_app_vocabulary
```

Result:

```text
Ran 5 tests in 4.047s
OK
```

No pod was used. Goal2482 is local Embree evidence only; OptiX parity and NVIDIA
timing remain future work.

## Claim Boundary

Goal2482 does not claim:

- paper reproduction;
- comparison against authors' implementation;
- public speedup;
- native robot, link, pose, planner, or collision API support;
- exact solid contact;
- continuous or swept support;
- row witnesses;
- OptiX parity;
- release/tag action.

## Files

Implementation:

- `src/native/embree/rtdl_embree_prelude.h`
- `src/native/embree/rtdl_embree_api.cpp`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/__init__.py`

Evidence:

- `tests/goal2482_robot_collision_embree_contract_test.py`
