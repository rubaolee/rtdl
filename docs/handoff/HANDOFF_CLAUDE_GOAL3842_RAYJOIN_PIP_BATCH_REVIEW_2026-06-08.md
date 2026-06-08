# Handoff: Claude Review For Goal3842 RayJoin PIP Batch Refresh

Please perform an independent read-only review of Goal3842 and save your review
to:

`docs/reviews/goal3843_claude_review_goal3842_rayjoin_pip_batch_executor_2026-06-08.md`

## Files To Inspect

- `docs/reports/goal3842_rayjoin_pip_batch_executor_current_refresh_2026-06-08.md`
- `docs/reports/goal3842_rayjoin_pip_batch_executor_current_a5000/summary.json`
- `tests/goal3842_rayjoin_pip_batch_executor_current_refresh_test.py`
- `src/rtdsl/v2_9_benchmark_adequacy.py`
- `docs/learn/benchmark_partner_reference_matrix.md`
- `docs/learn/partner_choice_for_custom_logic.md`
- Optional context:
  - `docs/reports/goal3834_rayjoin_public_cdb_numba_pip_partner_baseline_2026-06-07.md`
  - `docs/reports/goal3841_rayjoin_pip_contract_boundary_correction_2026-06-08.md`
  - `docs/reports/goal3312_prepared_point_batch_graph_negative_probe_2026-06-04.md`

## Review Questions

1. Does Goal3842 correctly distinguish one-shot bounded public-CDB PIP from
   resident repeated-request PIP throughput?
2. Does the artifact support the report's count, timing, and `~9.04x`
   per-request batching statement?
3. Does the report correctly record the `RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS=1e-9`
   requirement without turning it into hidden auto-dispatch?
4. Is the CUDA-graph replay path kept blocked after the current zero-count
   smoke, with no performance claim based on graph replay?
5. Do the learner docs and adequacy metadata avoid public speedup, RayJoin
   reproduction, broad RT-core, true-zero-copy, automatic partner selection, or
   universal PIP-dominance claims?

## Required Review Shape

Lead with findings, ordered by severity. Use one of the project verdicts:
`accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

If accepted, state the exact boundary: this is internal current-main evidence
for a generic prepared point/closed-shape batch-count executor, not a release
claim, not one-shot PIP latency, and not a RayJoin paper reproduction.
