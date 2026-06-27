# V4 Goal4720 Release-Candidate Guardrail Convergence

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision: `v4_python_edsl_operator_pushdown_release_candidate_machine_gate_converged`

## Purpose

Goal4720 closes the machine-state drift after Goal4718 and Goal4719. The current
V4 front door, catalog, scope gate, release-decision module, examples, and tests
now agree on the same user-facing truth:

- RTDL V4 is a Python eDSL/operator-pushdown release candidate.
- The current front door has `10` measured generic operator/workflow surfaces.
- The current partners with measured surface evidence are `cupy`, `numba`,
  `rtdl_native`, and `torch`.
- The V4-specific workflow win is constrained custom predicate early-exit:
  `v4_ray_triangle_custom_predicate_early_exit_3d_numba`.
- Broad legacy all-app high-performance wording remains unauthorized.
- Final public tag/release authorization remains blocked by external 3-AI
  review debt.

## What Changed

- `scripts/v4_catalog_regression_gate.py`
  - Updated the quickstart gate from the old `8 measured + 1 candidate` state to
    the current `10 measured + 0 candidates` state.
  - Added the public custom-predicate planning example to the dry-run regression
    gate.
  - Validates that constrained custom predicate early-exit remains authorized
    only as the measured V4 surface, while arbitrary Python/raw OptiX callbacks
    remain unauthorized.

- `src/rtdsl/v4_goal4643_publication_decision.py`
  - Reclassified the old Goal4643 publication record as superseded by the
    current Goal4720 release-candidate state instead of the older Goal4655-only
    bounded-operator state.
  - Preserves `formal_release_authorized: False`.

- Public/current docs and tests
  - Removed stale gate assumptions that still expected 8 or 9 measured surfaces.
  - Kept old Goal4639 scorecard truth intact while adding the post-scorecard
    aggregate-frontier and custom-predicate rows.
  - Kept public wording denominator-bound: no broad app-level speedup, no
    arbitrary callback support, no raw OptiX callback support, no C ABI or
    non-Python host claims.

## Evidence

- Catalog regression dry-run:
  `future/v4/evidence/v4_goal4720_catalog_regression_gate_dry_run_2026-06-26.json`
  and `.md`
  - status: `passed`
  - examples: `12`
  - quickstart measured surfaces: `10`
  - quickstart candidate surfaces: `0`
  - custom predicate planning example: `passed`

- Targeted regression suite:
  `py -m unittest tests.v4_catalog_regression_gate_test tests.v4_fixed_radius_docs_and_example_test tests.v4_goal4643_publication_decision_test tests.v4_goal4646_pretag_wording_fixes_test tests.v4_goal4651_partner_catalog_promotion_test tests.v4_goal4677_aggregate_frontier_promotion_test tests.v4_goal4678_ranked_summary_disposition_test`
  - result: `34 tests OK`

- Full V4 local suite:
  `py -m unittest discover -s tests -p "v4*_test.py"`
  - result: `435 tests OK`

- Compile check:
  `py -m py_compile scripts/v4_catalog_regression_gate.py src/rtdsl/v4_goal4643_publication_decision.py src/rtdsl/v4_release_decision.py src/rtdsl/v4_goal4644_post_release_guardrails.py`
  - result: passed

## Current Release Reading

This is now a legitimate V4 release candidate for the Python eDSL/operator
pushdown story:

- It exposes a clean V4 Python front door.
- It records 10 measured generic operator/workflow surfaces.
- It includes serious-scale evidence for a constrained user predicate workflow
  that V2.14/V3.0.2 did not expose as a first-class operator-pushdown route.
- It has runnable public examples and synchronized public docs.
- It has machine guardrails preventing the known overclaims.

This is not yet an externally authorized final public tag. The final tag still
requires external review debt closure under the user's 3-AI rule.

## Non-Authorization

Goal4720 does not authorize:

- broad V4 speedup wording;
- whole-application speedup wording;
- all-benchmark speedup wording;
- public true-zero-copy claims;
- arbitrary callback support;
- raw OptiX callback support;
- blanket CuPy performance claims;
- C ABI, embedding, or non-Python host binding claims;
- app-specific native engine kernels;
- final public tag without external review debt closure.

## Goal-Level Decision Audit

1. Was I being stupid?
   No. The action moved a concrete release blocker: stale machine gates and old
   8/9-surface assertions contradicted the current Goal4718/Goal4719 truth.

2. If yes, what action made the decision stupid?
   Not applicable. The avoided stupid action would have been writing another
   narrative summary while leaving the automated gates inconsistent.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes: do not claim broad legacy app-level speed. Keep the premise exactly at
   Python eDSL/operator-pushdown release candidate plus measured operator
   surfaces.

4. Can I now try the different path that actually solves the problem?
   Yes. The next path is final external review debt closure, clean-tree/release
   packaging, and only then a public tag with the bounded V4 wording.

## Next Goals

- Goal4721: external-review packet for the Goal4717-4720 release-candidate
  state, including exact reviewer questions and non-authorization boundaries.
- Goal4722: clean-tree/release-packaging gate for the V4 public front door.
- Goal4723: final tag decision after external review debt is closed.
