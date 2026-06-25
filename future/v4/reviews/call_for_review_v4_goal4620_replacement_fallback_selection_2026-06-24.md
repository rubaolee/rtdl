# Call For Review: `goal4620` Replacement Fallback Selection

Date: 2026-06-24
Author: Codex
Status: candidate-selection request for Claude review before implementation

This document is the required `goal4620` fallback-selection gate after:

- `goal4619` returned No-Go for a honest 3D fixed-radius Python GPU-array
  surface.
- Claude rejected the aggregate-tree fallback in
  `future/v4/reviews/claude_v4_goal4620_aggregate_tree_feasibility_protocol_review_2026-06-24.raw.md`
  with verdict `reject_aggregate_tree_candidate_choose_different_fallback`.

No implementation is authorized by this document. Codex must wait for Claude
review before implementing any `goal4620` replacement candidate.

## Continuous Goal Numbering

The project goal sequence remains:

- `goal4615` - freeze V4 forward goals and get Claude consensus
- `goal4616` - consolidate current V4 state and review debt
- `goal4617` - grouped-i64 promotion decision and measured-surface promotion
- `goal4618` - point-group nearest-witness promotion decision and measured
  surface promotion
- `goal4619` - 3D fixed-radius feasibility gate, completed as No-Go
- `goal4620` - implement one new Tier-2 surface only after reviewed fallback
  selection
- `goal4621` - Tier-2 catalog hardening
- `goal4622` - Tier-3 spike protocol, not implementation
- `goal4623` - V4 release-candidate decision packet

This packet does **not** create `goal4624`. It only asks which replacement
candidate, if any, is valid for `goal4620` after aggregate-tree was rejected.

## Current Ground Truth

Already promoted measured surfaces:

- `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
  (`goal4617`)
- `v4_point_group_nearest_witness_2d_device_arrays` (`goal4618`)

These two may be referenced as evidence that the V4 path can work, but they
must not be counted as the new `goal4620` implementation.

Rejected or deferred candidates:

- 3D fixed-radius count-threshold: No-Go under `goal4619` because the current
  route is not a full caller-owned query device-column V4 surface.
- Aggregate-tree weighted-vector sum: rejected by Claude because the kernel is
  Barnes-Hut / N-body gravity and CUDA-only, not a generic RT-core Tier-2
  operator.

V4.0 scope remains the Python GPU-array RT-core lane. It must not reopen the
old C ABI / embedding / multi-language host plan. It must not expose raw OptiX
callbacks, add app-identity kernels, or claim true zero-copy without separate
authorization.

## Goal-Level Decision Audit

1. Am I being foolish by writing a replacement selection packet instead of
   coding immediately?
   No. Claude explicitly required fallback candidate review before `goal4620`
   implementation after `goal4619` No-Go.
2. What action would make this foolish?
   Reusing `goal4617` or `goal4618` as fake new `goal4620` progress, or
   implementing a new surface before Claude accepts a replacement candidate.
3. Is there another path that avoids getting stuck in process?
   Yes. This packet should decide one candidate. If Claude rejects it, the
   next action is either a narrowly amended candidate list or `goal4620`
   No-Go, not another broad architecture essay.
4. Can I solve the problem differently?
   Yes. If no candidate passes the gate, record `goal4620` No-Go and continue
   to `goal4621` catalog hardening with the two newly promoted surfaces.

## Candidate Matrix

| Candidate | Status | Why |
|---|---|---|
| A. `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` | **Recommended** | Generic any-hit weighted sum over ray/triangle traversal. Native path is RT-core-backed (`optixLaunch` / `optixTrace`), accepts prepared device ray batch and caller-owned device weights, and already has a device-output graph-executor ABI that writes the scalar sum to caller-owned device memory. Not app-named and not a force law. |
| B. `v4_ray_triangle_hit_count_sum_3d_device_arrays` | Backup / defer | Generic count-sum operator and RT-core-backed, but current Python path returns scalar to Python; a device-output graph-executor variant is not yet visible. We should not prefer it over A unless Claude rejects weighted sum. |
| C. Closed-shape membership point-id/count | Defer | RT-core-backed and generic relation-like family, but the visible Python/native path still uses host point inputs or RTDL-owned prepared point state. Not a clean caller-owned GPU-array V4 front door today. |
| D. Shape-pair relation active device columns | Defer | RT-core-backed, but visible API accepts host-side left polygon structures and geometry packing. This risks repeating the `goal4619` host-query mistake. |
| E. Segment-pair left-id count | Defer | RT-core-backed, but visible API accepts host-side left segments and is close to RayJoin-specific relation work. Not the cleanest V4 Tier-2 proof target. |

## Recommended `goal4620` Candidate

Codex recommends selecting:

`v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`

The intended user-level contract:

- Inputs:
  - triangle scene columns, prepared once
  - caller-owned Torch CUDA ray columns, prepared as a ray batch
  - caller-owned Torch CUDA `uint64` ray weights
  - caller-owned or RTDL-allocated Torch CUDA `uint64[1]` output scalar
- Operation:
  - For each ray, run ray/triangle any-hit traversal.
  - If a ray hits any triangle, add that ray's weight to the output scalar.
  - Write the weighted hit sum to device memory, not to Python, on the hot
    executor path.
- Output:
  - device `uint64[1]` weighted-hit sum plus metadata.

This is a generic continuation operator: any-hit + weighted sum. It is not an
application identity kernel.

## Existing Evidence For Candidate A

Python/runtime hooks already exist below the V4 front door:

- `PreparedOptixStaticTriangleScene3D.ray_any_hit_weighted_sum_device_columns`
  accepts partner-owned ray columns and partner-owned ray weights, but returns
  the scalar to Python.
- `PreparedOptixStaticTriangleScene3D.ray_batch_any_hit_weighted_sum_device_weights`
  accepts a prepared device ray batch and partner-owned device weights, but
  returns the scalar to Python.
- `PreparedOptixStaticTriangleScene3D.prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor`
  prepares a stream-launchable executor that writes the weighted sum to device
  memory and records:
  - `device_output_used: True`
  - `host_scalar_read_before_consumer: False`
  - `host_row_materialization_before_consumer: False`
  - `query_rays_uploaded_each_run: False`
  - `ray_weights_uploaded_each_run: False`
  - `true_zero_copy_authorized: False`

Native symbols already visible in source:

- `rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights`
- `rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights_prepare_graph_executor`
- `rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights_launch_graph_executor_on_stream`
- `rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights_release_graph_executor`

Native source shows this path uses OptiX ray traversal with prepared rays and
device weights, not a CUDA-only kernel relabeled as Tier-2.

Existing historical scripts/tests:

- `scripts/goal4531_m134_triangle_weighted_replay_graph_capture.py`
- `scripts/goal4539_m140_triangle_capture_mode_audit.py`
- `tests/goal4474_v3_0_m78_triangle_prepared_ray_batch_weighted_sum_test.py`
- `tests/goal4531_v3_0_m134_triangle_weighted_replay_graph_capture_test.py`

These are not V4 user-facing surfaces yet. They are only evidence that the
lower-level route exists.

## Proposed `goal4620` Implementation If Claude Accepts

Add a V4 front-door candidate surface:

- surface name:
  `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
