# Gemini Review Task: RTDL v2 User-Level Hausdorff CUDA Benchmark

Please perform a read-only review of the new Hausdorff benchmark lab.

Files to read:

- `examples/rtdl_hausdorff_v2_user_benchmark.py`
- `docs/reports/hausdorff_v2_user_cuda_benchmark_lab_2026-05-15.md`
- `docs/reports/hausdorff_v2_user_benchmark_local_full_8192.json`
- `docs/reports/hausdorff_v2_user_benchmark_local_full_32768.json`
- `docs/reports/hausdorff_v2_user_benchmark_local_full_65536.json`

Review questions:

1. Does the benchmark respect the rule that RTDL v2.0 internals are not changed?
2. Is the distinction clear between:
   - RTDL v2 partner-column user app path,
   - independent OpenMP CPU baseline,
   - independent CUDA C++ baseline,
   - independent CuPy RawKernel baseline,
   - built-in v2 CuPy exact path?
3. Are the correctness claims supported by the JSON artifacts?
4. Are the performance claims bounded correctly, especially avoiding any exact-Hausdorff RT-core claim?
5. Is it fair to say this demonstrates that a user can combine RTDL partner columns with user-owned CUDA/CuPy continuation code?

Please write the review to:

`docs/reviews/hausdorff_v2_user_cuda_benchmark_gemini_review_2026-05-15.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
