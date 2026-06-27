# Goal 1584: OptiX Collect-K Candidate Preset 3-AI Consensus

## Verdict

Codex, Claude, and Gemini agree that `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1` is acceptable as an opt-in candidate preset for continued validation. It is not acceptable for default promotion yet, and it does not justify public speedup claims.

## Reviewed Artifacts

- Implementation/report: `docs/reports/goal1580_v1_5_4_optix_collect_k_fastest_candidate_preset_2026-05-08.md`
- Broader pod validation: `docs/reports/goal1581_v1_5_4_optix_collect_k_candidate_preset_broader_pod_validation_2026-05-08.md`
- 49153 noise isolation: `docs/reports/goal1582_v1_5_4_optix_collect_k_49153_noise_isolation_2026-05-08.md`
- Review fix and hostile-env validation: `docs/reports/goal1583_v1_5_4_optix_collect_k_candidate_preset_review_fix_2026-05-08.md`
- Claude review: `docs/reviews/goal1580_1582_collect_k_candidate_preset_claude_review_2026-05-08.md`
- Gemini review: `docs/reviews/goal1580_1583_collect_k_candidate_preset_gemini_review_2026-05-08.md`

## Consensus Points

- The preset correctly enables the measured positive bundle and does not enable the rejected pointer-carry diagnostics.
- The runner now isolates profile subprocess environments before selecting baseline, alias, or candidate-preset mode.
- Parity and topology evidence are accepted for the recorded Ada pod runs.
- The `49153` negative timing point is best treated as measurement instability rather than a correctness failure, but it remains a promotion caution.
- The current evidence is microbenchmark evidence for the exact OptiX `COLLECT_K_BOUNDED` subpath, not whole-application evidence.

## Remaining Blockers

- Run additional independent pod sessions to improve timing confidence.
- Validate at least one non-Ada NVIDIA architecture before default-promotion discussion.
- Add row-width coverage if the intended promotion scope expands beyond current row-width-2 evidence.
- Re-review the final evidence package before any stable promotion, public speedup wording, or release action.

## Claim Boundary

This consensus does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
