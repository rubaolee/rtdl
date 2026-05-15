# Goal 461: v0.7 DB App Demo

Date: 2026-04-16

## Purpose

Add an app-facing demo that shows how the v0.7 bounded DB workload features are
used by application code.

## Scope

The demo must show:

- application-owned denormalized rows
- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`
- portable CPU-reference execution
- prepared RT dataset execution for available Embree, OptiX, or Vulkan backends
- explicit honesty boundary that this is not a DBMS or arbitrary SQL engine

## Acceptance Criteria

- A runnable example is added under `examples/`.
- A focused unit test checks the CPU-reference app output.
- Local execution verifies the `auto` backend path on the available host.
- The examples index points users to the app-level demo.
- Goal 461 receives 2-AI consensus before closure.
