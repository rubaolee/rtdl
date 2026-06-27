# Goal 7 Spec

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-7-embree-backend
Repo: /Users/rl2025/rtdl_python_only
Baseline Commit: 4e2be7f1aa72a42f609e6045396bef47071441e8

## Goal

Add an Embree backend/runtime path so the currently supported RTDL workloads can
run on top of Embree on this Mac, not just through the pure Python simulator.

## In Scope

- use Embree as a real runtime backend on macOS
- support the currently implemented RTDL workload surface:
  - `lsi`
  - `pip`
  - `overlay`
  - `ray_tri_hitcount`
- keep the current Python DSL authoring model
- keep the current CPU simulator as the correctness baseline
- make RTDL programs runnable through an Embree-backed execution path
- add tests, docs, and demos for the Embree backend

## Out of Scope

- GPU execution
- new workloads
- robust/exact precision beyond `float_approx`
- performance tuning beyond functional runtime viability
- replacing the existing simulator

## Proposed Direction

Add a second local runtime path alongside the simulator:

- `rt.run_cpu(...)` remains the pure Python reference executor
- `rt.run_embree(...)` becomes the native accelerated executor on this Mac

The Embree backend should:

1. compile the RTDL kernel
2. validate supported workload constraints
3. normalize Python-side input records
4. build Embree scenes / geometry for the supported workload
5. run the workload using Embree intersection queries
6. materialize output rows matching the kernel `emit` schema

## Environment Reality

Embree does not appear to be installed on this machine yet. Goal 7 therefore
includes:

- selecting a usable local Embree integration strategy
- installing or linking Embree
- wiring RTDL against that local runtime

## Success Criteria

- Embree is available in the local development environment
- RTDL can run all four current workloads through an Embree-backed path
- results are checked against `rt.run_cpu(...)` on representative cases
- tests cover both happy paths and backend/setup failures
- docs explain when to use simulator mode vs Embree mode
