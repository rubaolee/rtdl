# Call For Review: V4 Goal4720 Release-Candidate Guardrail Convergence

Date: 2026-06-26

Requested verdict labels:

- `accept_goal4720_release_candidate_machine_gate_converged`
- `accept_with_required_amendments`
- `reject_goal4720_state_inconsistent`
- `reject_overclaims_or_missing_evidence`

## Review Target

Please review Goal4720:

- `future/v4/v4_goal4720_release_candidate_guardrail_convergence_2026-06-26.md`

Supporting current artifacts:

- `future/v4/v4_goal4717_custom_predicate_early_exit_serious_scale_validation_2026-06-26.md`
- `future/v4/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md`
- `future/v4/v4_goal4719_public_docs_examples_release_candidate_cleanup_2026-06-26.md`
- `future/v4/evidence/v4_goal4720_catalog_regression_gate_dry_run_2026-06-26.json`
- `future/v4/evidence/v4_goal4720_catalog_regression_gate_dry_run_2026-06-26.md`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_scope.py`
- `src/rtdsl/v4_release_decision.py`
- `scripts/v4_catalog_regression_gate.py`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`

## Questions

1. Do the current V4 front door, scope gate, catalog, release-decision module,
   examples, and public docs consistently say `10 measured surfaces` and
   `0 candidates`?
2. Does the custom predicate early-exit surface support the V4 Python
   eDSL/operator-pushdown release-candidate story without implying arbitrary
   callback or raw OptiX callback support?
3. Are broad legacy all-app speedup claims still blocked clearly enough?
4. Is it acceptable to treat Goal4720 as machine-gate convergence pending
   external review debt, not final public tag authorization?
5. Did the regression gate correctly add the custom-predicate public example
   and retire the stale 8/9-surface assumptions?
6. Are the validation results sufficient for a release-candidate state:
   `34 targeted tests OK`, `435 full V4 tests OK`, catalog dry-run passed?
7. What exact changes, if any, are required before final public tag?

## Non-Authorization

This review must not authorize broad V4 speedup wording, whole-application
speedups, all-benchmark speedups, public true-zero-copy claims, arbitrary
callback support, raw OptiX callbacks, blanket CuPy performance claims, C ABI,
embedding, non-Python host binding claims, app-specific native kernels, or a
final public tag unless the reviewer explicitly says the 3-AI final release
rule is satisfied.
