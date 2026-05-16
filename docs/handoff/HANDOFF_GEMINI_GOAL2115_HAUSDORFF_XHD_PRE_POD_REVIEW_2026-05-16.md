# Gemini Review Task: Goal2115 X-HD-Guided Hausdorff Pre-Pod Review

Please perform an independent read-only review of Goal2115 and write your review
to:

`docs/reviews/goal2116_gemini_review_goal2115_hausdorff_xhd_pre_pod_2026-05-16.md`

Context:

- We are preparing for serious RTX pod performance tests of the RTDL v2.0
  Hausdorff Distance application.
- The user wants X-HD used as guidance, not as something we overclaim matching.
- Goal2115 reviews the current design and implementation, removes a stale
  slower helper, and adds `rtdl_rt_nearest_witness_oracle_radius` as a
  diagnostic lower-bound method.

Files to inspect:

- `examples/rtdl_hausdorff_v2_function.py`
- `examples/rtdl_hausdorff_v2_language_lab.py`
- `docs/reports/goal2115_hausdorff_xhd_guided_pre_pod_design_review_2026-05-16.md`
- `docs/reports/hausdorff_v2_language_lab_local_optix_8192_oracle_radius.json`
- `tests/goal2110_hausdorff_exact_rt_nearest_witness_test.py`
- `tests/goal2112_hausdorff_v2_language_lab_test.py`
- `tests/goal2115_hausdorff_xhd_pre_pod_design_review_test.py`

Review questions:

1. Does Goal2115 correctly distinguish current RTDL HD implementation from a
   true X-HD-level algorithm?
2. Is the oracle-radius method clearly diagnostic and not a user-facing speedup
   claim?
3. Does removing the stale `_directed_rt_nearest_witness` helper make sense?
4. Is the pod method set and claim boundary appropriate?
5. Are there any blockers before starting pod performance testing?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. This should be read-only except writing the review file.
