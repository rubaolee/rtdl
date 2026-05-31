# Handoff - Goal2781 Grouped Vector-Sum Adapter Review

Please perform an independent read-only review of Goal2781 and write the result
to:

`docs/reviews/goal2781_gemini_review_grouped_vector_sum_adapter_2026-05-31.md`

## Files To Inspect

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/adapters/reductions.py`
- `tests/goal2781_grouped_vector_sum_adapter_test.py`
- `docs/reports/goal2781_grouped_vector_sum_adapter_2026-05-31.md`
- `docs/reports/goal2781_pod_artifacts/goal2781_grouped_vector_sum_adapter_pod_69_30_85_171_2026-05-31.json`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does `grouped_vector_sum_2d_partner_columns` remain generic and app-agnostic?
2. Does the Triton branch route through the declared generic operation
   `grouped_vector_sum_f64x2` without replacing RTDL/OptiX traversal?
3. Do the Torch/CuPy branches preserve same-contract partner-owned column
   behavior without implying that Torch is the neutral buffer protocol?
4. Is the negative pod performance evidence recorded honestly, especially the
   finding that current Triton is correct but 4x-17x slower than Torch?
5. Are all public speedup, RT-core, true-zero-copy, whole-app, and release
   claims still blocked?
6. Are the tests sufficient for this narrow adapter wiring slice?

## Expected Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.

This is not a release gate. It is a narrow v2.5 adapter-integration review.
