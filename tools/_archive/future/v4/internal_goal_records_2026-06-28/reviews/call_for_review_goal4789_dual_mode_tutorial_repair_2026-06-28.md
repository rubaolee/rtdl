# Call For Review: Goal4789 Dual-Mode Tutorial Repair

Date: 2026-06-28

## Review Request

Please critically review the tutorial repair now required for the V4 public
teaching surface.

The user correctly identified a structural flaw in the current tutorial
direction: several lessons teach `rtdl_v4.plan_operator_request_v4(...)` as the
main programming move. That is wrong. The V4 operator/runtime API is an
execution and planning surface, not the primary RTDL language model.

## Correct Model

Each tutorial program must teach two layers in this order:

1. **RTDL kernel mode first**
   - Show how the user problem becomes RTDL relations.
   - Identify probe inputs, build inputs, traversal, refinement predicate,
     emitted rows, and continuation.
   - Prefer real `@rt.kernel` code where the public kernel API supports the
     concept.

2. **V4 operator/runtime mode second**
   - Show how the same recognized relation can be planned or executed through a
     V4 operator surface.
   - Keep `plan_operator_request_v4(...)` as an advanced route/planning check,
     not as the beginner-facing programming model.

The desired ladder is:

```text
RTDL kernel thinking
-> RTDL kernel code or honest kernel-shaped model
-> output row reasoning
-> V4 operator/runtime mapping
```

## Scope Of This Repair

This repair supersedes the earlier approval of the Goal4788 foundation batch.
It targets the current foundation lessons first because all later tutorial
programs depend on them:

- `tutorials/current/04_relations_and_operators.md`
- `tutorials/current/05_fixed_radius_neighbors.md`
- `tutorials/current/06_nearest_witness.md`
- `tutorials/current/07_aabb_predicates.md`
- `examples/tutorial_programs/fixed_radius_neighbors.py`
- `examples/tutorial_programs/nearest_neighbor.py`
- `examples/tutorial_programs/aabb_spatial_index_predicates.py`

## Required Fixes

1. Fixed-radius must show the actual old/correct RTDL kernel shape:

   ```python
   @rt.kernel(backend="rtdl", precision="float_approx")
   def fixed_radius_neighbors_kernel():
       query_points = rt.input("query_points", rt.Points, role="probe")
       search_points = rt.input("search_points", rt.Points, role="build")
       candidates = rt.traverse(query_points, search_points, accel="bvh")
       hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(...))
       return rt.emit(hits, fields=[...])
   ```

2. Nearest witness must show candidate distance rows plus an argmin/top-k
   continuation before any V4 route planning call.

3. AABB must not fake a nonexistent public kernel predicate. If the public
   kernel API lacks a direct AABB predicate, the tutorial must say so and show
   the closest honest kernel-shaped relation before mapping to the V4 prepared
   AABB surface.

4. Every repaired program should expose two modes where possible:

   ```bash
   python examples/tutorial_programs/<name>.py --mode kernel
   python examples/tutorial_programs/<name>.py --mode v4
   python examples/tutorial_programs/<name>.py --mode both
   ```

   If the kernel API is missing for a concept, the program must report that
   honestly instead of inventing a fake kernel route.

5. Documentation must not teach V4 operator API first.

## Questions For Reviewer

1. Does the repair correctly demote `plan_operator_request_v4(...)` from
   beginner programming model to V4 execution/planning surface?
2. Do the repaired files teach RTDL kernel thinking before V4 operator API?
3. Does fixed-radius preserve the historical v2.x/v2.14 kernel model rather
   than replacing it with a planner call?
4. Does nearest witness teach candidate rows and argmin/top-k continuation?
5. Is the AABB limitation handled honestly, without inventing unsupported
   kernel API?
6. Are the examples runnable and educational rather than JSON dumps with
   release jargon?
7. Do you authorize continuing the tutorial cleanup after this repair?

## Non-Authorization

This review does not authorize a release tag, public performance claims, broad
V4 speedup claims, Tier-3 callback claims, raw OptiX callback claims, or any
benchmark/paper-reproduction claim. It only reviews whether the tutorial
teaching model has been repaired.
