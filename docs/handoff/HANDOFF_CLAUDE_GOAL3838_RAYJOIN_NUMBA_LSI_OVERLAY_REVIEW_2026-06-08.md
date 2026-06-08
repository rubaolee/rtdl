# Handoff: Claude Review Goal3838 RayJoin Numba LSI/Overlay Coverage

Please perform an independent read-only review of Goal3838 on current `main`.

## Scope

Review:

- `scripts/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.py`
- `tests/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline_test.py`
- `docs/reports/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline_2026-06-08.md`
- `docs/reports/goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_a5000/summary.json`
- learner-doc deltas in:
  - `docs/learn/benchmark_partner_reference_matrix.md`
  - `docs/learn/partner_choice_for_custom_logic.md`

## Questions

1. Are the LSI and overlay Numba CUDA JIT kernels same-contract with the existing Goal3589 CuPy RawKernel baselines?
2. Do the A5000 artifact counts and medians support the report's wording?
3. Is the "Numba coverage closed, but primitive-first RTDL/OptiX remains recommended" conclusion correct?
4. Are all claim boundaries intact: no release, no RayJoin paper reproduction, no automatic partner selection, no broad RT-core/zero-copy wording?
5. Is the learner-doc wording precise and not frustrating or misleading for users choosing CuPy vs Numba vs RTDL primitives?

## Required Output

Write your review to:

`docs/reviews/goal3839_claude_review_goal3838_rayjoin_numba_lsi_overlay_2026-06-08.md`

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
