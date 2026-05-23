# Goal2477 Codex + Gemini Consensus: Intersection-Direct Grouped-Union Experiment

Date: 2026-05-21

## Consensus

Goal2477 is accepted as an internal, app-agnostic, default-off OptiX grouped-union experiment. The implementation preserves the existing anyhit default path and adds separate execution-option symbols for the opt-in intersection-direct side-effect path.

This is not accepted as a default-path promotion and does not authorize public performance wording.

## Evidence

- Local focused tests: 20 tests OK.
- Local Python compile checks: OK.
- Local `git diff --check`: OK.
- Pod build: `make build-optix` passed on `root@69.30.85.177 -p 22181` with RTX A5000 and CUDA 12.8.
- Pod focused tests: 19 tests OK.
- Tiny direct-side-effect runtime smoke: `matches_reference=true`.
- Same-build pod A/B artifacts:
  - `docs/reports/goal2477_direct_side_effect_ab_off/summary.json`
  - `docs/reports/goal2477_direct_side_effect_ab_on/summary.json`
  - `docs/reports/goal2477_direct_side_effect_scale_131k_off/summary.json`
  - `docs/reports/goal2477_direct_side_effect_scale_131k_on/summary.json`

## Performance Conclusion

The performance result is mixed:

- 32768 points: direct path is slower in both total median and grouped native median.
- 65536 points: direct path is slightly faster in both total median and grouped native median.
- 131072 points: direct path is slower in both total median and grouped native median.
- Signatures match in both A/B configurations.

The evidence supports keeping the direct side-effect path as a default-off diagnostic/experiment only.

## External Review

Gemini review:

- File: `docs/reviews/goal2477_gemini_review_intersection_direct_grouped_union_2026-05-21.md`
- Blocking issues: none.
- Verdict: approved.

Gemini exact-number follow-up:

- File: `docs/reviews/goal2477_gemini_followup_exact_numbers_2026-05-21.md`
- Verdict: accepted.
- Result: report median values match artifact medians when rounded to 10 decimal places.

Gemini exact-number follow-up after the 131k supplement:

- File: `docs/reviews/goal2477_gemini_followup_exact_numbers_with_131k_2026-05-21.md`
- Verdict: accepted.
- Result: report median values for 32768, 65536, and 131072 match artifact medians when rounded to 10 decimal places.

## Claim Boundary

Public performance claims remain blocked. Any future promotion requires stronger positive evidence across representative sizes, correctness validation, and a fresh review/consensus pass.
