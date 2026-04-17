# Codex Consensus: Goal 507 Hausdorff Linux Performance

Date: 2026-04-17

Verdict: ACCEPT

## Reviewed Artifacts

- `/Users/rl2025/rtdl_python_only/examples/rtdl_hausdorff_distance_app.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal507_hausdorff_linux_perf.py`
- `/Users/rl2025/rtdl_python_only/tests/goal507_hausdorff_perf_harness_test.py`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal507_hausdorff_linux_perf_report_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal507_hausdorff_linux_perf_raw_2026-04-17.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal507_hausdorff_linux_perf_20k_raw_2026-04-17.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal507_claude_review_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal507_gemini_review_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL507_SINGLE_SENTENCE_EXTERNAL_REVIEW_REQUEST_2026-04-17.md`

## Consensus

Codex, Claude, and Gemini agree that Goal507 honestly closes the requested
Linux performance check for the v0.8 Hausdorff app:

- The app now exposes `embree`, `optix`, and `vulkan` paths for the same
  two-pass `knn_rows(k=1)` Hausdorff reduction.
- Linux correctness smoke tests passed for all three RTDL backends.
- The raw benchmark JSON covers 1k, 5k, 10k, and 20k points per side.
- The report accurately compares RTDL against SciPy `cKDTree`, scikit-learn
  `NearestNeighbors`, and FAISS `IndexFlatL2` baselines.

## Boundary

The accepted claim is bounded:

- RTDL multi-backend Hausdorff execution works on Linux for this app.
- OptiX/Vulkan strongly outperform RTDL Embree on the measured GTX 1070 host.
- RTDL does not beat mature nearest-neighbor libraries for this exact 2D
  nearest-neighbor Hausdorff benchmark.
- No RT-core acceleration is claimed because the measured GPU is a GTX 1070.

## Validation

Local validation passed:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal507_hausdorff_perf_harness_test tests.goal208_nearest_neighbor_examples_test tests.goal505_v0_8_app_suite_test -v
PYTHONPATH=src:. python3 -m py_compile examples/rtdl_hausdorff_distance_app.py scripts/goal507_hausdorff_linux_perf.py tests/goal507_hausdorff_perf_harness_test.py
git diff --check
```

Linux validation passed on `lestat-lx1` with Embree 4.3.0, OptiX 9.0.0, Vulkan
0.1.0, SciPy 1.17.1, scikit-learn 1.8.0, and FAISS 1.13.2.

No blockers remain for treating Goal507 as the current Hausdorff Linux
large-scale performance evidence package.
