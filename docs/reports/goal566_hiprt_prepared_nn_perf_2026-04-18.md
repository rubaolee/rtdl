# Goal 566: HIPRT Prepared 3D Nearest-Neighbor Performance Round

Date: 2026-04-18

## Scope

Goal 566 is the second v0.9 performance-improvement round after Goal 565. It extends the prepared-execution model from 3D ray/triangle hit-count to 3D fixed-radius nearest-neighbor search.

The implementation keeps the RTDL public model unchanged:

- App/kernel authors still write the standard ITRE kernel with `rt.fixed_radius_neighbors(radius=..., k_max=...)`.
- One-shot execution remains available through `rt.run_hiprt(...)`.
- Prepared execution is available through `rt.prepare_hiprt(..., search_points=...)`, then repeated `prepared.run(query_points=...)` calls.

## Implementation Summary

Files changed:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_hiprt.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal566_hiprt_prepared_nn_test.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal566_hiprt_prepared_nn_perf.py`

Native HIPRT now has a prepared 3D point-set context that owns:

- HIPRT runtime/context
- uploaded build/search points
- expanded point AABBs for the fixed radius
- HIPRT AABB geometry
- HIPRT function table using `intersectRtdlPointRadius3D`
- compiled `RtdlFixedRadiusNeighbors3DKernel`
- fixed-radius parameter buffer

Prepared query calls now only upload the probe/query points, allocate bounded output/count buffers, launch the already-compiled traversal kernel, and compact result rows.

## Correctness Evidence

Local macOS import/discovery check:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal566_hiprt_prepared_nn_test tests.goal548_hiprt_fixed_radius_3d_test tests.goal549_hiprt_3d_knn_test
Ran 9 tests ... OK (skipped=8)
```

Linux HIPRT execution check:

```text
cd /tmp/rtdl_goal566_prepared_nn
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 -m unittest tests.goal566_hiprt_prepared_nn_test tests.goal548_hiprt_fixed_radius_3d_test tests.goal549_hiprt_3d_knn_test
Ran 9 tests in 4.672s
OK
```

The Goal 566 tests verify:

- direct prepared helper parity with the CPU reference across multiple query batches
- high-level `rt.prepare_hiprt(...)` parity with the CPU reference across multiple query batches
- existing one-shot fixed-radius and 3D KNN tests still pass

## Linux Performance Evidence

Raw JSON:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal566_hiprt_prepared_nn_perf_linux_2026-04-18.json`

Fixture:

- 1024 query points
- 4096 search points
- radius `1.05`
- `k_max=16`
- 2238 output rows
- 5 prepared-query repeats

Median timings:

| Path | Median seconds | Correct vs CPU |
|---|---:|---|
| CPU Python reference | 0.878435 | reference |
| Embree one-shot | 0.021408 | PASS |
| OptiX one-shot | 0.483871 | PASS |
| Vulkan one-shot | 0.256358 | PASS |
| HIPRT one-shot | 0.598071 | PASS |
| HIPRT prepare/build | 0.548071 | build phase |
| HIPRT prepared query | 0.003533 | PASS |

Computed one-shot HIPRT to prepared HIPRT query speedup:

```text
0.598071 / 0.003533 = 169.30x
```

## Interpretation

This result confirms the same performance pattern as Goal 565: HIPRT cold one-shot calls are dominated by runtime/build/JIT overhead, but repeated query calls become fast once the build-side geometry and kernel are reused.

The performance claim is deliberately bounded:

- This is a genuine HIPRT ray-tracing traversal path over prepared 3D point AABBs.
- This is a repeated-query improvement, not a cold-call improvement.
- This is not yet prepared coverage for 2D neighbors, KNN rank helpers, graph CSR, DB tables, AMD GPUs, or RT-core acceleration.
- Embree remains faster on this one-shot CPU-oriented fixture.

## Verdict

Goal 566 is technically implemented and validated on Linux for prepared 3D fixed-radius nearest-neighbor reuse.

## AI Review Consensus

Review artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal566_external_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal566_gemini_flash_review_2026-04-18.md`

Claude initially rejected Goal 566 because public docs still described
`prepare_hiprt` as ray/triangle-only. The stale statements were corrected in
the public docs, and Claude re-reviewed the fixed state with final verdict
`ACCEPT`. Gemini Flash also returned `ACCEPT`. Codex accepts the goal with the
same bounded performance interpretation.

Recommended next prepared-performance targets:

- prepared 2D neighbor build sets
- prepared graph CSR for BFS and triangle-match
- prepared DB row/table buffers for v0.7 database workloads
