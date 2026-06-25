# V4 Goal4643 Publication Decision

Status: `v4_0_0_published_with_bounded_operator_claims`

Decision: `publish_v4_0_0_formal_high_performance_operator_release`

Authorized publication label:

`RTDL v4.0.0 formal high-performance generic RT-core operator release`

## What Is Published

RTDL V4.0.0 is now the formal high-performance generic RT-core operator
release for the documented measured surfaces.

The released surface contains:

- eight measured Tier-2 generic operator surfaces;
- measured partner scopes: Torch CUDA, Numba, and RTDL native prepared runner;
- zero current Tier-2 candidates;
- a conservative operator/callback planner that routes recognized generic
  operators and fails closed for unsupported logic;
- the frozen Goal4639 scorecard result: 8/8 measured surfaces and 4/4 strong
  families passed;
- representative operator-scorecard geomean: 5.185x.

The geomean is an operator-scorecard result. It is not a whole-application
speedup claim.

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
