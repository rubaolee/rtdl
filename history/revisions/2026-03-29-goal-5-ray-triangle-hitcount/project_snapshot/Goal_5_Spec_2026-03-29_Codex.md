# Goal 5 Spec

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-5-ray-triangle-hitcount
Repo: /Users/rl2025/rtdl_python_only
Source Commit: 3df92bb5e83fe4763a9268c45d1cde92bcf73d83

## Goal

Extend RTDL with a new general 2D ray query workload:

- a set of triangles in 2D,
- a set of finite rays in 2D,
- count how many triangles each ray hits.

This should make RTDL capable of expressing a program like:

- generate many random triangles,
- generate rays from a central point using random angle and random finite length,
- compile an RTDL kernel that reports per-ray hit counts.

## Language Surface To Add

- `rt.Triangles`
- `rt.Rays`
- a ray/triangle predicate
- a hit-count workload contract
- emit schema for per-ray counts

## Deliverables

1. RTDL language/runtime surface
   - new geometry types and layouts
   - new predicate
   - lowering/codegen support
   - CPU reference semantics

2. Documentation
   - update language reference and guides
   - add cookbook/example coverage for the new workload

3. Examples
   - canonical example
   - Codex-authored example
   - Gemini-authored example

4. Validation
   - tests for compile/lower/codegen
   - CPU semantic tests
   - example-based tests

## Constraints

- stay within 2D
- keep the current backend as `rayjoin`
- keep the current precision model as `float_approx`
- no claim of GPU runtime execution

## Completion Criteria

- RTDL can express the ray-vs-triangle hit-count workload
- docs describe the feature clearly enough for human and LLM authoring
- Codex-authored and Gemini-authored examples compile and lower successfully
- tests pass
- Codex and Gemini agree Goal 5 is complete
