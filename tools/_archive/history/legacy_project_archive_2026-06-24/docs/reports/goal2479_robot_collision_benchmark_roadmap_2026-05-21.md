# Goal2479 Robot Collision Benchmark Roadmap

Date: 2026-05-21

## Decision Proposal

The next RTDL benchmark-app campaign should be robot collision detection, not RayDB, for this development lane.

Reason: robot collision stresses RTDL in a direction that the current RayJoin, RTNN, Hausdorff/X-HD, and RT-DBSCAN work did not fully cover: dynamic transformed query geometry, batched pose/link checks, compact any-hit flags, prepared static obstacle scenes, and eventually continuous/swept collision. RayDB remains valuable, but it overlaps more with existing database-reduction and RayJoin-style spatial-query work.

The purpose is not to reproduce a full robotics paper immediately. The purpose is to use the app to force useful RTDL language/runtime reconstruction while keeping the native engine app-agnostic.

## Research Anchor

Working paper anchor:

- *Hardware-Accelerated Ray Tracing for Discrete and Continuous Collision
  Detection on GPUs*, ICRA 2025 direction. This citation is tentative; Goal2480
  should confirm the full authorship, venue status, DOI, code, and data
  availability before any paper-facing wording.

Current assumption:

- No official implementation has been verified in this repo yet.
- Until code/data are verified, RTDL should not claim comparison against the authors' implementation, paper reproduction, or paper-level speedups.
- The first campaign should use deterministic synthetic fixtures and clearly separated CPU, Embree, and OptiX evidence.

## Design Boundary

The native engine must not know robotics concepts:

- forbidden native vocabulary: `robot`, `link`, `pose`, `joint`, `kinematics`, `planner`;
- also avoid native `collision` vocabulary unless it appears only in app-facing
  Python/docs; native code should use geometry terms such as `intersection`,
  `overlap`, `hit`, or `any_hit`;
- no robot-specific native ABI;
- no app-specific collision policy inside Embree/OptiX.

Allowed native/runtime concepts:

- static build triangles or BVH geometry;
- transformed query triangles, rays, or conservative proxy primitives;
- batched query groups;
- any-hit flags;
- hit counts when explicitly requested;
- compact per-query output columns;
- prepared/reused build acceleration structures;
- phase timing metadata.

Python owns:

- robot/link model construction;
- pose generation;
- transform matrices;
- fixture labels;
- collision policy;
- per-pose/per-link summaries;
- paper-specific interpretation.

## Goal Sequence

### Goal2479: Robot Collision Benchmark Scoping

Deliver a formal scope document and tests that lock the claim boundary before implementation.

Tasks:

- Confirm paper/code/data status.
- Define the first app scope: static obstacles, simple robot link geometry, batched poses, compact flags.
- Define synthetic fixture families.
- Define CPU reference output contract.
- Define forbidden native vocabulary and app-agnostic runtime vocabulary.

Exit criteria:

- A report records scope, non-goals, and claim boundaries.
- Tests assert that the roadmap and app contract do not authorize paper reproduction or public speedup claims.

### Goal2480: CPU Reference Robot Collision App

Implement the minimum exact/reference app in Python.

Tasks:

- Add a benchmark app under `examples/v2_0/research_benchmarks/robot_collision/`.
- Model static obstacle triangles.
- Model simple link geometry as boxes or triangle meshes.
- Generate deterministic batched poses.
- Return per-pose/per-link collision flags.
- Add exact small-fixture tests.

Exit criteria:

- CPU reference produces deterministic expected labels.
- JSON metadata exposes claim boundaries and output contract.
- No native code is touched.

### Goal2481: Generic RTDL Contract Design

Design the app-agnostic primitive contract needed by robot collision.

Candidate contract shape:

```text
prepared_static_triangles + batched_transformed_query_geometry -> compact any-hit flags
```

Open design question:

