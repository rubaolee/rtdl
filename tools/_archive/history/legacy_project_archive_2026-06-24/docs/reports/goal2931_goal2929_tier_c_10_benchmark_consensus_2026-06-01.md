# Goal2931: Goal2929 Tier C / 10-Benchmark Foundation Consensus

Date: 2026-06-01
Status: accepted for internal v2.5 evidence indexing

## Scope

Goal2931 records Codex + Gemini 2-AI consensus for Goal2929, which added fresh
RTX A5000 Tier C no-regression smoke for:

- `contact_manifold`
- `robot_collision`

Goal2929 also clarified the current ten-benchmark foundation:

- seven apps in the current canonical packet,
- `raydb_style` through the same-contract performance gate,
- `contact_manifold` and `robot_collision` through Tier C no-regression smoke.

## Consensus Inputs

| Reviewer | Artifact | Verdict | Notes |
| --- | --- | --- | --- |
| Codex | `docs/reports/goal2929_tier_c_no_regression_and_10_benchmark_foundation_2026-06-01.md` | `accept-with-boundary` | Contact and robot evidence are fresh OptiX no-regression smokes, not release or public speedup evidence. |
| Gemini | `docs/reviews/goal2930_gemini_review_goal2929_tier_c_10_benchmark_foundation_2026-06-01.md` | `accept` | No issues found; Codex + Gemini 2-AI consensus is appropriate for this internal Goal2929. |

## Accepted Findings

The reviewers agree that Goal2929 is valid internal v2.5 foundation evidence:

- `contact_manifold` proves the generic OptiX AABB broadphase plus bounded
  witness-row path matches the CPU reference without adding native
  contact/manifold semantics.
- `robot_collision` proves prepared OptiX pose-flags oracle parity at the
  validation scale.
- The 65,536-pose robot artifact is correctly marked as timing-only with
  validation skipped and compacted into counts, checksums, and samples.
- The benchmark manifest now explains the ten-app foundation without promoting
  Tier C apps into Tier A/B partner-parity or public speedup rows.

## Boundary

This consensus does not authorize v2.5 release, release tag actions, public
speedup wording, broad RT-core claims, whole-app speedup claims, true zero-copy
claims, package-install claims, automatic Triton-selection claims,
paper-reproduction claims, or app-specific native engine logic.

Fresh 3-AI release consensus remains required before any release action or
public v2.5 performance claim.
