# 3-AI Consensus: Threshold-4 OptiX Collect-K Gate

## Verdict

Codex, Claude, and Gemini agree that the threshold-4 OptiX `COLLECT_K_BOUNDED` gated candidate mode is acceptable as an internal experimental opt-in feature.

The consensus does not promote `COLLECT_K_BOUNDED`, does not change default behavior, does not authorize public speedup wording, and does not justify additional GPU pod cycling for this micro-goal.

## Reviewed Inputs

- Review request: `docs/reviews/goal1596_1597_threshold4_collect_k_external_review_request_2026-05-09.md`
- Claude review: `docs/reviews/goal1596_1597_threshold4_collect_k_claude_review_2026-05-09.md`
- Gemini review: `docs/reviews/goal1596_1597_threshold4_collect_k_gemini_review_2026-05-09.md`
- RTX 4090 report: `docs/reports/goal1596_v1_5_4_optix_collect_k_threshold4_gate_rtx4090_validation_2026-05-09.md`
- RTX 3090 report: `docs/reports/goal1597_v1_5_4_optix_collect_k_threshold4_gate_rtx3090_validation_2026-05-09.md`

## Agreement

- The C++ and Python topology predictors match the documented threshold:
  `baseline_carry_payload_copies >= candidate_carry_payload_copies + 4`.
- The feature remains opt-in behind `RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE=1`.
- Cross-architecture evidence is sufficient for this internal micro-goal:
  RTX 4090 and RTX 3090 both support the same strong regions.
- The validated strong regions are `65537`, `65538`, `65552`, and `69632`.
- `69633` and no-copy-reduction cases are correctly treated as gate-off/noise-scale.
- The no-promotion and no-public-speedup claim boundary is clear.

## Important Nuance

Claude noted that `RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE=1` enables the optimized baseline bundle for all multi-tile cases while restricting only the candidate carry-alias behavior by threshold. This is intentional and documented, but it means the flag is an experimental optimized-bundle mode, not a no-op for non-gated counts.

## Recommendation

Stop GPU pod cycling for this micro-goal. Further work should move to broader architecture/release planning, documentation, or a separate promotion review with explicit criteria. Any default-on or public-claim discussion should require a new review package and external consensus.

## Claim Boundary

This consensus is internal v1.5.4 experimental validation only. It does not promote `COLLECT_K_BOUNDED`, does not change defaults, does not authorize public speedup wording, and does not publish a release.
