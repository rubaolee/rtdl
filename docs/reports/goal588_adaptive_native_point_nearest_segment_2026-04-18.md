# Goal588: Adaptive Native Point-Nearest-Segment

Status: accepted, 3-AI implementation consensus reached

Date: 2026-04-18 local EDT

Consensus:

- Codex: ACCEPT, focused correctness and bounded local performance evidence
  pass.
- Gemini Flash: ACCEPT in
  `/Users/rl2025/rtdl_python_only/docs/reports/goal588_gemini_flash_review_2026-04-18.md`.
- Claude: ACCEPT in
  `/Users/rl2025/rtdl_python_only/docs/reports/goal588_claude_review_2026-04-18.md`.

## Purpose

Goal588 promotes `point_nearest_segment` from compatibility dispatch to a native
adaptive C++ path.  This starts the nearest-neighbor family with a narrow,
measurable workload before broader radius/KNN kernels are attempted.

## Files Changed

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_adaptive.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/adaptive_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/goal585_adaptive_backend_skeleton_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal588_adaptive_native_point_nearest_segment_test.py`

## Native Path

Native mode:

```text
native_adaptive_cpu_soa_min_distance_2d
```

The C++ implementation reuses the adaptive segment SoA layout:

- segment IDs
- segment base coordinates
- segment direction vectors

The hot loop then:

1. stages the build-side segments once
2. computes per-point nearest segment in native C++
3. uses squared distances inside the loop
4. applies the same tie rule as the Python reference: lower distance first,
   lower segment ID on equal distance
5. emits one row per point when the segment set is non-empty

This is an adaptive CPU-native path, not a vendor RT API path.

## Runtime Behavior

If `librtdl_adaptive` is built:

- `rt.adaptive_predicate_mode(point_nearest_segment_kernel)` returns
  `mode="native_adaptive_cpu_soa_min_distance_2d"` and `native=True`
- `rt.run_adaptive(...)` uses the native C++ path for `point_nearest_segment`

If the library is not built:

- `run_adaptive` remains callable
- `point_nearest_segment` falls back to `cpu_reference_compat`
- no native-performance claim is exposed

## Correctness Test

Command:

```bash
make build-adaptive
PYTHONPATH=src:. python3 -m unittest \
  tests.goal585_adaptive_backend_skeleton_test \
  tests.goal586_adaptive_native_ray_hitcount_test \
  tests.goal587_adaptive_native_segment_intersection_test \
  tests.goal588_adaptive_native_point_nearest_segment_test -v
```

Result:

```text
Ran 5 tests in 0.007s

OK
```

The focused tests verify:

- the 18-workload support matrix is still intact
- `point_nearest_segment` upgrades to native only when the adaptive library is
  built
- native adaptive rows match `run_cpu_python_reference`

## Local Performance Smoke

Raw JSON:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal588_adaptive_native_point_nearest_segment_perf_macos_2026-04-18.json
```

Fixture:

- host: local macOS
- points: `1024`
- segments: `2048`
- candidate pairs: `2097152`
- result rows: `1024`
- repeats: `5`
- correctness parity: `true`

Median timing:

| Path | Median seconds |
| --- | ---: |
| `run_adaptive`, native C++ `native_adaptive_cpu_soa_min_distance_2d` | `0.005314250010997057` |
| `run_cpu_python_reference` | `0.5915607910137624` |

Interpretation:

- This proves the third adaptive native path removes Python from the hot loop.
- The result supports the branch/cache direction: reusable build-side SoA
  segment columns plus a predictable min-distance loop.
- This does not prove broad nearest-neighbor family speedup.
- This does not compare against SciPy, FAISS, Embree, OptiX, Vulkan, HIPRT, or
  Apple RT.

## Boundary

Goal588 implements native adaptive `point_nearest_segment` only.  Fixed-radius
neighbors and KNN remain compatibility mode until separate goals promote them
with their own correctness and performance evidence.

The unrelated dirty Apple RT experiment remains outside this goal.
