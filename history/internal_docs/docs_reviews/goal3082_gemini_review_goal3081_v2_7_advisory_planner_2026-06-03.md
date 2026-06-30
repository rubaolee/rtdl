# Goal3082: Gemini External Review — Goal3081 v2.7 Advisory Planner

Date: 2026-06-03

Reviewer: Gemini

Verdict: **accept**

---

## Files Reviewed

- `src/rtdsl/primitive_planner.py`
- `src/rtdsl/primitive_recipes.py`
- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/v2_5_partner_support_matrix.py`
- `src/rtdsl/primitive_catalog.py`
- `src/rtdsl/__init__.py`
- `docs/rtdl_primitive_catalog.md`
- `docs/reports/goal3081_v2_7_explain_only_advisory_planner_2026-06-03.md`
- `docs/reviews/goal3079_claude_review_goal3077_v2_7_composition_recipes_2026-06-03.md`
- `tests/goal3081_v2_7_advisory_planner_test.py`
- `tests/goal3077_v2_7_composition_recipes_test.py`
- `tests/goal3073_v2_7_generated_primitive_catalog_test.py`

---

## Review Questions and Findings

### 1. Does `plan_continuation(...)` remain explain-only, with no execution, dispatch, hidden routing, selected partner, or automatic partner selection?

**Finding:** Yes.

The `plan_continuation(...)` function and its associated `PrimitiveAdvisoryPlan` dataclass are rigorously designed to be explain-only. Key constants `PRIMITIVE_ADVISORY_PLANNER_EXECUTES` and `PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED` are explicitly set to `False`. The `plan_continuation` docstring clearly states, "It never calls native code, never dispatches a partner, and never selects a partner silently." The `selected_partner` field in `PrimitiveAdvisoryPlan` is consistently `None`. Furthermore, the `validate_primitive_advisory_planner()` function and dedicated unit tests (`tests/goal3081_v2_7_advisory_planner_test.py`) actively verify these constraints, confirming no execution, dispatch, hidden routing, selection of partners, or automatic partner selection occurs.

### 2. Does the planner correctly expose each primitive step's status, especially `candidate_behavior` and `internal_generic_path`, rather than promoting an advisory recipe into stable primitive status?

**Finding:** Yes.

The planner correctly exposes the status of each primitive step. The `PrimitiveAdvisoryPlan` includes `primitive_steps` (which contain `primitive_status` for each step) and `non_stable_step_ids`. A `status_boundary` of "advisory_plan_does_not_promote_internal_or_candidate_primitive_steps" is explicitly set. Warnings are generated if non-stable primitive steps are identified. This directly addresses the boundary condition specified in the `Goal3079` Claude review, ensuring that an `advisory_recipe` does not implicitly promote the stability of `candidate_behavior` or `internal_generic_path` primitives. Unit tests confirm that `candidate_behavior` statuses are correctly identified and flagged as non-stable.

### 3. Are partner options derived conservatively from the v2.5 support matrix, including fail-closed unsupported requested partner cells?

**Finding:** Yes.

Partner options are derived conservatively from `src/rtdsl/v2_5_partner_support_matrix.py`. The `_partner_options` function in `primitive_planner.py` calls `plan_v2_5_partner_support`, which itself enforces strict boundaries against authorizing performance claims, RT traversal replacement, or zero-copy claims. Crucially, if a specific partner is requested and found to be unsupported, its `unsupported_fail_closed` status is included in the plan's `partner_options`, providing transparency on why the requested option is not viable. This "fail-closed" behavior for unsupported requested partners is verified by unit tests.

### 4. Is the generated catalog updated without overclaiming release readiness, public speedups, RT-core speedups, true zero-copy, paper reproduction, package install, or automatic Triton selection?

**Finding:** Yes.

The generated catalog (`docs/rtdl_primitive_catalog.md`) is updated conservatively. The `PRIMITIVE_ADVISORY_PLANNER_CLAIM_BOUNDARY` from `primitive_planner.py` is prominently displayed, explicitly denying authorization for release readiness, public speedup wording, broad RT-core wording, true zero-copy wording, and promotion of internal/candidate primitive steps. Similar conservative language appears throughout the catalog and in the `Goal3081` report, preventing overclaiming across all specified aspects. Unit tests verify the presence of these crucial boundary statements in the generated documentation.

### 5. Are the tests sufficient for this first v2.7 planner slice?

**Finding:** Yes.

The test suite (`tests/goal3081_v2_7_advisory_planner_test.py`) provides sufficient coverage for this initial slice of the v2.7 planner. It includes tests for:
- Overall planner validation, including `executes`, `automatic_partner_selection_allowed`, and error states.
- Public API exports.
- Behavior of `plan_continuation` for simple primitive-first recommendations.
- Complex scenarios involving partner options, requested partners, and the fail-closed mechanism for unsupported partner cells.
- The critical exposure of non-stable primitive step statuses, directly validating the boundary condition from Goal3077.
- Documentation consistency in the generated catalog.
The tests confirm that the planner adheres to its explain-only nature and boundary conditions.

### 6. Is it acceptable to proceed next to small learner examples/docs showing `find_primitive(...)`, `find_recipe(...)`, and `plan_continuation(...)` as the v2.7 primitive discovery workflow?

**Finding:** Yes.

Given that the planner is explicitly designed as an "explain-only" and "advisory" tool, providing learner examples and documentation for the `find_primitive(...)`, `find_recipe(...)`, and `plan_continuation(...)` functions is a logical and appropriate next step. This will effectively communicate the intended v2.7 primitive discovery workflow to users, reinforcing the non-executing and boundary-aware nature of these tools.

---

## Conclusion

Goal3081 successfully implements the v2.7 advisory planner, strictly adhering to the "explain-only" mandate and meticulously addressing the boundary conditions set forth in the previous review for Goal3077. The planner transparently exposes primitive step statuses, handles partner options conservatively (including fail-closed unsupported scenarios), and prevents any form of overclaiming in its design, implementation, and generated documentation. The test coverage is robust for this initial slice.

---
