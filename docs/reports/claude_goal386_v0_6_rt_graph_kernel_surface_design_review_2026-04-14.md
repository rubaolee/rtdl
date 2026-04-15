# Claude Review: Goal 386 v0.6 RT Graph Kernel Surface Design

Date: 2026-04-14
Reviewer: Claude (Sonnet 4.6)
Status: accepted with two flagged items

## Evidence Read

- `docs/goal_386_v0_6_rt_graph_kernel_surface_design.md`
- `docs/reports/goal386_v0_6_rt_graph_kernel_surface_design_2026-04-14.md`
- `docs/reports/gemini_goal386_v0_6_rt_graph_kernel_surface_design_review_2026-04-14.md`
- `docs/reports/goal385_v0_6_rt_graph_version_plan_review_2026-04-14.md`

## Verdict

Goal 386 is accepted.

The design is the correct next dependency for the v0.6 graph line and it keeps
the graph work inside the RTDL kernel model. Two items are flagged below; neither
blocks proceeding, but both should be resolved when lowering is defined.

---

## Is This the Correct Next Dependency?

Yes.

Goal 385 established that v0.6 is an RTDL-kernel graph line and that backend and
lowering work must wait until the kernel surface exists. Goal 386 is that surface.
Without it, any backend work would be building toward an undefined contract, and
any claim that RTDL can express BFS or triangle counting would be unverifiable.

The sequencing is correct: version boundary first (Goal 385), kernel surface next
(Goal 386), lowering and backend work after. Proceeding in any other order would
either produce a design claim with no kernel contract behind it, or produce a
kernel contract that does not align with the paper.

The Gemini review reaches the same conclusion. Agreement across reviewers is
consistent with the design being straightforwardly correct rather than narrowly
defensible.

---

## Does the Design Stay Inside the RTDL Kernel Model?

Yes.

The design extends `input -> traverse -> refine -> emit` to graph workloads
rather than introducing a parallel graph execution path. The additions are:

- new logical input types that slot into the existing role/layout system
- graph-specific traverse modes that extend `rt.traverse(...)`, not replace it
- graph-semantic refine predicates that extend `rt.refine(...)`, not bypass it
- emit fields that match the existing pattern

Graph workloads remain expressed as RTDL kernels. The host/kernel boundaries for
both BFS and triangle count are drawn correctly:

- the BFS level loop, frontier deduplication, visited-state management, and
  termination check are host responsibilities
- the RT-based neighbor expansion is one bounded kernel invocation
- the outer batching and final reduction for triangle count are host
  responsibilities
- the RT-based common-neighbor search is one bounded kernel invocation

This matches the paper's structure. Neither workload has its outer algorithm
loop absorbed into the kernel, which would divorce the design from the paper.

The CSR-to-RT-encoding separation is also correct. Users author against the
logical graph (`rt.GraphCSR`), not against a BVH primitive stream. The
acceleration structure is a compilation target, not an authoring surface. That
keeps the design honest about what the RT hardware is doing without requiring
users to think in geometry.

---

## Strengths

1. The host/kernel boundaries for BFS and triangle count are explicitly stated and
   paper-aligned. This is the hardest part to get right, and the design gets it
   right.

2. The non-goals section is complete. It excludes primitive geometry details,
   lowering, backend API calls, performance claims, and syntax stability beyond
   the two initial workloads. A design that over-claims in those areas would be
   dishonest; this one does not.

3. The logical graph types (`rt.GraphCSR`, `rt.VertexFrontier`, `rt.VertexSet`,
   `rt.EdgeSet`) are the right level of abstraction. They are graph concepts, not
   RT encoding artifacts.

4. The design is bounded to two workloads. Extending to additional graph workloads
   before the kernel surface for BFS and triangle count is validated would be
   premature. The scope here is appropriate.

---

## Flagged Items

### 1. `precision="float_approx"` on graph kernels

Both the BFS and triangle-count kernel examples carry:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
```

`float_approx` is a geometry-inherited annotation. Graph traversal is exact: a
vertex is either in the frontier or it is not; a triangle either exists or it
does not. Carrying `float_approx` forward uncritically into graph kernels
conflates two different execution semantics.

This does not block the design, because the kernel examples are design-form only
and the precision annotation will be interpreted when lowering is defined. But
the issue should be resolved before any lowering work is written. Options:

- introduce `precision="exact"` for graph kernels
- drop the precision annotation for graph kernels if it is not meaningful at
  this level
- document explicitly that `float_approx` has no semantic effect in the graph
  line and is carried only for kernel decorator uniformity

Leaving it undefined risks a future lowering step interpreting `float_approx` as
permission to introduce approximation where graph algorithms require exactness.

### 2. `accel="bvh"` in graph traverse calls

Both kernel examples use `accel="bvh"` explicitly:

```python
rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
```

The design report correctly notes that the execution target is a "BVH or
equivalent RT acceleration structure." But if the acceleration structure for
graph workloads may not be a BVH in the geometric sense, hard-coding `accel="bvh"`
in the kernel surface is premature.

This is not a blocking issue at design stage, because the exact primitive
encoding is explicitly out of scope for this goal. But before the first graph
kernel lowering goal opens, the design should decide whether `accel="bvh"` is a
stable surface identifier (meaning the implementation commits to BVH encoding for
graphs) or whether it should be `accel="rt_graph"` or similar to leave encoding
flexibility to the compiler.

---

## Paper Alignment

The design is paper-consistent. The SIGMETRICS 2025 claim is that BFS and
triangle counting can be recast as RT traversal workloads under the RTDL model.
This design enforces that claim at the kernel authoring level:

- users do not write a graph library call
- users write an RTDL kernel that declares graph inputs and drives traversal
  through `rt.traverse` and `rt.refine`
- the RT hardware accelerates the traversal step; the algorithm loop stays
  host-side

Nothing in this design allows a graph workload to bypass the RT traversal path
and still call itself RTDL. That enforcement is what the paper requires.

---

## What Must Follow

The two flagged items above need resolution before any lowering goal opens. No
other blockers were found in the design.

The correct next goals after Goal 386 closes are:

- define the RT primitive encoding for graph CSR (the non-goal explicitly
  deferred here)
- define the lowering path from `rt.GraphCSR` and `rt.traverse(..., mode="graph_*")`
  to backend-specific calls
- keep the backend work downstream of those two definitions
