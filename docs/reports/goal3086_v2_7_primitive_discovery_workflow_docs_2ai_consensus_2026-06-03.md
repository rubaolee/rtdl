# Goal3086: v2.7 Primitive Discovery Workflow Docs 2-AI Consensus

Date: 2026-06-03

Status: consensus accepted

## Scope

This consensus covers Goal3084, the learner-facing primitive discovery workflow
docs and runnable metadata-only example.

Goal3084 is a small learner/documentation slice, not a release gate, roadmap
change, or public performance claim. The required level is 2-AI consensus:
Codex implementation/review plus one independent external AI review.

## Evidence

- Codex implementation report:
  `docs/reports/goal3084_v2_7_primitive_discovery_workflow_docs_example_2026-06-03.md`
- Claude external review:
  `docs/reviews/goal3085_claude_review_goal3084_v2_7_primitive_discovery_workflow_docs_2026-06-03.md`

Claude verdict: `accept-with-boundary`.

Codex verdict: `accept-with-boundary`.

Consensus verdict: `accept-with-boundary`.

Gemini was attempted for this slice, but the CLI produced only a placeholder
review and then a stream error. That placeholder was not counted as consensus
evidence and was not kept in the tracked repo.

## Accepted Claims

- `examples/v2_0/getting_started/rtdl_primitive_discovery_workflow.py` is a
  runnable metadata-only learner example.
- The example shows `find_primitive(...)`, `find_recipe(...)`, and
  `plan_continuation(...)` without executing a backend or dispatching a
  partner.
- The example makes `selected_partner: null`, `executes: false`, and
  `automatic_partner_selection_allowed: false` visible in JSON output.
- The deliberate `partner="numba"` request surfaces an
  `unsupported_fail_closed` support cell, showing that requested partners are
  explained rather than silently selected.
- Public learner and example indexes now point to the workflow without routing
  normal learners through history or release logs.

## Review Intake

Claude accepted the slice and noted two minor issues:

1. `docs/tutorials/README.md` mixed a v2.6 release label with a v2.7 discovery
   workflow step.
2. The first version of the test only checked that `partner_options` was
   non-empty, not that the specific fail-closed Numba cell existed.

Both were addressed before this consensus:

- The tutorial README now states that runtime examples teach the v2.6 released
  source-tree surface while primitive discovery is a v2.7 metadata-only
  source-tree addition.
- The Goal3084 test now asserts the
  `grouped_argmin_f64` / `numba` / `unsupported_fail_closed` cell.

## Boundaries

This consensus does not authorize release readiness, package-install wording,
public speedup wording, broad RT-core wording, true zero-copy wording,
automatic partner selection, automatic Triton selection, paper reproduction, or
app-specific native engine logic.

The accepted workflow is learner-facing metadata and discovery guidance only.

## Validation

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3084_v2_7_primitive_discovery_workflow_docs_test tests.goal3081_v2_7_advisory_planner_test tests.goal3077_v2_7_composition_recipes_test tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3070_v2_7_primitive_discovery_core_test
```

Result:

```text
Ran 30 tests in 1.222s

OK
primitive catalog up to date: C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\docs\rtdl_primitive_catalog.md
```

Additional check:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m py_compile examples\v2_0\getting_started\rtdl_primitive_discovery_workflow.py tests\goal3084_v2_7_primitive_discovery_workflow_docs_test.py
```

Passed.
