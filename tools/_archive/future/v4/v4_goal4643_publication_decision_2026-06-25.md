# V4 Goal4643 Publication Decision

Status: `v4_0_0_publication_record_superseded_by_goal4720`

Decision: `goal4643_publication_record_superseded_by_goal4720_release_candidate_review_debt`

Current label:

`RTDL V4 Python eDSL/operator-pushdown release candidate: 10 measured generic RT-core operator surfaces including constrained custom predicate early-exit at serious scale; broad legacy all-app speedup remains unauthorized`

Goal4643 is retained as a historical publication record. It is superseded for
current user-facing truth by Goal4718/Goal4719 and the Goal4720 machine release
decision: V4 is a Python eDSL/operator-pushdown release candidate, not a broad
legacy all-app speedup release.

## What Is Published

RTDL V4 currently exposes a Python eDSL/operator-pushdown front door for the
documented measured surfaces. Its public performance wording is limited to the
10 documented generic operator/workflow rows measured against their stated
denominators, plus the Goal4669 legacy app-level boundary.

The released surface contains:

- 10 measured Tier-2 generic operator/workflow surfaces;
- measured partner scopes: Torch CUDA, CuPy, Numba, and RTDL native prepared runner;
- zero current Tier-2 candidates;
- a conservative operator/callback planner that routes recognized generic
  operators and fails closed for unsupported logic;
- the frozen Goal4639 scorecard result: 8/8 original measured surfaces and 4/4 strong
  families passed, plus the post-scorecard aggregate-frontier and custom-predicate rows;
- public ratio distribution: most measured operators are 1.2-1.7x against
  their stated brute-force partner/CPU baselines; any-hit flags is 5.671x;
  point-nearest and AABB are large scale-dependent algorithmic-complexity wins
  against brute-force or slower same-contract index controls; custom predicate
  early-exit is a V4-specific operator-pushdown workflow win.

The raw 5.185x operator-scorecard geomean is retained as internal scorecard
math, but it must not be used as the public headline because it is dominated by
two algorithmic-complexity outliers. It is not a whole-application speedup claim
and it is not a near-handwritten-OptiX claim.

## Required Release Evidence

- Goal4639 scorecard:
  `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md`.
- Goal4640 docs cleanup:
  `future/v4/v4_goal4640_public_docs_cleanup_decision_2026-06-25.md`.
- Goal4641 clean-tree gate:
  `future/v4/v4_goal4641_clean_tree_reproducibility_gate_2026-06-25.md`.
- Goal4642 final authorization packet:
  `future/v4/v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md`.
- Antigravity authorization and amendment recheck:
  `future/v4/reviews/antigravity_v4_goal4642_final_3ai_release_authorization_review_amended_2026-06-25.md`,
  `future/v4/reviews/antigravity_v4_goal4642_amendment_recheck_2026-06-25.md`.
- Independent Codex authorization:
  `future/v4/reviews/codex_independent_v4_goal4642_final_authorization_review_and_amendment_recheck_2026-06-25.md`.
- Main Codex release-owner authorization:
  `future/v4/reviews/codex_main_v4_goal4642_final_release_owner_authorization_2026-06-25.md`.
- Goal4717 serious custom-predicate scale validation:
  `future/v4/v4_goal4717_custom_predicate_early_exit_serious_scale_validation_2026-06-26.md`.
- Goal4718 release matrix after custom predicate:
  `future/v4/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.md`.
- Goal4719 public docs/examples cleanup:
  `future/v4/v4_goal4719_public_docs_examples_release_candidate_cleanup_2026-06-26.md`.
- External review debt records for Goals 4717-4719:
  `future/v4/reviews/v4_goal4717_custom_predicate_early_exit_serious_scale_validation_review_debt_2026-06-26.md`,
  `future/v4/reviews/v4_goal4718_release_matrix_after_custom_predicate_review_debt_2026-06-26.md`,
  `future/v4/reviews/v4_goal4719_public_docs_examples_release_candidate_cleanup_review_debt_2026-06-26.md`.

## Still Not Authorized

The current Goal4720 boundary blocks the final public tag until external review
debt is closed. Goal4669 also blocks broad legacy all-app high-performance V4
release wording.

V4.0.0 does not authorize:

- broad V4 speedup wording;
- whole-application speedup wording;
- all-benchmark speedup wording;
- public true-zero-copy claims;
- Tier-3 callback/PTX support claims;
- raw OptiX callback support;
- CuPy performance claims;
- embedding, C ABI, or non-Python host binding claims;
- app-specific native engine kernels;
- Barnes-Hut new V4-over-V3 speedup;
- Spatial RayJoin speedup;
- LibRTS paper reproduction.

## Goal-Level Decision Audit

1. Was I stupid?
   No. This action follows the 3-AI release authorization and clean-tree
   evidence instead of creating more process work.

2. If yes, what actions made the decision stupid?
   Not applicable. The risky action avoided here is turning a bounded operator
   release into unsupported broad claims.

3. Was there another possible path?
   Yes: continue to wait for Claude. That would be review debt management, not
   a new technical gate, because Antigravity plus independent Codex plus main
   release-owner audit already satisfy the three-seat rule.

4. Can I switch to a real path that solves the problem?
   Yes. The real path is exactly this publication switch plus post-release
   guardrails and deferred-review debt.
