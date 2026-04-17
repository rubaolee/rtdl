## Goal 415: v0.7 RT DB Execution Interpretation

Date: 2026-04-15
Status: active

### Purpose

Define what RTDL's new database-style kernels mean operationally before any
Embree, OptiX, or Vulkan implementation claims are made.

### Why this goal exists

The current `v0.7` DB surface is closed only at:

- Python truth
- native/oracle CPU
- PostgreSQL correctness

Those are semantic/correctness engines, not RT engines. Before implementing RT
backends, RTDL needs an explicit execution interpretation for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

### Required outputs

1. A report that defines:
   - what `DenormTable`, `PredicateSet`, and `GroupedQuery` mean at execution time
   - what `build`, `probe`, `traverse`, `refine`, and `emit` mean for the DB family
   - which work belongs to RT traversal and which work remains bounded host-side logic
2. An explicit honesty boundary that distinguishes:
   - semantic engines
   - RT engines
3. A bounded support matrix for the first RT backend wave.

### Acceptance criteria

- The report must make clear that current Python/native/PostgreSQL paths are not
  ray-tracing implementations.
- The report must define a bounded RT-friendly execution interpretation that can
  be shared by Embree, OptiX, and Vulkan.
- The report must keep RTDL positioned as a workload language/runtime, not a DBMS.
- Closure requires 2+ AI consensus.
