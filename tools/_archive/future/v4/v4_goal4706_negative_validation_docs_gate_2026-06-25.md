# V4 Goal4706 Negative Validation And Example Gate

Date: 2026-06-25

Status: `complete_pending_3ai_review_debt`

## Goal

Validate fail-closed behavior for rejected specialized Tier-3 callback shapes and
provide one bounded candidate example that runs without enabling public support.

## Result

Validation status: `passed`

Accepted example:

- path: `future/v4/examples/v4_specialized_tier3_scalar_callback_candidate_example.py`
- status: `bounded_candidate_example_not_public_api`
- compile stage: `compile_cache_ready_not_executed`
- public support authorized: `false`
- release authorized: `false`
- performance claim authorized: `false`

Negative rows rejected before compile:

- `arbitrary_python_callback`
- `action_side_effect_callback`
- `external_memory_mutation_callback`
- `dynamic_sbt_direct_callable_hot_path`
- `non_scalar_variable_length_output`

Each negative row returns a `RTDL_V4_TIER3_CALLBACK_REJECTED_*` error code,
keeps `internal_compile_allowed: false`, and keeps public support false.

## Evidence

- JSON:
  `future/v4/evidence/v4_goal4706_negative_validation_docs_gate_2026-06-25.json`
- Markdown:
  `future/v4/evidence/v4_goal4706_negative_validation_docs_gate_2026-06-25.md`
- Source:
  `src/rtdsl/v4_goal4706_negative_validation_docs_gate.py`
- Script:
  `scripts/v4_goal4706_negative_validation_docs_gate.py`
- Example:
  `future/v4/examples/v4_specialized_tier3_scalar_callback_candidate_example.py`
- Tests:
  `tests/v4_goal4706_negative_validation_docs_gate_test.py`

## Validation

Commands run:

```text
py scripts/v4_goal4706_negative_validation_docs_gate.py --json-out future/v4/evidence/v4_goal4706_negative_validation_docs_gate_2026-06-25.json --md-out future/v4/evidence/v4_goal4706_negative_validation_docs_gate_2026-06-25.md
py -m py_compile src/rtdsl/v4_goal4706_negative_validation_docs_gate.py scripts/v4_goal4706_negative_validation_docs_gate.py future/v4/examples/v4_specialized_tier3_scalar_callback_candidate_example.py src/rtdsl/v4.py
py -m unittest tests.v4_goal4706_negative_validation_docs_gate_test tests.v4_goal4705_source_ptx_cache_stability_test tests.v4_goal4704_specialized_tier3_support_wording_test
```

Observed:

- evidence generation: passed.
- `py_compile`: passed.
- unit tests: `9 tests OK`.

## Claim Boundary

Goal4706 does not authorize:

- public Tier-3 support;
- arbitrary callbacks;
- raw OptiX callbacks;
- action/side-effect callbacks;
- V4 release wording;
- app-level speed claims;
- broad V4 performance claims.

## Goal-Level Decision Audit

1. Was I being stupid?

No. This goal strengthens the fail-closed boundary and gives reviewers a small,
bounded example without turning the candidate into a public API.

2. If yes, what actions made the decision stupid?

Not applicable. One subtle point remains: the `non_scalar_variable_length_output`
case is rejected through the broader action/side-effect rejection path. That is
acceptable for fail-closed behavior but can be made more precise later if
reviewers ask.

3. Is there another path that avoids being stupid on one idea?

Yes. Keep examples in `future/v4/examples` and label them candidate/internal
until external review authorizes public docs.

4. Can I start a different path that actually solves the problem?

Yes. Goal4707 should consolidate review debt and produce one external-review
packet for Goals4696-4706, instead of scattering reviewer work across many
microfiles.

## Next

Proceed to Goal4707: specialized Tier-3 external-review packet and debt
consolidation.
