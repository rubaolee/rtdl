# Goal 462: v0.7 DB Kernel App Demo

Date: 2026-04-16

## Purpose

Add a kernel-form app demo that shows how application DB-style workloads are
written as RTDL kernels before runtime lowering chooses CPU, Embree, OptiX, or
Vulkan execution.

## Scope

The demo must show:

- `rt.input(..., role="probe")` for predicates or grouped queries
- `rt.input(..., role="build")` for application-owned rows
- `rt.traverse(..., accel="bvh")` for candidate discovery
- `rt.refine(...)` for exact scan or aggregation semantics
- `rt.emit(...)` for application-ready result rows
- one-, two-, and three-predicate conjunctive scan examples
- grouped count and grouped sum examples
- portable CPU Python reference execution
- optional native backend execution through `cpu`, `embree`, `optix`, or
  `vulkan`
- explicit honesty boundary that this is not SQL, joins, transactions, or a
  DBMS

## Acceptance Criteria

- A runnable kernel-form app example is added under `examples/`.
- A focused unit test checks the CPU Python reference output.
- Local execution verifies both portable JSON output and `auto` backend
  behavior on the available host.
- The examples index points users to the kernel-form app demo.
- Goal 462 receives 2-AI consensus before closure.
