## Goal 416: v0.7 RT DB Lowering Runtime Contract

Date: 2026-04-15
Status: active

### Purpose

Define the concrete lowering contract that maps the first `v0.7`
database-style kernels into bounded RT jobs for Embree, OptiX, and Vulkan.

### Why this goal exists

The DB kernel surface now exists, but no backend can be implemented honestly
until RTDL defines:

- how denormalized rows become RT primitives
- how predicates become RT query regions and rays
- how grouped kernels use RT traversal without pretending to be a full DBMS
- how over-boundary cases are decomposed or rejected

### Required outputs

1. A report that defines:
   - primary RT layouts for scan and grouped kernels
   - predicate grouping/decomposition rules
   - refine rules
   - backend-neutral primitive/payload expectations
2. Explicit first-wave support limits for:
   - number of scan clauses
   - number of group keys
   - aggregate kinds
3. A backend implementation order for:
   - Embree
   - OptiX
   - Vulkan

### Acceptance criteria

- The lowering must be implementable on all three RT backends without changing
  RTDL language semantics.
- It must remain bounded and honest about unsupported cases.
- It must state how PostgreSQL remains the cross-engine correctness anchor.
- Closure requires 2+ AI consensus.
