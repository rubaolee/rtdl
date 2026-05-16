# Gemini Review Task: Goal2112 Hausdorff v2.0 Language Lab

Please perform an independent read-only review of Goal2112 and write your review
to:

`docs/reviews/goal2113_gemini_review_goal2112_hausdorff_language_lab_2026-05-15.md`

Context:

- Goal2112 treats RTDL v2.0 as a programming-language/runtime test by
  implementing exact 2-D Hausdorff Distance and comparing it against OpenMP
  C++, CUDA C++, CuPy RawKernel, RTDL+CuPy, RTDL/OptiX threshold search, and
  RTDL/OptiX exact nearest witness.
- The goal is not to claim X-HD-level performance. The intended conclusion is
  that RTDL v2 can express and validate the algorithm, while the RT-core path
  still needs X-HD-style grid grouping, estimator pruning, and heavy-cell
  continuation before speedup claims are justified.

Files to inspect:

- `examples/rtdl_hausdorff_v2_function.py`
- `examples/rtdl_hausdorff_v2_language_lab.py`
- `docs/reports/goal2112_hausdorff_v2_language_lab_2026-05-15.md`
- `docs/reports/hausdorff_v2_language_lab_local_optix_512.json`
- `docs/reports/hausdorff_v2_language_lab_local_optix_2048.json`
- `docs/reports/hausdorff_v2_language_lab_local_optix_8192.json`
- `tests/goal2110_hausdorff_exact_rt_nearest_witness_test.py`
- `tests/goal2112_hausdorff_v2_language_lab_test.py`
- Existing Goal2110 report/review for context.

Review questions:

1. Does the lab correctly distinguish exact RTDL+CuPy from RTDL/OptiX RT-core
   methods?
2. Do the artifacts support the correctness claim versus OpenMP/CUDA/CuPy
   baselines?
3. Does the report avoid claiming broad RT-core speedup or X-HD parity?
4. Is the threshold-seeded witness radius a reasonable user-level algorithmic
   improvement that keeps the native engine app-agnostic?
5. What remains before this can become a strong v2.0 performance story?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. This should be read-only except writing the review file.
