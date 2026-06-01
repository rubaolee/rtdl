# Goal2986 Gemini Review: Goal2984/Goal2985 Second-Architecture Bounded Packet

Date: 2026-06-01

## Verdict

**accept-with-boundary**

## Rationale

This review assesses Goal2984's introduction of an explicit second-architecture Barnes-Hut profile and Goal2985's execution of a bounded packet using this profile. The key finding from Goal2977 was the performance bottleneck of the 8192-body Embree CPU baseline on the RTX 4000 Ada, preventing a clean 7/7 packet.

**1. Does Goal2984 make the bounded Barnes-Hut second-architecture profile explicit enough, without silently weakening the default canonical runner?**

Yes. Goal2984 successfully introduces a `second_arch_bounded` profile for the Barnes-Hut harness in `scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py`. This profile explicitly restricts the Barnes-Hut cases to `512:16` and `2048:32`, while the `default` profile retains the full `512:16`, `2048:32`, and `8192:32` cases. The `docs/reports/goal2984_barnes_hut_second_arch_profile_policy_2026-06-01.md` report clearly states that the bounded profile is not a release shortcut unless explicitly scoped, and the runner's boundary definitions prevent silent weakening. This is further validated by `tests/goal2984_barnes_hut_second_arch_profile_policy_test.py`, which confirms the distinctness and explicit boundaries of both profiles.

**2. Does Goal2985 provide a valid clean 7/7 RTX 4000 Ada packet for the bounded second-architecture scope?**

Yes. The execution documented in `docs/reports/goal2985_rtx4000ada_second_arch_bounded_packet_2026-06-01.md` and summarized in `docs/reports/goal2985_second_arch_bounded_packet_pod/goal2855_summary.json` confirms a `status: pass` with `all_pass: true` and `artifact_count: 7` for the specified `second_arch_bounded` profile. The `goal2803_barnes_hut.json` artifact for Barnes-Hut shows successful execution with OptiX RT-core acceleration and matching rows for the 512 and 2048 body counts, within the specified boundary.

**3. Does this close the operational part of the Goal2977 gap, while correctly keeping the release-scope policy question open?**

Yes. By successfully running a clean 7/7 packet on the RTX 4000 Ada with the `second_arch_bounded` Barnes-Hut profile, Goal2985 operationally resolves the bottleneck identified in Goal2977. Both Goal2984 and Goal2985 reports, as well as the `src/rtdsl/v2_5_internal_readiness.py` validation, explicitly state that this work "does not authorize v2.5 release or release tag action." They consistently highlight that the full 8192-body Embree CPU baseline remains unmeasured on this second architecture, leaving the policy decision for its inclusion in a future release packet open.

**4. Are any claims overbroad, especially public speedup, broad RT-core speedup, whole-app speedup, release readiness, paper reproduction, or true zero-copy?**

No. All relevant documents (`docs/reports/goal2984_barnes_hut_second_arch_profile_policy_2026-06-01.md`, `docs/reports/goal2985_rtx4000ada_second_arch_bounded_packet_2026-06-01.md`, and `docs/reports/goal2985_second_arch_bounded_packet_pod/goal2855_summary.json`) consistently and explicitly disclaim authorization for any overbroad claims, including public speedup, broad RT-core speedup, whole-app speedup, release readiness, paper reproduction, or true zero-copy. The internal readiness packet (`src/rtdsl/v2_5_internal_readiness.py`) reinforces these boundaries.

**5. What remains before a user-requested v2.5 release packet?**

Before a user-requested v2.5 release packet, the following key items remain:

*   **Policy Decision on Bounded Barnes-Hut:** A definitive policy decision is required regarding the acceptability of using the `second_arch_bounded` Barnes-Hut profile for v2.5 release claims on the second architecture, given the unmeasured 8192-body Embree baseline. This decision needs external reviewer consensus.
*   **External Review Completion:** This current external review of Goal2984/2985 must be considered complete and integrated.
*   **Triage of Goal2985:** Triage of the Goal2985 second-architecture bounded packet is listed as a next action in `src/rtdsl/v2_5_internal_readiness.py`.
*   **Fresh 3-AI Release Consensus:** A final, explicit 3-AI consensus would be necessary for any user-requested v2.5 release.
*   **Ongoing Internal Readiness:** Various "keep\_green" and "triage" actions in `V2_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS` indicate continuous internal readiness and monitoring tasks across other goals.
