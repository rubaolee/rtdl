# Goal3084: v2.7 Primitive Discovery Workflow Docs And Example

Date: 2026-06-03

Status: implemented locally

## Purpose

Goal3084 adds the first learner-facing workflow for the v2.7 primitive
discovery stack accepted in Goals3070, 3077, and 3081.

The workflow shows three metadata-only calls:

1. `find_primitive(...)`
2. `find_recipe(...)`
3. `plan_continuation(...)`

It teaches users how to inspect primitive intent, composition recipes, and
explain-only advisory plans without implying that RTDL silently executes,
dispatches, selects partners, or authorizes performance claims.

## Files Added Or Updated

- Added `examples/v2_0/getting_started/rtdl_primitive_discovery_workflow.py`.
- Added `docs/learn/primitive_discovery_workflow.md`.
- Linked the workflow from:
  - `docs/learn/README.md`
  - `docs/tutorials/README.md`
  - `docs/app_example_quickstart.md`
  - `docs/application_catalog.md`
  - `examples/README.md`
  - `examples/v2_0/README.md`
  - `examples/v2_0/getting_started/README.md`
- Added compatibility import alias in `examples/__init__.py`.
- Added `tests/goal3084_v2_7_primitive_discovery_workflow_docs_test.py`.

## Example Behavior

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\v2_0\getting_started\rtdl_primitive_discovery_workflow.py
```

The output is JSON with:

- `primitive_match`
- `recipe_match`
- `advisory_plan`
- `claim_boundary`

The example intentionally asks for `partner="numba"` on fixed-radius ranked
summary planning. The current support matrix exposes Numba as
`unsupported_fail_closed` for the grouped argmin/top-k operations, while
`selected_partner` stays `null`. This makes the no-auto-selection rule visible
to learners.

## Validation

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3084_v2_7_primitive_discovery_workflow_docs_test tests.goal3081_v2_7_advisory_planner_test tests.goal3077_v2_7_composition_recipes_test tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3070_v2_7_primitive_discovery_core_test
```

Result:

```text
Ran 30 tests in 1.114s

OK
primitive catalog up to date: C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\docs\rtdl_primitive_catalog.md
```

Additional check:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m py_compile examples\v2_0\getting_started\rtdl_primitive_discovery_workflow.py tests\goal3084_v2_7_primitive_discovery_workflow_docs_test.py
```

Passed. The Windows Python launcher printed the known local-prefix warning, but
the command exited successfully.

Post-review hardening after Claude Goal3085:

- `docs/tutorials/README.md` now distinguishes the v2.6 released runtime
  examples from the v2.7 metadata-only primitive discovery addition.
- `tests/goal3084_v2_7_primitive_discovery_workflow_docs_test.py` now asserts
  the specific `grouped_argmin_f64` / `numba` /
  `unsupported_fail_closed` cell that demonstrates fail-closed partner
  explanation without selected-partner behavior.

## Boundaries

Goal3084 does not authorize release readiness, package-install wording, public
speedup wording, broad RT-core wording, true zero-copy wording, automatic
partner selection, automatic Triton selection, paper reproduction, or
app-specific native engine logic.

The workflow is a learner-facing metadata route only. It helps users inspect
what to use; it does not choose or run the app for them.
