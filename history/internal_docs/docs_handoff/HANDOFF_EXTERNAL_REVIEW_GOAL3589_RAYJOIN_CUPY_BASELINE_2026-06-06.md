# Handoff: External Review Of Goal3589 RayJoin CuPy Same-Contract Baseline

Please perform a read-only review and save the result to:

`docs/reviews/goal3590_claude_review_goal3589_rayjoin_cupy_same_contract_baseline_2026-06-06.md`

## Files To Read

- `scripts/goal3589_rayjoin_cupy_same_contract_baseline.py`
- `tests/goal3589_rayjoin_cupy_same_contract_baseline_test.py`
- `docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_2026-06-06.md`
- `docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_a5000/summary.json`
- `docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_stress_a5000/summary.json`
- For context only: `docs/reports/goal3586_rayjoin_composite_score_from_hot_promoted_routes_2026-06-06.md`

## Review Questions

1. Does the Goal3589 script correctly define the CuPy rows as non-RT,
   same-contract, user/partner CUDA-core baselines rather than RTDL engine work?
2. Do the A5000 artifacts support the report's main conclusion: RTDL/OptiX wins
   stress LSI against dense CuPy, but loses PIP and overlay active-count to
   warmed dense CuPy on the simple authored tiled fixtures?
3. Are the result boundaries honest, especially that Goal3586 remains valid only
   as an Embree-vs-OptiX packet and Goal3589 blocks public RayJoin RT-core
   speedup wording against serious CUDA-core baselines?
4. Are there any measurement-contract problems, unfair exclusions, count/parity
   gaps, or suspicious timings that should be marked as blockers before using
   Goal3589 as internal benchmark guidance?

## Expected Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please lead with findings, cite file paths and concrete values, and keep all
release / public speedup / RayJoin-paper claims blocked unless the evidence
strictly authorizes them.
