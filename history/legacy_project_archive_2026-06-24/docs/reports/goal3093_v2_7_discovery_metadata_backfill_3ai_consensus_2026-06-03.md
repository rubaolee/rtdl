# Goal3093: 3-AI Consensus For Goal3090 Discovery Metadata Backfill

Date: 2026-06-03

Status: accepted with bounded scope.

## Inputs

- Codex implementation/report:
  - `docs/reports/goal3090_v2_7_discovery_metadata_backfill_2026-06-03.md`
- Claude review:
  - `docs/reviews/goal3091_claude_review_goal3090_v2_7_discovery_metadata_backfill_2026-06-03.md`
- Gemini review:
  - `docs/reviews/goal3091_gemini_review_goal3090_v2_7_discovery_metadata_backfill_2026-06-03.md`
- Earlier 2-AI consensus:
  - `docs/reports/goal3092_v2_7_discovery_metadata_backfill_2ai_consensus_2026-06-03.md`

## Consensus Verdict

Goal3090 is accepted by Codex, Claude, and Gemini as the v2.7 D-2 discovery
metadata backfill.

All three reviewers agree that:

- `require_discovery_metadata=True` makes the D-2 requirement executable while
  preserving default hierarchy-validation behavior.
- All promotion-status primitive hierarchy nodes now have non-empty discovery
  metadata fields: `capability_tags`, `aliases`, `intent_phrases`,
  `reference_path`, and `backends`.
- The metadata stays app-agnostic, conservative, and bounded to primitive
  discovery/orchestration.
- `metadata_only` is an honest marker for abstract or future-pressure nodes
  that do not themselves execute.
- The generated primitive catalog accurately reports strict metadata validation.
- Goal3090 does not add runtime behavior, choose partners, promote stable
  primitives, or authorize release/performance/zero-copy/hardware claims.

## Validation

Codex and Gemini both report the same focused validation passing:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3090_v2_7_discovery_metadata_backfill_test `
  tests.goal3087_v2_7_duplicate_gate_promotion_workflow_test `
  tests.goal3084_v2_7_primitive_discovery_workflow_docs_test `
  tests.goal3081_v2_7_advisory_planner_test `
  tests.goal3077_v2_7_composition_recipes_test `
  tests.goal3073_v2_7_generated_primitive_catalog_test `
  tests.goal3070_v2_7_primitive_discovery_core_test `
  tests.goal2624_primitive_hierarchy_test

Ran 47 tests
OK
```

Codex also ran py_compile on the touched Python files. Claude could not run
tests in its environment, but performed source-level review and returned
`accept`.

## Optional Note

Claude identified one optional future cleanup: layer overview nodes currently
mix concrete backend lists and `metadata_only`. The reviewers do not treat this
as a blocker because executable child nodes carry their own backend scopes.
Future catalog cleanup may either normalize layer overview rows to
`metadata_only` or explicitly document inherited child-backend summary
semantics.

## Claim Boundary

This consensus does not authorize release readiness, public speedup wording,
zero-copy wording, broad RT-core claims, paper-reproduction claims, stable
primitive promotion, or app-specific native engine logic. It accepts only the
v2.7 discovery metadata backfill and strict metadata-validation workflow.
