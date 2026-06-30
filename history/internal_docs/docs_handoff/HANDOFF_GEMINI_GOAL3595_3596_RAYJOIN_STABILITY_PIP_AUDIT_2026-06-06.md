# Handoff: Gemini Review For Goal3595/Goal3596 RayJoin Stability And PIP Route Audit

Please perform a read-only independent review of Goal3595 and Goal3596 and write the review to:

`docs/reviews/goal3597_gemini_review_goal3595_3596_rayjoin_public_cdb_stability_pip_audit_2026-06-06.md`

## Context

Goal3595 reran the bounded public-CDB Goal3593 probe with `repeat=200` and `warmup=5` from a fresh clean A5000 checkout, addressing the git-cleanliness concern raised in the Goal3594 Gemini review.

Goal3596 audited existing PIP routes on the same public-CDB slice. It found:

- CuPy dense CUDA-core PIP count remains fastest for scalar PIP count.
- RTDL/OptiX exact prepared count is the best current RTDL-only scalar PIP count route.
- The OptiX-candidate-plus-CuPy-refiner path is correct but slower for scalar count-only PIP.
- The fast device-filtered modes fail closed on this slice because they do not match exact positive-membership semantics.

## Files To Read

- `docs/reports/goal3595_rayjoin_public_cdb_long_repeat_stability_2026-06-06.md`
- `docs/reports/goal3595_rayjoin_public_cdb_repeat200_a5000/summary.json`
- `tests/goal3595_rayjoin_public_cdb_long_repeat_stability_test.py`
- `docs/reports/goal3596_rayjoin_public_cdb_pip_route_audit_2026-06-06.md`
- `tests/goal3596_rayjoin_public_cdb_pip_route_audit_test.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md`
- `docs/reviews/goal3594_gemini_review_goal3593_rayjoin_public_cdb_cupy_same_contract_2026-06-06.md`

## Review Questions

1. Does Goal3595 adequately address the prior git-cleanliness concern by using a fresh clean checkout and enforcing `git_status_short == ""`?
2. Are the Goal3595 long-repeat numbers accurately reported from the artifact, including totals, medians, count parity, and boundaries?
3. Is Goal3596's PIP route conclusion supported by the measured existing-route probes?
4. Is the README guidance now clear for three cases: public-CDB mixed routes, no-partner RTDL-only PIP scalar count, and richer candidate-plus-refiner PIP workflows?
5. Do Goal3595/Goal3596 avoid overclaiming release, RayJoin reproduction, broad RT-core speedup, whole-app speedup, zero-copy, or automatic-dispatch authority?
6. What concrete next engineering step should be prioritized before a v2.9 RayJoin performance packet?

## Required Review Shape

- Start with `Verdict: accept`, `Verdict: accept-with-boundary`, `Verdict: needs-more-evidence`, or `Verdict: reject`.
- Lead with findings ordered by severity.
- Include file-level references.
- State that this is an independent Gemini review, distinct from Codex.
- Do not edit source or report files except for writing the review path above.
