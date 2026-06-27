# Call For Review: V4 Goal4746 Final Release-Candidate Review Packet

Date: 2026-06-26

Reviewer requested: Claude and Antigravity when available.

Status: `external_review_requested_debt_allowed`

## Files To Review

- `future/v4/v4_goal4746_final_release_candidate_review_packet_2026-06-26.md`
- `future/v4/evidence/v4_goal4746_final_release_candidate_review_packet_2026-06-26.json`
- `future/v4/v4_goal4742_current_release_framing_after_blocker_closure_2026-06-26.md`
- `future/v4/v4_goal4743_public_docs_current_framing_cleanup_2026-06-26.md`
- `future/v4/v4_goal4744_full_v4_local_gate_after_current_frontdoor_cleanup_2026-06-26.md`
- `future/v4/v4_goal4745_machine_release_decision_current_boundary_refresh_2026-06-26.md`
- `README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `future/v4/README.md`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_release_decision.py`

## Questions

1. Is this a coherent V4 release candidate for a Python eDSL/operator-pushdown
   surface?
2. Is the product claim honest given the app-level matrix?
3. Is custom predicate early-exit correctly framed as V4-specific value rather
   than a legacy all-app speedup?
4. Do docs, quickstart, scope gate, and machine release decision align?
5. Is the 561-test local gate sufficient local evidence?
6. Should final public tag be authorized now, or blocked pending amendments?

## Requested Verdict Labels

- `authorize_final_v4_tag_under_bounded_release_candidate_label`
- `approve_release_candidate_but_block_final_tag_until_amendments`
- `reject_release_candidate_overclaim_or_incomplete`

## Non-Authorization

This call-for-review itself does not authorize final V4 tag, all-benchmark
speedup claims, broad V4-over-V2.14 claims, arbitrary callbacks, raw OptiX
callbacks, true-zero-copy wording, non-Python embedding/C ABI, or app-specific
native kernels.
