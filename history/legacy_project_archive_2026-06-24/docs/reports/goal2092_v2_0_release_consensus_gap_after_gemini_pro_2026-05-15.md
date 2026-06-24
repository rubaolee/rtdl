# Goal2092 v2.0 Release Consensus Gap After Gemini Pro

Date: 2026-05-15

Status: `release-ready-except-strict-claude-family-consensus`

## Purpose

Goal2088 prepared the post-Goal2086 v2.0 release packet after the streaming witness-column fix. Goal2090 now contains a Gemini Pro review with verdict `accept-with-boundary`. Goal2091 contains a Copilot supplemental review with verdict `accept-with-boundary`.

This file records the exact consensus position without overclaiming.

## Current Reviews

| Review | System | File | Verdict | Counts For Strict v2.0 3-AI Consensus |
| --- | --- | --- | --- | --- |
| Codex integration review | OpenAI Codex | `docs/reports/goal2088_v2_0_release_prep_after_streaming_witness_2026-05-15.md` | `release-prep-candidate` | yes |
| Gemini Pro final review | Gemini | `docs/reviews/goal2090_gemini_review_goal2088_post_streaming_v2_release_prep_2026-05-15.md` | `accept-with-boundary` | yes |
| Copilot supplemental review | GitHub Copilot | `docs/reviews/goal2091_copilot_supplemental_review_goal2088_post_streaming_v2_release_prep_2026-05-15.md` | `accept-with-boundary` | supplemental only |
| Claude final review | Claude | pending | pending | missing |

Copilot is useful review signal, but the project refresh file says Copilot is likely GPT/OpenAI-backed and should not replace Claude or Gemini for strict distinct external-family consensus unless the user explicitly changes that rule.

## User Authorization

The repo now contains `docs/handoff/USER_V2_0_RELEASE_AUTHORIZATION_2026-05-15.md`, which records an out-of-band user authorization statement: `"updated results suggest we should release v2.0"`.

This clears the old Goal2072 blocker named `explicit user-requested release action missing`, subject to the main AI confirming the release action in the active workflow before tagging or publishing.

## Technical Release Position

Accepted by the current post-Goal2086 evidence:

- Goal2085 has all Embree and OptiX/RT cells filled.
- All 16 current OptiX/RT rows have measured v2/v1.8 ratios below `1.0` under documented contracts.
- The old `segment_polygon_anyhit_rows` mixed status is superseded by the streaming exact witness-column contract.
- Embree is bounded CPU same-contract evidence, not the headline GPU partner-speedup surface.
- Claim boundaries remain intact: no package-install claim, no arbitrary partner acceleration claim, no broad RT-core claim, no arbitrary polygon overlay claim, and no released-version claim until a release action happens.

## Remaining Governance Gap

Strict v2.0 release consensus is still missing one Claude-family external review under the standing rule:

- v2.0 public closure is a key decision requiring 3-AI consensus.
- The normal distinct set is Codex + Gemini + Claude.
- Claude is unavailable for roughly two days.
- Copilot does not replace Claude unless the user explicitly relaxes the rule for this release.

## Options

1. Wait for Claude and then write the final post-Goal2086 consensus file.
2. User explicitly relaxes the rule for this release to allow Codex + Gemini Pro + Copilot supplemental review, while documenting that exception.
3. User authorizes a bounded pre-release tag instead of final v2.0, preserving the strict final-release gate for later Claude review.

## Verdict

`accept-with-boundary`

The engineering evidence is release-ready after Goal2086 and Gemini Pro review. The only remaining issue is governance: whether to wait for Claude or explicitly accept Copilot as a temporary supplemental substitute.

