# Goal3082: Claude External Review — Goal3081 v2.7 Advisory Planner

Date: 2026-06-03

Reviewer: Claude Sonnet 4.6 (external read-only review)

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

Test run recorded in the goal report:

```
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3081_v2_7_advisory_planner_test ...

Ran 31 tests in 0.070s

OK
primitive catalog up to date: ...docs\rtdl_primitive_catalog.md
```

This reviewer performed a static read-only code inspection. Tests were not independently re-executed.

---

## Q1: Does `plan_continuation(...)` remain explain-only, with no execution, dispatch, hidden routing, selected partner, or automatic partner selection?

**Yes, on every axis.**

The module-level constants establish the boundary before any code runs:

```python
PRIMITIVE_ADVISORY_PLANNER_EXECUTES = False
PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED = False
```

These values are the defaults for the corresponding fields on `PrimitiveAdvisoryPlan` (`primitive_planner.py:126-127`), so every returned plan carries them as structural facts, not just documentation.

In `_plan_from_match` (`primitive_planner.py:301-334`), `selected_partner=None` is always set explicitly. There is no code path that assigns any other value to `selected_partner`. `hidden_dispatch_allowed=False` is set via the dataclass field default (`primitive_planner.py:128`).

`validate_primitive_advisory_planner()` (`primitive_planner.py:219-260`) iterates every recipe, calls `plan_continuation(recipe_id=..., max_plans=1)`, and asserts all four boundary conditions hold at runtime:

```python
if plan.executes is not False:
    errors.append(...)
if plan.selected_partner is not None:
    errors.append(...)
if plan.automatic_partner_selection_allowed is not False:
    errors.append(...)
if plan.hidden_dispatch_allowed is not False:
    errors.append(...)
```

No native code is called in `primitive_planner.py`. The module imports only frozen dataclasses and pure Python lookup functions from `primitive_hierarchy`, `primitive_recipes`, and `v2_5_partner_support_matrix`. There is no executor binding, no dispatch call, no `__call__` method on any returned object.

**Finding: explain-only on all axes. No execution, dispatch, hidden routing, selected partner, or automatic partner selection.**

---

## Q2: Does the planner correctly expose each primitive step's status, especially `candidate_behavior` and `internal_generic_path`, rather than promoting advisory recipe status to stable primitive status?

**Yes.**

`_plan_step_from_node` (`primitive_planner.py:345-363`) reads `node.status` directly from the hierarchy node with no transformation:

```python
PrimitivePlanStep(
    ...
    primitive_status=node.status,
    ...
)
```

The `externally_stable` property on `PrimitivePlanStep` (`primitive_planner.py:55-56`) is defined as:

```python
_EXTERNAL_STABLE_STATUSES = (
    "stable_primitive",
    "stable_behavior",
    "stable_compatibility_path",
)

@property
def externally_stable(self) -> bool:
    return self.primitive_status in _EXTERNAL_STABLE_STATUSES
```

This means `candidate_behavior` and `internal_generic_path` and `internal_substrate` are all `externally_stable = False`.

`PrimitiveAdvisoryPlan.non_stable_step_ids` is the tuple of step ids where `not step.externally_stable`. `_plan_warnings` generates an explicit warning for any non-stable step ids:

```python
warnings.append(
    "recipe references non-stable primitive steps; advisory plan does not promote them: "
    + ", ".join(non_stable)
)
```

The `status_boundary` field is hardcoded to `"advisory_plan_does_not_promote_internal_or_candidate_primitive_steps"` on `PrimitiveAdvisoryPlan` (`primitive_planner.py:130`).

`validate_primitive_advisory_planner()` checks (`primitive_planner.py:242-243`):

```python
if plan.non_stable_step_ids and "does_not_promote" not in plan.status_boundary:
    errors.append(...)
```

The test `test_planner_exposes_non_stable_step_statuses` verifies the entire chain for `recipe.ray_triangle_hit_stream_grouped_summary`:

- `status_by_id["rows.ray_triangle_hit_stream_3d"] == "candidate_behavior"` ✓
- `"rows.ray_triangle_hit_stream_3d" in plan.non_stable_step_ids` ✓
- `"does_not_promote" in plan.status_boundary` ✓
- Warning containing `"non-stable primitive steps"` present ✓

This directly satisfies the forward boundary noted in Goal3079: "when a planner is built to surface these recipes to callers, it must propagate per-step primitive stability so callers understand that following a recipe may involve `candidate_behavior` or `internal_generic_path` nodes."

**Finding: per-step status is correctly exposed. `candidate_behavior` and `internal_generic_path` steps are flagged, warned, and listed in `non_stable_step_ids`. The advisory recipe label does not promote them.**

