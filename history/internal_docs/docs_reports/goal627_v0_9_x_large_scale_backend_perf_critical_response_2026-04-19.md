# Goal 627: v0.9.x Large-Scale Backend Performance Critical Response

Date: 2026-04-19

Repository: `/Users/rl2025/rtdl_python_only`

## Input

This response handles a user-supplied external performance summary for a
large-scale Linux comparison across OptiX, Vulkan, and HIPRT. The summary
reported:

- database scan over 5M rows: OptiX `46.2s`, Vulkan `46.5s`, HIPRT `51.9s`
- graph BFS over 5M edges: OptiX `3.14s`, Vulkan `3.18s`, HIPRT failed with
  `std::bad_alloc`
- interpretation: Vulkan was approximately OptiX-parity on the tested NVIDIA
  host, HIPRT carried overhead on the NVIDIA/CUDA/Orochi path, and HIPRT graph
  memory scaling was weak

The summary appears to refer to a "Goal561 mega-performance" style artifact,
but no committed `goal561_linux_three_way_large_perf.py` or final mega report
exists in this checkout. Therefore this response treats the supplied numbers as
external input to be documented and bounded, not as a newly canonical raw
benchmark artifact.

## Current Canonical Evidence

The committed canonical v0.9 HIPRT release evidence remains:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal560_hiprt_backend_perf_compare_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal560_hiprt_backend_perf_compare_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal565_hiprt_prepared_ray_perf_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal566_hiprt_prepared_nn_perf_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal567_hiprt_prepared_graph_perf_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal568_hiprt_prepared_db_perf_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`

Goal560 proves release-smoke correctness and availability across 18 workloads
and four backends. It explicitly says the one-repeat small-fixture timings are
not throughput benchmarks and not speedup claims.

## Critical Findings

1. The large-scale results are plausible and important, but they must not be
   mislabeled. The tested HIPRT path is HIPRT/Orochi CUDA mode on NVIDIA. It is
   not AMD GPU validation.

2. Vulkan parity with OptiX on the reported large database and BFS tests is a
   serious architectural signal. Vulkan should stay a first-class open GPU
   performance path. This does not by itself justify removing OptiX, because
   OptiX remains the NVIDIA-specific RT backend and has feature/runtime
   differences that are still useful for RTDL.

3. HIPRT `std::bad_alloc` on the large graph BFS case is a real scaling
   warning. It means current HIPRT graph support is correctness-credible but
   not yet memory-scalable enough for a graph performance claim.

4. The DB timings indicate that HIPRT is not performance-leading on the
   reported large scan. Current prepared DB evidence remains useful for
   repeated-query setup amortization, but it is not a general DB throughput or
   arbitrary-SQL claim.

5. The correct engineering response is not to drop backends immediately. The
   correct response is to document the scaling boundary, prioritize Vulkan and
   prepared/chunked execution for performance work, and require HIPRT memory
   profiling before any large-graph claim.

## Actions Taken

Updated:

- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`

The updates add the missing public-doc boundary:

- Vulkan is a serious open GPU performance path where the reported large-scale
  evidence shows parity with OptiX.
- HIPRT remains real and correctness-focused, but not performance-leading.
- HIPRT large graph scalability is explicitly not claimed after the reported
  `std::bad_alloc`.
- HIPRT-on-NVIDIA/CUDA/Orochi measurements must not be presented as AMD GPU
  results.

## External v0.9.4 Blocker Cross-Check

The working tree also contained an uncommitted external test report revision
claiming macOS test blockers in these test groups:

- `tests.goal15_compare_test`
- `tests.goal17_prepared_runtime_test`
- `tests.goal19_compare_test`
- `tests.report_smoke_test`
- `tests.goal207_knn_rows_external_baselines_test`

Focused local verification in this checkout:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal15_compare_test \
  tests.goal17_prepared_runtime_test \
  tests.goal19_compare_test \
  tests.report_smoke_test \
  tests.goal207_knn_rows_external_baselines_test -v
```

Result:

```text
Ran 20 tests in 30.053s
OK
```

Therefore those blocker claims are not reproduced in the current local
checkout. They should remain treated as external-machine findings unless a
fresh exact environment reproduction is provided.

## Verdict

ACCEPT with caveats.

The current v0.9.x documentation is mostly within the honesty boundary, but it
needed an explicit large-scale backend performance note. That note is now
documented. The supplied performance criticism does not invalidate v0.9.4
correctness or release status, but it creates clear future work:

- keep Vulkan as a priority performance backend
- keep OptiX as the NVIDIA-specific backend
- keep HIPRT as correctness/API coverage until AMD hardware and large-graph
  memory behavior are validated
- add chunked/prepared execution before making any broad DB or graph throughput
  claim