- module:
  `src/rtdsl/v4_ray_triangle.py`
- catalog status:
  `candidate`, not measured, until a separate promotion review
- partner scope:
  Torch CUDA only for this goal; CuPy declared-unmeasured or absent
- OptiX scope:
  OptiX 8.0 / RTX A5000 evidence only unless separately validated

Implementation tasks:

1. Add claim-boundary metadata for the new surface.
2. Add a session wrapper around the existing prepared ray-batch weighted-sum
   device-output graph executor.
3. Add an allocator/helper for a `uint64[1]` device output scalar.
4. Add a small user-visible example only if it can run directly.
5. Add local tests that validate API shape, claim boundaries, and non-release
   wording.
6. Add POD validation script with correctness parity and same-contract
   comparison against the existing host-scalar weighted-sum route.

POD gate:

- Hardware: the current RTX A5000 POD.
- Sizes: at least two non-toy ray counts from the V4 candidate scale
  convention, proposed `32768` and `131072`.
- Correctness: device scalar after synchronization must equal the expected
  weighted hit sum and the existing host-scalar route.
- Evidence: JSON + short Markdown summary under `future/v4/evidence/`.
- Required metadata:
  - `runtime_executed: true`
  - `optix_launch_used: true`
  - `device_output_used: true`
  - `host_scalar_read_before_consumer: false`
  - `host_row_materialization_before_consumer: false`
  - `query_rays_uploaded_each_run: false`
  - `ray_weights_uploaded_each_run: false`
  - `true_zero_copy_authorized: false`
  - `public_speedup_claim_authorized: false`

Completion gate for `goal4620`:

- Claude accepts candidate selection before implementation.
- Implementation and evidence exist.
- Completion packet receives 3-AI consensus, or missing seats are recorded as
  explicit review debt.
- The candidate remains candidate unless a separate promotion review authorizes
  measured-catalog status.

## Why Not Use The Subagent's Top Candidate

The read-only subagent Halley recommended
`v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` as the
strongest candidate. That recommendation is technically accurate for V4
strength, but unusable for `goal4620` because it is already the completed
`goal4617` promotion. Reusing it as `goal4620` would be double-counting.

## Reviewer Questions For Claude

1. Do you accept Candidate A,
   `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`, as the replacement
   fallback candidate for `goal4620`?
2. Is its lower family breadth acceptable given that the stricter audit
   rejected aggregate-tree and 3D fixed-radius?
3. Is the existing device-output graph executor strong enough to support a V4
   candidate surface, provided the V4 front door preserves candidate status and
   no true-zero-copy wording?
4. Should `ray_hit_count_sum_3d_device_arrays` be implemented as a backup in
   the same goal, or deferred to avoid scope creep?
5. Are closed-shape membership, shape-pair relation, and segment-pair relation
   correctly deferred because their current front doors are not clean
   caller-owned device-array surfaces?
6. If you reject Candidate A, should Codex record `goal4620` No-Go and move to
   `goal4621`, or attempt one more candidate-selection packet?

## Non-Authorization

This packet does not authorize:

- `goal4620` implementation before Claude review
- measured-catalog promotion
- V4 release
- whole-app or broad V4 speedup wording
- true-zero-copy wording
- OptiX 9.1 scope
- CuPy performance claims
- Tier-3 callback work
- C ABI / embedding / non-Python-host work
- app-specific native kernels