- Whether the first RTDL primitive should represent transformed link geometry as transformed triangles, edge rays, bounding-volume proxies, or a two-stage broad/narrow contract.
- Whether compact output should be byte-per-query, bit-packed, or a typed
  partner/native column. Goal2481 should choose this by alignment with existing RTDL
  buffer and tensor conventions, not by robot-link convenience.

Exit criteria:

- Design report chooses the first minimal generic contract.
- Tests check that native code remains free of robot-specific vocabulary.
- The contract is stated in terms reusable by other dynamic transformed-geometry workloads.

### Goal2482: Embree Prototype

Implement the CPU RT prototype for the selected generic contract.

Tasks:

- Prepare static obstacle geometry once.
- Submit transformed query geometry batches.
- Return compact flags.
- Compare against CPU reference fixtures.

Exit criteria:

- Same-contract parity with CPU reference.
- Phase metadata separates prepare, query packing, traversal, and postprocess.
- No robot-specific native ABI.

### Goal2483: OptiX Prototype

Implement the NVIDIA RT prototype for the same generic contract.

Tasks:

- Prepare static obstacle geometry once.
- Use batched query buffers.
- Return compact flags on device or with minimal transfer.
- Validate on pod.

Exit criteria:

- OptiX correctness artifacts exist under `docs/reports/`.
- Pod report records hardware, CUDA/OptiX environment, commands, and claim boundary.
- No public speedup wording.

### Goal2484: Prepared/Reused Execution

Add prepared-session support needed for fair performance measurement.

Tasks:

- Reuse static scene acceleration structure.
- Reuse query/output buffers when possible.
- Run repeated timing probes.
- Record phase-separated timing.

Exit criteria:

- Repeat probe drops first warmup row and reports tail medians.
- Goal2484 must define the warmup protocol before measurement, including the
  number of warmup rows and the metadata used to verify prepared-state reuse.
- Prepared execution has tests for reuse metadata.
- Performance comparison can distinguish native traversal from Python packing.

### Goal2485: Performance Matrix

Collect bounded internal evidence.

Suggested rows:

- CPU reference;
- Embree prepared static scene;
- OptiX prepared static scene;
- optional pure CUDA/partner baseline if needed.

Suggested fixture axes:

- pose count;
- link count;
- obstacle triangle count;
- dense vs sparse collision cases.

Exit criteria:

- Report includes exact commands, hardware, medians, signatures/parity, and phase timings.
- Claims stay internal until external review accepts any wording.

### Goal2486: Continuous Collision Feasibility

Study the continuous/swept collision extension separately.

Candidate directions:

- sampled transforms over time;
- swept spheres/capsules;
- conservative interval/bounds primitive;
- app-level continuation over discrete RTDL queries.

Exit criteria:

- Design-only report unless the primitive is clearly small and generic.
- Explicit decision: implement next, defer to v3, or keep as paper-reproduction-only work.

### Goal2487: Robot Collision Project Closeout

Close the benchmark app after the minimal generic runtime value is proven.

Exit criteria:

- Final report explains what robot collision forced into RTDL.
- External review checks app-agnostic native boundary.
- Performance claims remain bounded unless separately approved.
- Deferred items are explicit.

## Expected RTDL Improvements

If this campaign succeeds, RTDL gains:

- dynamic transformed query geometry support;
- prepared static scene plus changing query batches;
- compact batched any-hit output as a first-class benchmark pattern;
- better phase timing for geometry packing vs native traversal;
- stronger app-agnostic boundary tests for robotics-style workloads;
- a path toward continuous collision only after the discrete contract is solid.

## Non-Goals For The First Pass

- Full ICRA paper reproduction.
- Comparing against authors' code before code/data are verified.
- If authors' code becomes available, any comparison requires a separate
  scoping goal before claims or performance wording.
- Full robotics stack integration.
- Motion planning.
- General-purpose rigid-body simulation.
- Continuous collision implementation before the discrete contract is reviewed.
- Public speedup wording.

## Recommendation

Proceed with Goal2479 and Goal2480 first. Do not start native Embree/OptiX work until the CPU reference app and generic contract design are reviewed.
