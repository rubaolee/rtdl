# Goal 193: v0.4 Direction Decision Review

Date: 2026-04-09
Status: closed

## Current review state

- Codex report written:
  - [goal193_v0_4_direction_decision_2026-04-09.md](goal193_v0_4_direction_decision_2026-04-09.md)
- Claude review saved:
  - [claude_v0_4_direction_review_2026-04-09.md](claude_v0_4_direction_review_2026-04-09.md)
- Gemini review saved:
  - [gemini_v0_4_direction_review_2026-04-09.md](gemini_v0_4_direction_review_2026-04-09.md)
- Codex consensus updated after Gemini:
  - [2026-04-09-codex-consensus-v0_4-direction-decision.md](../../history/ad_hoc_reviews/2026-04-09-codex-consensus-v0_4-direction-decision.md)

## Main live conclusion so far

The direction survives external challenge, but under a sharper contract:

- `v0.4` should still be a workload-language-first milestone
- `v0.4` should still convert `v0.3.0` proof work into public 3D
  geometric-query surface
- but it must include a concrete non-graphical 3D spatial-data workload rather
  than only generic ray visibility or demo mechanics
- and it must make the first engineering target explicit, not only describe the
  candidate space

## Final resolved decision

- first substrate feature to formalize:
  - `ray_tri_hitcount_3d`
- headline release workload:
  - `point_in_volume`

This resolves the main Claude objection that the previous package argued for a
direction without choosing the concrete first target that makes `v0.4`
actionable.
