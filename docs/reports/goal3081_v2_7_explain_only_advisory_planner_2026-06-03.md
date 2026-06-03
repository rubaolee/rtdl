# Goal3081: v2.7 Explain-Only Advisory Planner

Date: 2026-06-03

Status: implemented locally

## Purpose

Goal3081 adds the first v2.7 orchestration surface over the primitive discovery
and recipe layers. The new planner helps a caller move from intent to an
explainable primitive/recipe plan without turning RTDL into a hidden dispatcher.

This directly follows the late Goal3079 Claude review of the composition
recipes. That review accepted Goal3077 with one forward boundary: a planner must
expose each recipe step's primitive stability and must not let an
`advisory_recipe` label promote `candidate_behavior` or `internal_generic_path`
steps. Goal3081 encodes that rule in code and tests.

## What Changed

- Added `src/rtdsl/primitive_planner.py`.
- Exported `plan_continuation(...)`,
  `validate_primitive_advisory_planner()`, and planner dataclasses through
  `rtdsl`.
- Updated the generated primitive catalog renderer and regenerated
  `docs/rtdl_primitive_catalog.md`.
- Added `tests/goal3081_v2_7_advisory_planner_test.py`.

The planner consumes existing `CompositionRecipe` records and v2.5 partner
support metadata. It returns immutable explain-only `PrimitiveAdvisoryPlan`
objects containing:

- matched recipe id/title/status;
- matched facets and score;
- primitive steps with each step's `primitive_status`;
- `non_stable_step_ids`;
- optional partner-support cells for operations declared by the matched
  primitive steps;
- `selected_partner=None`;
- explicit no-execution, no-hidden-dispatch, and no-auto-partner-selection
  flags;
- claim boundaries and warnings.

## Planner Rules

1. If a recipe has no partner operations and says no partner is required, the
   recommendation is `primitive_first`.
2. If a recipe exposes partner-capable continuation operations, the
   recommendation is `primitive_first_with_explicit_partner_options`.
3. If the caller passes `partner=...`, the planner records that preference only
   for explanation; it never sets `selected_partner`.
4. Unsupported requested partner cells are shown fail-closed so the caller can
   see why the requested partner is not currently a supported option for that
   operation.
5. Non-stable recipe steps are reported through `non_stable_step_ids` and a
   warning. The plan status boundary states that advisory plans do not promote
   internal or candidate primitive steps.

## Example

```python
import rtdsl as rt

plans = rt.plan_continuation(
    intent="nearest",
    shape="fixed_radius",
    dim="3d",
    output="grouped",
    partner="numba",
)

plan = plans[0]
assert plan.recipe_id == "recipe.fixed_radius_ranked_candidates"
assert plan.selected_partner is None
assert plan.recommendation == "primitive_first_with_explicit_partner_options"
```

The returned plan includes `python_reference` and `triton` support cells for
`grouped_argmin_f64`; because the requested `numba` cell is unsupported for
that operation in the current support matrix, it is surfaced as
`unsupported_fail_closed` rather than silently selected.

## Validation

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3081_v2_7_advisory_planner_test tests.goal3077_v2_7_composition_recipes_test tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3070_v2_7_primitive_discovery_core_test tests.goal2624_primitive_hierarchy_test
```

Result:

```text
Ran 31 tests in 0.070s

OK
primitive catalog up to date: C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\docs\rtdl_primitive_catalog.md
```

## Boundaries

Goal3081 does not authorize release readiness, public speedup wording, broad
RT-core wording, true zero-copy wording, package-install wording,
paper-reproduction claims, hidden dispatch, automatic partner selection, or
automatic Triton selection.

The planner is a discovery/orchestration explanation layer only. It helps users
see candidate primitive and partner paths; users still choose partners and
execution code explicitly.

## Next Step

Seek external review of Goal3081. The review should verify that the planner is
useful enough for v2.7 discovery/orchestration while preserving the
app-agnostic, no-hidden-dispatch, no-auto-partner-selection boundary.
