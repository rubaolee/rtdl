# Handoff: Claude Review For Goals 3036-3040

Please perform an independent Claude review of the Goal3036-Goal3040 chain in the RTDL repository.

## Required Output

Write the review to:

`docs/reviews/goal3041_claude_review_goal3036_3040_numba_hausdorff_2026-06-02.md`

Use exactly one of these verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

The review should explicitly state that it is an independent Claude review distinct from Codex and Gemini. It should not claim final release consensus by itself.

## Scope To Review

Please inspect the current repository state and the following files:

- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- `src/rtdsl/v2_6_roadmap.py`
- `docs/reports/goal3036_numba_global_argmax_block_reduce_hardening_2026-06-02.md`
- `docs/reports/goal3037_point_group_nearest_numba_argmax_a4000_pod_2026-06-02.md`
- `docs/reports/goal3037_point_group_nearest_numba_argmax_a4000_pod_2026-06-02.json`
- `docs/reports/goal3039_hausdorff_device_columns_numba_argmax_strategy_2026-06-02.md`
- `docs/reports/goal3040_hausdorff_device_columns_numba_argmax_a4000_perf_2026-06-02.md`
- `docs/reports/goal3040_hausdorff_device_columns_numba_argmax_a4000_perf_2026-06-02.json`
- `tests/goal3036_numba_global_argmax_block_reduce_hardening_test.py`
- `tests/goal3037_point_group_nearest_numba_argmax_a4000_pod_test.py`
- `tests/goal3039_hausdorff_device_columns_numba_argmax_strategy_test.py`
- `tests/goal3040_hausdorff_device_columns_numba_argmax_a4000_perf_test.py`

## Questions To Answer

1. Does Goal3036 correctly harden the Numba global argmax path by replacing fragile global atomic behavior with a generic block-reduce strategy?
2. Does Goal3037 provide valid clean-source RTX A4000 evidence that RTDL OptiX device columns can feed the Numba grouped argmax continuation with exact parity against the raw row-view oracle?
3. Does Goal3039 wire that composition into the Hausdorff benchmark as app-level Python strategy only, without adding app-specific native engine behavior?
4. Does Goal3040 correctly interpret the measured performance result as a negative speed result for the full witness-column plus Numba global-reduction strategy, rather than as a speedup?
5. Is the proposed next direction technically justified: a generic device-resident active-set / candidate-frontier primitive with witness selection, instead of merely downloading full columns and reducing them?
6. Are the claim boundaries intact? In particular, the review should reject any release, public speedup, true-zero-copy, broad RT-core acceleration, or automatic partner-selection claim if the evidence does not support it.

## Review Expectations

- This should be a read-only technical audit except for writing the requested review file.
- Ground findings in code and report evidence, with file references where useful.
- If tests are run, include the exact command and result.
- State any remaining risks clearly, especially whether the Numba dependency/toolchain and the RTX A4000 pod result are sufficient only for this narrow composition lane.
- Do not continue implementation work.
