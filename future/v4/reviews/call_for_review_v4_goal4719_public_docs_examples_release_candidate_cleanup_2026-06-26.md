# Call For Review: V4 Goal4719 Public Docs, Tutorials, Examples, And Release Wording Cleanup

Date: 2026-06-26

Requested verdict:

`accept_goal4719_public_docs_continue_final_release_gate`

or reject/amend with concrete reasons.

## Review Target

Please review:

- completion report:
  `future/v4/v4_goal4719_public_docs_examples_release_candidate_cleanup_2026-06-26.md`
- current front page:
  `README.md`
- current status:
  `docs/current_v4_status.md`
- app-level boundary:
  `docs/app_level_benchmark_summary.md`
- performance wording:
  `docs/learn/performance_wording.md`
- examples index:
  `examples/README.md`
- new example:
  `examples/v4/custom_predicate_early_exit_planning.py`
- V4 catalog:
  `future/v4/tier2_operator_catalog.md`
- tests:
  `tests/v4_goal4640_public_docs_cleanup_test.py`
  `tests/v4_goal4644_post_release_guardrails_test.py`

## Questions

1. Do the public docs now explain V4 as a Python eDSL/operator-pushdown release
   candidate rather than a vague bounded-only/no-go surface?
2. Do the docs clearly preserve the legacy all-app no-go boundary?
3. Is the custom predicate early-exit workflow described with its denominator,
   scale, and callback limits?
4. Is the new example runnable and correctly fail-closed for unsafe callbacks?
5. Is Goal4720 final release gate the right next step?

## Non-Authorization To Preserve

This review must not authorize:

- final public tag;
- broad all-app speedup;
- "all benchmark apps are faster";
- arbitrary Python callback support;
- raw OptiX callback support;
- public Tier-3 support;
- embedding/C ABI or non-Python host claims;
- app-specific native kernels.

The only accepted continuation should be:

`Goal4720: final V4 release decision packet, machine release gate update, and broad local validation.`
