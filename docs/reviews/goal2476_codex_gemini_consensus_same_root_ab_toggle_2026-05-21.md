# Goal2476 Codex + Gemini Consensus: Same-Root Culling A/B Toggle

Date: 2026-05-21

## Verdict

Goal2476 is accepted as an internal app-agnostic grouped-union engineering step.

The implementation preserves existing default behavior by keeping the original
C ABI symbols default-on for same-root culling, and adds explicit `_with_options`
symbols plus Python/benchmark controls for same-build A/B measurement.

## Evidence Accepted

- Local grouped-continuation validation passed: 68 tests OK.
- Pod build passed on `NVIDIA RTX A5000, 570.211.01` with CUDA 12.8 and OptiX
  8.0 headers.
- Pod focused tests passed: 23 tests OK.
- Same-build pod A/B artifacts show matching signatures with same-root culling
  enabled and disabled.
- Median native grouped-union speedups for default-on culling were 1.314x at
  32768 points and 1.221x at 65536 points.
- Median total column-signature speedups for default-on culling were 1.193x at
  32768 points and 1.143x at 65536 points.

## External Review

Gemini's first review accepted the goal with no blocking issues but included an
incorrect illustrative timing example. A narrow follow-up review verified the
exact table values against the copied JSON artifacts and again reported no
blockers.

Review artifacts:

- `docs/reviews/goal2476_gemini_review_same_root_ab_toggle_2026-05-21.md`
- `docs/reviews/goal2476_gemini_followup_exact_numbers_same_root_ab_toggle_2026-05-21.md`

## Boundary

Public performance claims remain blocked. These numbers authorize only an
internal same-build engineering conclusion for the generic fixed-radius
grouped-union primitive. They do not authorize broad RT-core, whole-app
RT-DBSCAN, release, or paper speedup wording.
