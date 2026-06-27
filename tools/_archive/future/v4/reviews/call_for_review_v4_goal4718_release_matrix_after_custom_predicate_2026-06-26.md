# Call For Review: V4 Goal4718 Release Matrix After Custom Predicate Early-Exit

Date: 2026-06-26

Requested verdict:

`accept_goal4718_release_matrix_continue_goal4719_docs`

or reject/amend with concrete reasons.

## Review Target

Please review:

- completion report:
  `future/v4/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md`
- evidence:
  `future/v4/evidence/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.json`
- evidence summary:
  `future/v4/evidence/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md`
- implementation:
  `src/rtdsl/v4_goal4718_release_matrix_after_custom_predicate.py`
- front door:
  `src/rtdsl/v4.py`
- scope gate:
  `src/rtdsl/v4_scope.py`
- tests:
  `tests/v4_goal4718_release_matrix_after_custom_predicate_test.py`
  `tests/v4_frontdoor_test.py`
  `tests/v4_scope_gate_test.py`

## Questions

1. Does Goal4718 correctly separate the new V4 workflow win from the old
   promoted-app all-suite high-performance no-go?
2. Is it legitimate to classify V4 as a Python eDSL/operator-pushdown release
   candidate after Goal4717, while keeping public tag/release unauthorized?
3. Are the allowed claims narrow enough and evidence-backed?
4. Are the forbidden claims complete enough to prevent V3-style overclaiming?
5. Is Goal4719 docs/tutorial/examples cleanup the correct next step before
   final release/tag review?

## Non-Authorization To Preserve

This review must not authorize:

- public tag;
- final V4 release wording;
- broad all-app speedup;
- "all benchmark apps are faster";
- arbitrary Python callback support;
- raw OptiX callback support;
- public Tier-3 support;
- non-Python embedding/C ABI;
- app-specific native kernels.

The only accepted continuation should be:

`Goal4719: public docs, tutorials, examples, and release wording cleanup.`
