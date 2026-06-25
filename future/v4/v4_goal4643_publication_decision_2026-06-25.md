# V4 Goal4643 Publication Decision

Status: `v4_0_0_published_with_bounded_operator_claims`

Decision: `publish_v4_0_0_bounded_operator_release`

Authorized publication label:

`RTDL v4.0.0 bounded operator release: 8 generic RT-core operators faster than brute-force partner/CPU baselines`

## What Is Published

RTDL V4.0.0 is now a bounded generic RT-core operator release for the
documented measured surfaces. Its public performance claim is limited to the
eight documented operators beating their stated brute-force partner/CPU
baselines on the frozen Goal4639 scorecard.

The released surface contains:

- eight measured Tier-2 generic operator surfaces;
- measured partner scopes: Torch CUDA, Numba, and RTDL native prepared runner;
- zero current Tier-2 candidates;
- a conservative operator/callback planner that routes recognized generic
  operators and fails closed for unsupported logic;
- the frozen Goal4639 scorecard result: 8/8 measured surfaces and 4/4 strong
  families passed;
- public ratio distribution: most measured operators are 1.2-1.7x against
  their stated brute-force partner/CPU baselines; any-hit flags is 5.671x;
  point-nearest and AABB are large scale-dependent algorithmic-complexity wins
  against brute-force or slower same-contract index controls.

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

## Still Not Authorized

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
- Barnes-Hut covered by V4.0;
- Spatial RayJoin covered by V4.0;
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
