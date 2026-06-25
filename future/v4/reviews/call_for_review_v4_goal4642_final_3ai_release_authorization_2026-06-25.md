# Call For Review: V4 Goal4642 Final 3-AI Release Authorization

Requested reviewer: Claude, Antigravity, and Codex/owner-side final auditor.

This is the final V4 release authorization packet. Do not treat this as a
routine goal-completion review. The reviewer must explicitly authorize, require
amendments, or no-go release.

## Requested Publication Label

`RTDL v4.0.0 bounded operator release: 8 generic RT-core operators faster than brute-force partner/CPU baselines`

## Required Verdict Labels

Choose exactly one:

- `authorize_formal_v4_0_bounded_operator_release`
- `authorize_with_amendments_before_publication`
- `no_go_do_not_release_v4_0`

## Files To Review

- `future/v4/v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md`
- `future/v4/v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md`
- `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md`
- `future/v4/v4_goal4640_public_docs_cleanup_decision_2026-06-25.md`
- `future/v4/v4_goal4641_clean_tree_reproducibility_gate_2026-06-25.md`
- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4_goal4642_final_authorization_packet.py`
- `tests/v4_goal4642_final_authorization_packet_test.py`
- `docs/current_v4_status.md`
- `README.md`
- `future/v4/tier2_operator_catalog.md`

## Questions

1. Does the requested label accurately match the evidence?
2. Are the eight measured operator surfaces and the `4/4` strong-family
   scorecard sufficient for the requested narrow formal release?
3. Are deferred rows (`spatial_rayjoin`, `barnes_hut`) and partial controls
   handled honestly?
4. Are public docs and examples clean enough for release without misleading
   users?
5. Does the clean-tree evidence close the reproducibility blocker?
6. Which open review debts are closed, waived for this narrow release, or still
   release-blocking?
7. Are any forbidden claims still present in public-facing docs or machine
   status?
8. Final answer: authorize, authorize with amendments, or no-go?

## Do Not Authorize

Do not authorize any of these claims:

- broad V4 speedup;
- whole-application speedup;
- all-benchmark speedup;
- public true-zero-copy;
- Tier-3 callback support;
- raw OptiX callback support;
- CuPy performance;
- C ABI / embedding / non-Python host;
- app-specific native kernels;
- Barnes-Hut covered by V4.0;
- Spatial RayJoin covered by V4.0;
- LibRTS paper reproduction.

## Required Output

- one verdict label;
- findings by severity;
- answers to all eight questions;
- explicit debt disposition;
- explicit non-authorization block.
