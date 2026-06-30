# External Review Handoff: Goals 2984-2985 Second-Architecture Bounded Packet

Date: 2026-06-01

Please perform an independent review of the Goal2984/Goal2985 v2.5
second-architecture bounded packet work and write a review file under
`docs/reviews/`.

Suggested output paths:

- Gemini: `docs/reviews/goal2986_gemini_review_goal2984_2985_second_arch_bounded_packet_2026-06-01.md`
- Claude: `docs/reviews/goal2987_claude_review_goal2984_2985_second_arch_bounded_packet_2026-06-01.md`

## Files To Inspect

- `docs/reports/goal2984_barnes_hut_second_arch_profile_policy_2026-06-01.md`
- `docs/reports/goal2985_rtx4000ada_second_arch_bounded_packet_2026-06-01.md`
- `docs/reports/goal2985_second_arch_bounded_packet_pod/goal2855_summary.json`
- `docs/reports/goal2985_second_arch_bounded_packet_pod/goal2803_barnes_hut.json`
- `scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2984_barnes_hut_second_arch_profile_policy_test.py`
- `tests/goal2985_rtx4000ada_second_arch_bounded_packet_test.py`

## Context

Goal2977 produced useful RTX 4000 Ada evidence but was not a clean 7/7 packet
because the Barnes-Hut 8192-body Embree CPU baseline did not finish in a useful
time. Claude and Gemini both identified this as the concrete remaining
release-packet gap in the Goal2981 closeout reviews.

Goal2984 adds an explicit Goal2855 runner profile:

- `default`: full Barnes-Hut profile with `512:16`, `2048:32`, and `8192:32`;
- `second_arch_bounded`: bounded second-architecture profile with `512:16` and
  `2048:32` only.

Goal2985 then runs the full seven-harness packet on RTX 4000 Ada at commit
`20b62a3eb21607a4e313b58fd8804de91e681f4e` using
`--barnes-hut-case-profile second_arch_bounded`. The summary reports:

- `status: pass`
- `all_pass: true`
- `artifact_count: 7`
- `expected_artifact_count: 7`
- `barnes_hut_case_profile: second_arch_bounded`
- `dirty_artifacts: {}`
- `claim_boundary_violations: {}`

Barnes-Hut bounded rows:

- 512 bodies: Embree `2.994s`, OptiX `0.503s`, total `5.955x`, membership
  `177.221x`, rows match true.
- 2048 bodies: Embree `59.169s`, OptiX `3.773s`, total `15.681x`, membership
  `696.740x`, rows match true.

The full 8192-body Embree CPU baseline remains unmeasured on this second
architecture. Goal2985 says this is now a policy/review question, not missing
execution: a future release packet must explicitly state whether second-arch
Barnes-Hut evidence uses the bounded profile while the full profile remains
primary-architecture evidence.

## Questions To Answer

1. Does Goal2984 make the bounded Barnes-Hut second-architecture profile
   explicit enough, without silently weakening the default canonical runner?
2. Does Goal2985 provide a valid clean 7/7 RTX 4000 Ada packet for the bounded
   second-architecture scope?
3. Does this close the operational part of the Goal2977 gap, while correctly
   keeping the release-scope policy question open?
4. Are any claims overbroad, especially public speedup, broad RT-core speedup,
   whole-app speedup, release readiness, paper reproduction, or true zero-copy?
5. What remains before a user-requested v2.5 release packet?

Use one of these verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This review must not authorize release by itself. Final v2.5 release would
still require a user request and fresh 3-AI release consensus.
