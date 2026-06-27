# Codex Main V4 Goal4642 Final Release-Owner Authorization

Date: 2026-06-25

Verdict: `authorize_formal_v4_0_high_performance_operator_release`

Authorized publication label:

`RTDL v4.0.0 formal high-performance generic RT-core operator release`

## Review Seats

1. Antigravity:
   `future/v4/reviews/antigravity_v4_goal4642_final_3ai_release_authorization_review_amended_2026-06-25.md`
   and
   `future/v4/reviews/antigravity_v4_goal4642_amendment_recheck_2026-06-25.md`.
   Final verdict: `amendments_satisfied_authorize_publication`.

2. Independent Codex review:
   `future/v4/reviews/codex_independent_v4_goal4642_final_authorization_review_and_amendment_recheck_2026-06-25.md`.
   Final verdict: `amendments_satisfied_authorize_publication`.

3. Main Codex release-owner audit:
   this record. Final verdict: `authorize_formal_v4_0_high_performance_operator_release`.

Claude remained unavailable due session limits during this release decision
window. That debt is recorded but is not counted as a blocking seat because the
user authorized Antigravity plus later Claude debt when Claude is unavailable,
and the required three seats are satisfied by Antigravity, independent Codex,
and main Codex release-owner audit.

## Evidence Checked

- Goal4639 serious scorecard passed:
  `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md`.
- Goal4640 public-doc cleanup passed:
  `future/v4/v4_goal4640_public_docs_cleanup_decision_2026-06-25.md`.
- Goal4641 committed clean-tree reproducibility passed:
  `future/v4/v4_goal4641_clean_tree_reproducibility_gate_2026-06-25.md`.
- Goal4642 final authorization packet exists:
  `future/v4/v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md`.
- Amendment closure committed in `8e9307fc5b5e13d8d214f5893f9c31bf6e718fe1`.
- Local V4 suite passed at amendment closure: 175 tests.
- Clean-tree V4 suite passed from
  `C:\Users\Lestat\Desktop\work\rtdl_v4_goal4641_clean_tree_check` at
  `8e9307fc5b5e13d8d214f5893f9c31bf6e718fe1`: 175 tests.
- Clean-tree catalog dry-run and quickstart passed at
  `8e9307fc5b5e13d8d214f5893f9c31bf6e718fe1`.

## Authorized Claims

- RTDL V4.0.0 is the formal high-performance generic RT-core operator release.
- V4.0.0 contains eight measured Tier-2 generic operator surfaces.
- The frozen Goal4639 scorecard passed for those documented operator surfaces:
  8/8 measured surfaces and 4/4 strong families.
- The representative operator-scorecard geomean is 5.185x.
- The release is Python-facing and measured for the documented partner scopes:
  Torch CUDA, Numba, and RTDL native prepared runner.

## Forbidden Claims

This release does not authorize:

- broad V4 speedup;
- whole-application speedup;
- all-benchmark speedup;
- public true-zero-copy;
- Tier-3 callback/PTX support;
- raw OptiX callback support;
- CuPy performance;
- C ABI, embedding, or non-Python host binding support;
- app-specific native engine kernels;
- Barnes-Hut covered by V4.0;
- Spatial RayJoin covered by V4.0;
- LibRTS paper reproduction.

## Goal-Level Decision Audit

1. Was I stupid?
   No for this release-owner decision. The stupid path would be to keep
   producing more review process after two explicit authorizing reviewers and
   clean-tree evidence, or to flip broad release flags beyond the authorized
   scope.

2. If yes, what actions made the decision stupid?
   Not applicable. The risky action identified and avoided here is conflating
   a formal operator release with broad whole-app speedup, Tier-3, zero-copy,
   or embedding claims.

3. Was there another possible path?
   Yes: defer publication until Claude returns. That path would add waiting but
   no new evidence because the required three seats are already satisfied and
   Claude unavailability is recorded as debt.

4. Can I switch to a real path that solves the problem?
   Yes. The real path is to publish the narrow V4.0.0 operator release now,
   keep forbidden claims machine-guarded, and move any remaining Claude review
   to post-release debt.

## Decision

Proceed to Goal4643 publication-state switch. The release owner authorizes the
source tree and public docs to state the narrow V4.0.0 formal release label
above, provided the publication patch keeps all forbidden claims false and
passes the V4 regression gates again.