---

## Q3: Are partner options derived conservatively from the v2.5 support matrix, including fail-closed unsupported requested partner cells?

**Yes.**

`_partner_options` (`primitive_planner.py:366-398`) iterates `V2_5_ALLOWED_PARTNERS` and calls `plan_v2_5_partner_support(operation, partner)` for each, reading directly from `v2_5_partner_support_matrix.py`. No values are overridden or transformed beyond casting to the declared field types.

The filtering logic at `primitive_planner.py:376-379` is:

```python
if (
    cell["status"] == V2_5_SUPPORT_STATUS_UNSUPPORTED
    and partner != requested_partner
):
    continue
```

This means unsupported cells are hidden by default (conservative), but if the caller specifically requested that partner, the unsupported cell is included so the caller sees the fail-closed reason — not silently promoted or silently dropped. This is the correct behavior.

`V25PartnerSupportCell.__post_init__` (`v2_5_partner_support_matrix.py:54-79`) actively raises `ValueError` if any of these flags are set:

```python
if self.promoted_performance_path:
    raise ValueError(...)
if self.rt_traversal_replacement_allowed:
    raise ValueError(...)
if self.public_speedup_claim_authorized:
    raise ValueError(...)
if self.true_zero_copy_claim_authorized:
    raise ValueError(...)
```

These invariants hold at matrix construction time, before `plan_continuation` is ever called. `validate_primitive_advisory_planner()` also checks all returned partner options at planning time:

```python
if option.promoted_performance_path:
    errors.append(...)
if option.public_speedup_claim_authorized:
    errors.append(...)
if option.true_zero_copy_claim_authorized:
    errors.append(...)
```

The test `test_fixed_radius_query_lists_explicit_partner_options_without_selection` verifies the full partner option set for `partner="numba"` on a recipe with `grouped_argmin_f64` and `grouped_topk_f64` partner operations:

- `("grouped_argmin_f64", "python_reference", "reference_contract")` present ✓
- `("grouped_argmin_f64", "triton", "preview_not_promoted")` present ✓
- `("grouped_argmin_f64", "numba", "unsupported_fail_closed")` present (fail-closed, not silently dropped) ✓
- `selected_partner is None` ✓
- Warning about `"selected_partner remains None"` present ✓

**Finding: partner options are derived conservatively from the v2.5 support matrix. Unsupported-requested-partner cells are surfaced fail-closed. No performance path, speedup, or zero-copy flags are set in any option.**

---

## Q4: Is the generated catalog updated without overclaiming release readiness, public speedups, RT-core speedups, true zero-copy, paper reproduction, package install, or automatic Triton selection?

**No overclaiming on any axis.**

The catalog header (`primitive_catalog.py:44-48`, rendered to `docs/rtdl_primitive_catalog.md:5-8`) states:

> "Status: generated internal architecture catalog. This document organizes the current RTDL primitive surface; it does not authorize public release wording, public speedup claims, external ABI stability, authors-code parity, or paper reproduction claims."

The `## Advisory Planner` section (`primitive_catalog.py:343-368`, rendered to `docs/rtdl_primitive_catalog.md:341-363`) includes the full `PRIMITIVE_ADVISORY_PLANNER_CLAIM_BOUNDARY` verbatim:

> "v2.7 primitive advisory plans are explain-only metadata. They do not execute, dispatch, auto-select partners, authorize release readiness, authorize public speedup wording, authorize broad RT-core wording, authorize true zero-copy wording, or promote internal/candidate primitive steps to stable public primitives."

The planner table shows:
- `Executes or dispatches | False`
- `Auto-selects partners | False`

The `## Claim Boundary` section at the end of the catalog (`primitive_catalog.py:225-230`) reiterates that the catalog authorizes none of: release readiness, public speedup wording, zero-copy claims, broad RT-core claims, paper-reproduction claims, or app-specific native engine logic.

Checking for forbidden wording: The advisory planner section does not mention any speedup numbers, Triton selection, zero-copy semantics, or package installation. The `selected_partner=None` field description is explicitly documented. The word "automatic" appears only in the context of `automatic_partner_selection_allowed = False`.

The `test_catalog_documents_advisory_planner` test (`goal3081`) and `test_catalog_preserves_claim_boundary` test (`goal3073`) provide drift gates for the catalog wording.

**Finding: catalog is correctly conservative. No overclaiming on any prohibited axis.**

---

## Q5: Are the tests sufficient for this first v2.7 planner slice?

**Yes, with acceptable coverage gaps for a first slice.**

The five tests in `goal3081_v2_7_advisory_planner_test.py` cover:

