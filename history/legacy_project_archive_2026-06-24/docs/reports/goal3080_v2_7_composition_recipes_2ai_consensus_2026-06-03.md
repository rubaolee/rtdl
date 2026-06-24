# Goal3080: v2.7 Composition Recipes 2-AI Consensus

Date: 2026-06-03

Status: accepted for internal v2.7 continuation; not a release authorization.

## Scope

This consensus covers Goal3077 only:

- `src/rtdsl/primitive_recipes.py`
- recipe API exports from `src/rtdsl/__init__.py`
- generated recipe section in `docs/rtdl_primitive_catalog.md`
- `tests/goal3077_v2_7_composition_recipes_test.py`
- `docs/reports/goal3077_v2_7_advisory_composition_recipes_2026-06-03.md`

It does not cover advisory planning, hidden dispatch, partner auto-selection,
release packaging, performance claims, zero-copy claims, or public v2.7
readiness.

## Evidence

Codex local implementation and validation:

- Windows validation: `Ran 25 tests in 0.027s OK`
- `scripts/generate_rtdl_primitive_catalog.py --check`: up to date
- `py_compile` clean for the recipe module, catalog renderer, `__init__`, and recipe tests

Gemini independent review:

- `docs/reviews/goal3078_gemini_review_goal3077_v2_7_composition_recipes_2026-06-03.md`
- Verdict signal: all six review questions were answered with `accept`

Claude review attempt:

- Background Claude was attempted through the handoff workflow.
- No `docs/reviews/goal3079_claude_review_goal3077_v2_7_composition_recipes_2026-06-03.md` file exists.
- This file does not claim 3-AI consensus.

## Consensus Verdict

Codex + Gemini agree that Goal3077 is acceptable for internal v2.7 continuation.

The accepted boundary is:

- composition recipes are metadata only;
- recipes do not execute, dispatch, or auto-select partners;
- recipe ids, titles, and summaries remain app-agnostic;
- every recipe references existing primitive node ids;
- `validate_composition_recipes()` fails closed on missing primitive steps,
  unknown tags, missing boundaries, and auto partner selection;
- generated catalog wording remains non-authorizing;
- no release, speedup, zero-copy, broad RT-core, paper-reproduction, or
  app-specific engine claim is authorized.

## Next Recommended Goal

Proceed to an advisory planner only if it stays explain-only. The planner may
return recommended primitive-first recipes and explicit partner options, but it
must not execute, dispatch, or select a partner automatically.
