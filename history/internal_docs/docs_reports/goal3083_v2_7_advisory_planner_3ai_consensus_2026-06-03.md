# Goal3083: v2.7 Advisory Planner 3-AI Consensus

Date: 2026-06-03

Status: consensus accepted

## Scope

This consensus covers Goal3081, the explain-only v2.7 advisory planner over
primitive discovery and composition recipes.

Goal3081 is an important internal architecture/discovery step, not a release
gate, roadmap reset, public performance claim, or public release authorization.
The required level was 2-AI consensus: Codex implementation/review plus one
independent external AI review. The actual result is stronger: Codex plus
Gemini plus Claude.

## Evidence

- Codex implementation report:
  `docs/reports/goal3081_v2_7_explain_only_advisory_planner_2026-06-03.md`
- Gemini external review:
  `docs/reviews/goal3082_gemini_review_goal3081_v2_7_advisory_planner_2026-06-03.md`
- Claude external review:
  `docs/reviews/goal3082_claude_review_goal3081_v2_7_advisory_planner_2026-06-03.md`
- Late Claude input used as forward design guidance, not counted as the
  same-goal review:
  `docs/reviews/goal3079_claude_review_goal3077_v2_7_composition_recipes_2026-06-03.md`

Gemini verdict: `accept`.

Claude verdict: `accept`.

Codex verdict: `accept-with-boundary`.

Consensus verdict: `accept-with-boundary`.

## Accepted Claims

- `plan_continuation(...)` is an explain-only planner.
- The planner does not execute native code, dispatch runtime work, hide routing,
  select a partner, or allow automatic partner selection.
- The planner exposes each primitive step's status, including non-stable
  `candidate_behavior` and `internal_generic_path` steps.
- The planner derives optional partner-support cells from the existing v2.5
  support matrix and surfaces unsupported requested partner cells fail-closed.
- The generated primitive catalog documents the planner without authorizing
  public release, speedup, RT-core, zero-copy, package-install, or
  paper-reproduction wording.

## Boundaries

This consensus does not authorize a release, public speedup wording, broad
RT-core wording, true zero-copy wording, package-install wording, paper
reproduction, app-specific native engine logic, hidden dispatch, automatic
partner selection, or automatic Triton selection.

The planner is accepted as a v2.7 discovery/orchestration explanation layer.
Users still choose execution paths and partners explicitly.

## Validation

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3081_v2_7_advisory_planner_test tests.goal3077_v2_7_composition_recipes_test tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3070_v2_7_primitive_discovery_core_test tests.goal2624_primitive_hierarchy_test
```

Result:

```text
Ran 31 tests in 0.065s

OK
primitive catalog up to date: C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\docs\rtdl_primitive_catalog.md
```

Additional checks:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m py_compile src\rtdsl\primitive_planner.py src\rtdsl\primitive_catalog.py src\rtdsl\__init__.py tests\goal3081_v2_7_advisory_planner_test.py
$env:PYTHONPATH='src;.'; py -3 scripts\generate_rtdl_primitive_catalog.py --check
```

Both checks passed.

## Next Accepted Step

Proceed to small learner-facing examples/docs showing the v2.7 workflow:

1. `find_primitive(...)` for intent search.
2. `find_recipe(...)` for composition discovery.
3. `plan_continuation(...)` for explain-only primitive-first and explicit
   partner-option planning.

That next step must preserve the same no-hidden-dispatch and
no-auto-partner-selection boundary.
