# Goal3076: v2.7 Generated Primitive Catalog 2-AI Consensus

Date: 2026-06-03

Status: accepted for internal v2.7 continuation; not a release authorization.

## Scope

This consensus covers Goal3073 only:

- `src/rtdsl/primitive_catalog.py`
- `scripts/generate_rtdl_primitive_catalog.py`
- generated `docs/rtdl_primitive_catalog.md`
- `tests/goal3073_v2_7_generated_primitive_catalog_test.py`
- current-source wording cleanup from `Triton-first Partner Continuation` to
  `Explicit Partner Continuation`
- targeted update to the v2.5 pivot test so it no longer forces stale current
  hierarchy wording

It does not cover orchestration recipes, auto partner selection, release
packaging, performance claims, zero-copy claims, or public v2.7 readiness.

## Evidence

Codex local implementation and validation:

- `docs/reports/goal3073_v2_7_generated_primitive_catalog_and_drift_gate_2026-06-03.md`
- Windows validation: `Ran 27 tests in 0.026s OK`
- `scripts/generate_rtdl_primitive_catalog.py --check`: up to date
- `py_compile` clean for the generator, renderer, hierarchy, and touched tests

Gemini independent review:

- `docs/reviews/goal3074_gemini_review_goal3073_v2_7_generated_primitive_catalog_2026-06-03.md`
- Verdict: `accept`

Claude review attempt:

- Background Claude was attempted through the handoff workflow.
- Claude returned a session-limit message: `You've hit your session limit ... resets 9:50pm (America/New_York)`.
- No Claude review file exists for this goal; this file does not claim 3-AI consensus.

## Consensus Verdict

Codex + Gemini agree that Goal3073 is acceptable for internal v2.7 continuation.

The accepted boundary is:

- `src/rtdsl/primitive_hierarchy.py` is now the catalog source of truth;
- the checked-in catalog must match `render_primitive_catalog_markdown()`;
- the drift gate is byte-for-byte and fail-closed for this slice;
- generated docs remain app-agnostic and readable for primitive discovery;
- partner continuation wording is explicit and not Triton-first;
- no release, speedup, zero-copy, broad RT-core, paper-reproduction, or
  app-specific engine claim is authorized.

## Next Recommended Goal

Proceed to the next v2.7 slice only after this generated catalog gate stays
green: add advisory composition recipes over existing primitive nodes. Recipes
should remain discoverability/planning metadata, not hidden dispatch or partner
auto-selection.
