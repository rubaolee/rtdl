# Claude Review: Goal 197 Fixed-Radius Neighbors DSL Surface

Date: 2026-04-10
Reviewer: Claude (Sonnet 4.6)

## Verdict

Pass. Goal 197 is correctly bounded, the lowering rejection is honest and explicit, and the docs describe the new surface without overstating support.

## Findings

**Scope discipline**: The implementation is confined entirely to the DSL/Python layer. `api.py:156-164` adds `fixed_radius_neighbors(*, radius: float, k_max: int)` which validates its arguments and returns a `Predicate` node. No lowering logic, no backend paths, no runtime hooks were added. The function fits the same structural pattern as the other predicates (`segment_intersection`, `point_in_polygon`, etc.) and introduces no new mechanisms.

**Lowering rejection**: `lowering.py:77-81` handles `fixed_radius_neighbors` with an explicit `raise ValueError` before the catch-all unsupported-predicate error. The message names the workload, the version boundary (`v0.4`), and the exact scope of the goal ("Goal 197 adds the DSL/Python contract only, not lowering yet"). There is no silent fallthrough, no stub path, and no accidental delegation to a generic error. The rejection is intentional and self-documenting.

**Docs honesty**: Per the completion report, all three docs (`llm_authoring_guide.md`, `dsl_reference.md`, `workload_cookbook.md`) were updated to mention the new predicate while keeping the implemented-versus-planned boundary explicit. The report itself accurately describes what changed and what was deliberately excluded, including a clear acceptance summary that lists lowering/runtime support as "intentionally no."

**Tests**: 104 tests pass, covering the new API surface and the lowering rejection. No gaps were identified in the test scope relative to the goal's required results.

## Summary

Goal 197 did exactly what it said it would do and nothing more. The API surface exists, the package export exists, kernels compile, lowering fails loudly with a clear planned-surface message, and the docs reflect the boundary honestly. The goal is complete and correctly scoped.
