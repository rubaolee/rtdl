# Goal1316: Embree Bounded Candidate Collection Surface

Date: 2026-05-05

## Scope

This slice adds the symmetric Python/ctypes surface for the Embree backend under
the same v1.5 `COLLECT_K_BOUNDED` polygon-pair candidate contract:

`rtdl_embree_collect_polygon_pair_candidates_bounded`

The wrapper is optional so existing Embree shared libraries do not become stale
hard failures during import. Calls fail with a rebuild-oriented error when the
native symbol is absent.

## Contract

The Embree surface mirrors the OptiX surface:

- Explicit positive `candidate_capacity`.
- Stable sorted `(left_polygon_id, right_polygon_id)` candidate ids.
- `primitive=COLLECT_K_BOUNDED`.
- `backend=embree`.
- `complete_candidate_coverage=true` only on non-overflow return.
- `failure_mode=fail_closed_overflow`.
- `overflow_policy=no_silent_truncation`.

## Validation

Local validation completed:

- Missing-symbol behavior.
- Successful metadata shape with mocked native rows.
- Fail-closed overflow behavior.
- Capacity validation.
- Cross-run with OptiX surface and generic Jaccard fail-closed tests.
- `py_compile` for touched Python runtime files.
- `git diff --check`.

## Boundary

This is the Embree Python/native surface, not the Embree native C++ export. The
same-contract native export must still be implemented and validated before
`polygon_set_jaccard` can use native bounded collection as a promoted v1.5 path.