| Test | What it verifies |
| --- | --- |
| `test_advisory_planner_validates` | All recipes pass the planner's own self-validation gate (status=accept, executes=False, auto-partner=False, errors=()) |
| `test_public_exports_include_planner_api` | All 8 planner symbols are in `rt.__all__` |
| `test_count_query_recommends_primitive_first_without_partner` | Facet query → correct recipe, `recommendation="primitive_first"`, no partner options, `selected_partner=None`, stable step statuses |
| `test_fixed_radius_query_lists_explicit_partner_options_without_selection` | Facet query + partner pref → explicit options, fail-closed unsupported, `selected_partner=None`, requires_explicit_partner_choice=True |
| `test_planner_exposes_non_stable_step_statuses` | candidate_behavior step exposed, non_stable_step_ids populated, "does_not_promote" in status_boundary, warning emitted |

`test_advisory_planner_validates` provides broad recipe coverage by running every defined recipe through `plan_continuation` and checking all boundary flags programmatically. This is equivalent to six indirect tests (one per recipe) in a single assertion.

`test_catalog_documents_advisory_planner` provides a drift gate for the catalog's planner section.

The existing `goal3077` and `goal3073` test suites continue to gate the recipe layer and the catalog integrity that the planner depends on.

Observable gaps (acceptable at this slice):
- No test for the `recipe_id=...` direct lookup path in `_recipe_matches`
- No test for `max_plans=0` returning empty tuple
- No test for invalid partner names raising `ValueError`
- No explicit test for `to_dict()` round-trip integrity of `PrimitiveAdvisoryPlan`
- No test for recipes with no partner operations (e.g., `recipe.aabb_candidate_rows_to_refinement`) producing empty `partner_options`

These are low-risk gaps. The `validate_primitive_advisory_planner()` coverage and the boundary-flag tests are the critical ones for this goal.

**Finding: tests are sufficient for the first v2.7 planner slice. Critical boundary properties, status exposure, fail-closed partner behavior, and catalog drift are all gated.**

---

## Q6: Is it acceptable to proceed next to small learner examples/docs showing `find_primitive(...)`, `find_recipe(...)`, and `plan_continuation(...)` as the v2.7 primitive discovery workflow?

**Yes.**

The three-function discovery workflow has stable, frozen interfaces:
- `find_primitive(...)` returns `tuple[PrimitiveDiscoveryMatch, ...]`
- `find_recipe(...)` returns `tuple[CompositionRecipeMatch, ...]`
- `plan_continuation(...)` returns `tuple[PrimitiveAdvisoryPlan, ...]`

All return types are frozen dataclasses with no callable methods beyond `to_dict()`. Learner examples would read from these objects without being able to trigger execution, dispatch, or partner selection.

The main risk with learner documentation is wording creep — an example that uses phrases like "select Triton," "zero-copy," or "run natively" would violate the claim boundary. That risk is managed by the same review process applied to any other documentation change. It is not a reason to block learner example work.

**Finding: proceeding to learner examples is appropriate. The underlying API is stable and explain-only. Wording review is the primary control needed for documentation work.**

---

## Boundary Note

This review verifies that Goal3081 does not authorize a release, public performance claim, broad RT-core wording, true zero-copy wording, package-install wording, automatic partner selection, or app-specific native engine logic. All six prohibited categories are explicitly blocked by code invariants (`__post_init__` guards, constant flags, `validate_primitive_advisory_planner()` gates) and are independently locked by the test suite.

The `docs/rtdl_primitive_catalog.md` drift gate (`test_checked_in_catalog_matches_renderer`) ensures the checked-in catalog stays synchronized with the renderer. Any change to the renderer that would introduce overclaiming wording would be caught by the drift gate before reaching the review stage.

---

## Summary

| Review question | Finding |
| --- | --- |
| Q1 explain-only: no execution, dispatch, hidden routing, selected partner, or auto-partner selection | Pass |
| Q2 per-step status exposed, candidate/internal steps not promoted | Pass |
| Q3 partner options conservative, unsupported-requested fail-closed | Pass |
| Q4 catalog updated, no overclaiming on any axis | Pass |
| Q5 tests sufficient for first v2.7 planner slice | Pass |
| Q6 safe to proceed to learner examples/docs | Yes |

**Verdict: `accept`**

Goal3081 delivers a clean, explain-only advisory planner that directly addresses the forward boundary from Goal3079. The code is conservative: every boundary flag is a structural constant, not just documentation. Every recipe is programmatically verified through `validate_primitive_advisory_planner()`. The prior review boundary ("planner must expose per-step primitive status") is explicitly encoded and tested. No overclaiming was found on any prohibited axis.
