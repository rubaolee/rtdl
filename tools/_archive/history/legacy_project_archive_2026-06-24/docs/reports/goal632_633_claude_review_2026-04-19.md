# Goal632/633 v0.9.5 Any-Hit and Visibility Rows — Claude Review

Date: 2026-04-19
Reviewer: Claude Sonnet 4.6
Verdict: **ACCEPT**

## Scope

Reviewed all artifacts requested in the handoff:
- `docs/reports/goal631_v0_9_5_anyhit_visibility_goal_ladder_2026-04-19.md`
- `docs/reports/goal632_v0_9_5_ray_triangle_any_hit_2026-04-19.md`
- `docs/reports/goal633_v0_9_5_visibility_rows_standard_library_2026-04-19.md`
- `src/rtdsl/api.py`, `reference.py`, `runtime.py`, `oracle_runtime.py`, `lowering.py`, `__init__.py`
- `tests/goal632_ray_triangle_any_hit_test.py`, `tests/goal633_visibility_rows_test.py`
- `examples/rtdl_ray_triangle_any_hit.py`, `examples/rtdl_visibility_rows.py`
- `docs/features/ray_tri_anyhit/README.md`, `docs/features/visibility_rows/README.md`

## Test Execution

```
Ran 22 tests in 0.014s — OK
```

All 9 focused Goal632/633 tests pass. All 22 tests in the combined suite pass.

## Goal632: Ray/Triangle Any-Hit

**Predicate constructor** — `api.py:144`: `ray_triangle_any_hit(*, exact=False)` is correctly added and returns a typed `Predicate`.

**Reference implementation** — `reference.py:180–192`: `ray_triangle_any_hit_cpu` iterates triangles and breaks on the first accepted hit. The early-exit `break` is present and correct. Output schema is exactly `{ray_id, any_hit}`.

**Lowering** — `lowering.py:702–771`: `_lower_ray_triangle_any_hit` emits `workload_kind="ray_tri_anyhit"`, payload register `any_hit` at index 2, and host step text `"terminate traversal after the first accepted triangle hit"`. The device program `__anyhit__rtdl_triangle_terminate` is named distinctly from the hit-count variant `__anyhit__rtdl_triangle_count`, which is correct.

**Runtime wiring** — `runtime.py:172–173`: `ray_triangle_any_hit` is dispatched to `ray_triangle_any_hit_cpu`. The `_validate_oracle_supported_inputs` guard at `runtime.py:449` explicitly permits `Ray3D`/`Triangle3D` through the reference fallback, consistent with the v0.9.5 boundary.

**Oracle wiring** — `oracle_runtime.py:328–330`: `ray_triangle_any_hit` falls through to the Python reference (no native any-hit oracle), which matches the documented contract. The `candidates.left`/`right` indexing is consistent with the test fixtures where rays are always declared on the left.

**Exports** — `__init__.py:19, 331, 767, 770`: `ray_triangle_any_hit`, `ray_triangle_any_hit_cpu` are present in both the import list and `__all__`.

**Acceptance criteria met:**
- DSL predicate compiles and lowers to `ray_tri_anyhit` ✓
- Output schema is exactly `(ray_id, any_hit)` ✓
- `run_cpu_python_reference` and `run_cpu` match ✓
- Semantics are bounded: early-exit `break` after first hit ✓
- Exact first-blocker ID is not in the schema (not promised) ✓
- 3D any-hit routes through reference fallback ✓

## Goal633: Visibility Rows Standard Library

**Implementation** — `reference.py:224–278`: `visibility_rows_cpu` builds finite rays with the full un-normalized direction vector `(target - observer)` and `tmax=1.0`. At `t=1.0` the ray endpoint is exactly the target, so intersection is bounded to the observer-to-target segment. Blockers beyond the target (t > 1.0) are correctly ignored. This is the right design.

**Validation** — The function correctly rejects:
- Mixed 2D/3D observers and targets (`"one dimensionality"`)
- Zero-length observer-target pairs (`"distinct observer and target"`)
- Blocker triangles with dimension mismatch (`"blocker triangles must match"`)

**Empty-blockers case** — `ray_triangle_any_hit_cpu(rays, ())` yields `any_hit=0` for all rays, so `visible=1` for all pairs. Correct.

**Output schema** — `{observer_id, target_id, visible}` with `visible=0` when blocked and `visible=1` otherwise. Correct.

**Exports** — `__init__.py:338, 595`: `visibility_rows_cpu` is imported from reference and present in `__all__`.

**Acceptance criteria met:**
- Output schema is exactly `(observer_id, target_id, visible)` ✓
- 2D points and 2D triangle blockers supported ✓
- 3D points and 3D triangle blockers supported ✓
- Uses any-hit predicate internally ✓
- No rendering concepts exposed ✓
- Blocker IDs not promised or exposed ✓

## Goal634: Docs and Examples

**Feature docs** — `docs/features/ray_tri_anyhit/README.md` and `docs/features/visibility_rows/README.md` are both present, accurate, and explain the non-rendering spatial-query nature, the kernel shape, the output schema, the current backend maturity boundary, and how to run the examples.

**Examples** — Both `examples/rtdl_ray_triangle_any_hit.py` and `examples/rtdl_visibility_rows.py` are runnable, demonstrate the public API, and include meaningful fixtures.

## Minor Observations (Non-Blocking)

1. **Oracle input ordering assumption** — `oracle_runtime.py:329` reads `candidates.left` as rays and `candidates.right` as triangles without role-aware resolution. If a future caller constructs a kernel with triangles on the left and rays on the right, the oracle would receive swapped inputs. This pre-existing pattern is shared with `ray_triangle_closest_hit` and `ray_triangle_hit_count`, so it is not a regression introduced here. Documenting or guarding the assumption in a future cleanup would be useful.

2. **Dimension validation in `ray_triangle_any_hit_cpu`** — Mixed 2D/3D inputs raise inside `_finite_ray_triangle_hit_t` rather than at the entry of `ray_triangle_any_hit_cpu`. The error message is clear and the pattern is consistent with `ray_triangle_hit_count_cpu`. Acceptable for a reference implementation.

## Summary

The v0.9.5 any-hit and visibility implementation is correct, well-tested, and properly scoped. The early-exit semantic is implemented with `break` in the Python reference. The `tmax=1.0` + full-direction-vector construction in `visibility_rows_cpu` correctly bounds visibility queries to the observer-to-target segment. All Goal631 acceptance ladder items for Goal632, Goal633, and Goal634 are satisfied. No blocking issues found.

**ACCEPT**
