# Goal2481 Robot Collision Generic Contract Design

Date: 2026-05-21

## Decision

Goal2481 chooses the first app-agnostic RTDL contract needed by the robot
collision benchmark lane:

```text
PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1
```

Contract shape:

```text
prepared_static_triangle_scene_3d
+ grouped finite 3D query segment probes
-> byte-per-query-group any-hit flags
```

This is not a native robot-collision API. It is a generic prepared-scene
traversal primitive. Python owns application geometry, transforms, grouping,
collision policy, and summary labels.

## Why This Contract

The Goal2479 candidate was:

```text
prepared_static_triangles + batched_transformed_query_geometry -> compact any-hit flags
```

Goal2481 narrows that candidate to grouped finite 3D segment probes for the
first native slice.

Rationale:

- Embree and OptiX directly support ray/segment-style traversal against
  triangle scenes.
- A native exact triangle-triangle or solid-collision Boolean API would import
  application policy into the engine.
- Segment/probe batches are reusable for other transformed-geometry workloads:
  swept samples, finite sensor beams, boundary probes, conservative broad-phase
  tests, and mesh-contact screening.
- The output is a compact flag vector, not row witnesses, so this lane avoids
  `COLLECT_K_BOUNDED` and row-returning semantics.

## 2D vs 3D Decision

Goal2480's CPU reference is intentionally 2D. Goal2481 chooses a 3D native
contract anyway.

Reason:

- The active native targets, Embree and OptiX, are primarily useful here as 3D
  triangle-scene traversal engines.
- A 2D-only native contract would be easier to compare with the current CPU
  reference but would under-specify the benchmark direction.
- A 3D segment/probe contract can still support 2D fixtures by embedding them
  in 3D for tests, while leaving room for realistic 3D query geometry later.

Requirement for Goal2482:

- Before claiming Embree parity for this contract, add a small 3D CPU
  probe-oracle fixture that matches the Goal2481 contract exactly.
- The existing 2D Goal2480 CPU fixture remains an application-level seed, not
  sufficient native-contract parity evidence by itself.

## Contract Signature

The language-level contract is:

```text
prepare_static_triangle_scene_3d(
    static_vertices_xyz,
    static_triangle_indices,
    scene_metadata
) -> prepared_scene

run_grouped_segment_any_hit_flags_3d(
    prepared_scene,
    segment_start_xyz,
    segment_end_xyz,
    segment_group_offsets,
    output_flags_u8
) -> phase_metadata
```

Where:

| Field | Requirement |
| --- | --- |
| `static_vertices_xyz` | Contiguous 3D vertex coordinates supplied by Python. Host side may be float64; backend may narrow to float32 if metadata records it. |
| `static_triangle_indices` | `uint32` triangle index triplets into the static vertex array. |
| `prepared_scene` | Reusable backend handle for static scene acceleration. |
| `segment_start_xyz` / `segment_end_xyz` | Contiguous finite 3D query segment endpoints. Host side may be float64; backend may narrow to float32 if metadata records it. |
| `segment_group_offsets` | `uint32[G + 1]` offsets; segments for group `g` occupy `[offsets[g], offsets[g+1])`. |
| `output_flags_u8` | `uint8[G]`, one byte per query group, values exactly `0` or `1`. |
| `phase_metadata` | At minimum records prepare/build, query-pack/upload, traversal, flag-download/postprocess timing when available. |

The first Python-facing wrapper may return a Python list or NumPy-compatible
array of `0/1` flags, but the native contract is byte-per-query-group.

## Semantics

For each query group:

```text
output_flags_u8[group_id] = 1
    if any finite segment probe in that group intersects any static triangle
output_flags_u8[group_id] = 0
    otherwise
```

Semantics are deliberately minimal:

- Group order is stable and equals the order of `segment_group_offsets`.
- Empty groups are valid and return `0`.
- Empty static scenes are valid and return all `0`.
- Duplicate hits do not matter.
- Backends may terminate traversal after the first hit within a group.
- Non-finite coordinates are invalid.
- Zero-length query segments are invalid for V1 and must be rejected by the
  Python packer before native traversal.
- Degenerate static triangles should be rejected by the Python packer or
  reported as invalid input before native traversal.

## Output Format Decision

Goal2481 chooses byte-per-query-group `uint8` flags for V1.

Rejected for V1:

- bit-packed flags;
- row witness lists;
- pair rows;
- per-segment hit rows;
- app-specific pose/link summary rows.

Reason:

- `uint8` flags are simple for NumPy, Torch, CuPy, C ABI structs, and device
  buffers.
- Byte flags avoid bit unpacking overhead during early correctness work.
- The shape is stable across Embree, OptiX, and partner backends.
- Memory pressure from one byte per group is not the current bottleneck.

Bit-packed output can be reconsidered only after Goal2485 performance evidence
shows flag bandwidth is material.

## App Lowering Boundary

Python owns the robot benchmark semantics:

- loading or constructing robot-like models;
- generating transforms;
- converting transformed query geometry into finite 3D segment probes;
- assigning probe groups;
- interpreting flags as per-pose/per-link summaries;
- any exact fallback, conservative expansion, or paper-specific interpretation.

The native engine sees only:

- static triangles;
- finite query segments;
- group offsets;
- any-hit flags;
- timing and validation metadata.

## Native Vocabulary Boundary

Forbidden vocabulary in active native Embree/OptiX code for this lane:

```text
robot, link, pose, joint, kinematic, kinematics, planner, collision
```

Allowed native vocabulary:

```text
scene, triangle, segment, query, group, probe, intersection, overlap, hit, any_hit, flag
```

Goal2481 broadens the previous ABI-prefix-only scan. Tests now check active
Embree/OptiX native files for those forbidden application words, not only
`rtdl_*robot*` or `rtdl_*collision*` symbols.

## Claim Boundary

Goal2481 does not authorize:

- paper reproduction claims;
- comparison against authors' code;
- public speedup wording;
- exact solid-collision claims;
- continuous or swept collision support;
- native robot, link, pose, kinematic, planner, or collision APIs;
- package-install claims;
- release/tag action.

The paper citation, venue status, DOI, official code, and official data remain
blocked until a later scoping goal verifies them.

## Goal2482 Requirements

Goal2482 may start Embree work only under this contract.

Required Goal2482 deliverables:

- a 3D CPU probe-oracle fixture for the exact Goal2481 segment-group contract;
- at least one full-float64 input fixture to surface backend precision narrowing
  issues for both static scene and query segment coordinates;
- Embree same-contract parity against that fixture;
- reusable prepared static triangle scene metadata;
- `uint8` compact flag output;
- phase timing that separates prepare/build, query packing/upload, traversal,
  and output/postprocess;
- tests proving no forbidden native vocabulary was introduced.

Goal2482 must not add native robot-collision or exact solid-collision APIs.
The Goal2481 tests, external reviews, and consensus artifact must be green
before Goal2482 native work begins.

## Consensus Request

This report is ready for Gemini and Claude review. Review should focus on:

- whether the 3D grouped finite-segment contract is the right first native
  target;
- whether byte-per-query-group `uint8` flags are the right V1 output format;
- whether the app/native boundary is sufficiently strict;
- whether Goal2482 is properly gated before native work starts.
