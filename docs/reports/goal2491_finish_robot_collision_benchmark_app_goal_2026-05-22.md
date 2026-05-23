# Goal2491: Finish the Robot-Collision Benchmark App

Date: 2026-05-22

## Goal

Finish the robot-collision benchmark app as a bounded RTDL benchmark: correct,
documented, repeatable, app-agnostic at the native-engine boundary, and backed
by exact internal evidence for the implemented Embree and OptiX paths.

This goal should close the benchmark app itself. Any remaining work that would
change the research problem materially should be deferred into a later project,
not hidden inside this closeout.

## Current State

The benchmark has already produced the main RTDL design/runtime improvements it
was meant to force:

- deterministic Python CPU reference for sampled discrete robot feasibility;
- generic grouped finite 3D segment query contract;
- Embree prepared static triangle scene path;
- OptiX prepared static triangle scene path;
- prepared host query/output buffer reuse;
- OptiX native device-resident grouped segment query buffers;
- OptiX count-only screening result mode;
- phase-separated timing for app lowering, query packing, traversal, and output
  postprocess;
- native vocabulary guards to keep robot/link/pose/collision semantics out of
  active native engine files.

## Finish Scope

Goal2491 should complete these concrete items:

- Clean the benchmark CLI and mode documentation so each mode has a precise
  purpose and claim boundary.
- Produce one final benchmark matrix covering the canonical supported modes:
  `cpu_reference`, `embree_prepared`, `embree_prepared_buffers`,
  `optix_prepared`, `optix_prepared_buffers`,
  `optix_prepared_device_buffers`, and `optix_prepared_device_count`.
- Record same-contract correctness for all measured modes against the sampled
  probe reference.
- Record final exact internal performance evidence, with environment details,
  repeats, warmup, dataset shape, and pod command where applicable.
- Add or update tests that ensure the app modes remain exposed, metadata remains
  honest, and native OptiX/Embree files remain app-vocabulary-free.
- Write a final closeout report explaining what the benchmark app contributed
  to RTDL language/runtime design and what is intentionally deferred.

## Non-Goals

Goal2491 must not expand the benchmark into a new robotics project:

- no continuous or swept-volume collision support;
- no exact solid-contact collision claim;
- no paper reproduction claim;
- no authors-code comparison claim unless official code and data are separately
  scoped and verified;
- no public speedup claim without the required review and wording gate;
- no true zero-copy claim;
- no new robot-specific native ABI;
- no Vulkan, HIPRT, Apple RT, or packaging/release work.

## Definition of Done

The benchmark app is finished when all of the following are true:

- The final report states the supported contract: sampled discrete feasibility
  via grouped finite 3D segment probes against static triangle obstacles.
- The final report states the unsupported contract: no continuous collision, no
  exact solid-contact result, no paper reproduction, no authors-code comparison.
- The final matrix includes correctness and timing rows for the canonical
  modes, or explicitly marks unavailable rows as skipped with a reason.
- The OptiX rows are backed by pod evidence when NVIDIA timing is claimed.
- The Embree rows are backed by local or Linux evidence and use the same
  sampled probe contract.
- Native engine files contain no robot/link/pose/collision/planner vocabulary.
- Tests cover the closeout report, mode exposure, metadata boundaries, and
  native vocabulary guard.
- The final conclusion is phrased as internal exact-subpath evidence only unless
  separate public-claim consensus is completed.

## Expected Final Conclusion

The expected conclusion is that robot collision is valuable as a benchmark app
because it exposed repeated-query overheads that prior apps did not stress
enough. The app pushed RTDL from prepared-scene reuse toward prepared query
reuse, device-resident query buffers, and scalar result consumption.

The expected engineering conclusion is not that RTDL solves general robot
collision. The correct claim is narrower: RTDL now has reusable generic
primitives for static triangle scenes plus grouped finite segment any-hit
queries, with Embree and OptiX implementations and measured internal evidence
for sampled feasibility screening.

## Deferred After Finish

After Goal2491 closes the benchmark app, future work should become separate
projects:

- true device-side scalar reduction for count-only results;
- partner/device-column handoff for zero-copy-style pipelines;
- continuous/swept collision as a separately reviewed v3.0-or-later candidate;
- a RayDB or other benchmark app to force different language/runtime pressure.

## Consensus Requirement

Goal2491 is a closeout and claim-boundary goal. It should receive at least
2-AI consensus before being treated as finished. If the closeout introduces any
public wording, release wording, or broad performance claim, require 3-AI
consensus.
