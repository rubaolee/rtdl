# Goal587: Adaptive Native 2D Segment Intersection

Status: accepted, 3-AI implementation consensus reached

Date: 2026-04-18 local EDT

Consensus:

- Codex: ACCEPT, focused correctness and bounded local performance evidence
  pass.
- Gemini Flash: ACCEPT in
  `/Users/rl2025/rtdl_python_only/docs/reports/goal587_gemini_flash_review_2026-04-18.md`.
- Claude: ACCEPT in
  `/Users/rl2025/rtdl_python_only/docs/reports/goal587_claude_review_2026-04-18.md`.

Post-review fix:

- Claude noted that `bbox_overlap` recomputed left-segment bounds inside the
  inner right-segment loop.  The implementation now computes the left bounds
  once per probe segment before the inner loop.

## Purpose

Goal587 starts the adaptive backend's 2D geometry family by promoting
`segment_intersection` from compatibility dispatch to a native adaptive C++ path.

This follows the Goal584 design: use workload-specific layout and branch/cache
choices instead of forcing every workload through one fixed ray/BVH encoding.

## Files Changed

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_adaptive.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/adaptive_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/goal585_adaptive_backend_skeleton_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal587_adaptive_native_segment_intersection_test.py`

## Native Path

Native mode:

```text
native_adaptive_cpu_soa_2d
```

The C++ implementation stages the build-side segments into SoA columns:

- segment IDs
- base point coordinates
- direction vectors
- bounding boxes

The hot loop then:

1. computes the probe segment direction once
2. rejects non-overlapping bounding boxes before exact math
3. evaluates the exact 2D segment intersection equation only for candidates
   that survive the box test
4. emits `left_id`, `right_id`, and intersection point coordinates

This is an adaptive CPU-native path, not a vendor RT API path.

## Runtime Behavior

If `librtdl_adaptive` is built:

- `rt.adaptive_predicate_mode(segment_intersection_kernel)` returns
  `mode="native_adaptive_cpu_soa_2d"` and `native=True`
- `rt.run_adaptive(...)` uses the native C++ path for `segment_intersection`

If the library is not built:

- `run_adaptive` remains callable
- `segment_intersection` falls back to `cpu_reference_compat`
- no native-performance claim is exposed

## Correctness Test

Command:

```bash
make build-adaptive
PYTHONPATH=src:. python3 -m unittest \
  tests.goal585_adaptive_backend_skeleton_test \
  tests.goal586_adaptive_native_ray_hitcount_test \
  tests.goal587_adaptive_native_segment_intersection_test -v
```

Result:

```text
Ran 4 tests in 0.002s

OK
```

The focused tests verify:

- the 18-workload support matrix is still intact
- `segment_intersection` upgrades to native only when the adaptive library is
  built
- native adaptive rows match `run_cpu_python_reference`

## Local Performance Smoke

Raw JSON:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal587_adaptive_native_segment_intersection_perf_macos_2026-04-18.json
```

Fixture:

- host: local macOS
- left segments: `1024`
- right segments: `2048`
- candidate pairs: `2097152`
- result rows: `2048`
- repeats: `5`
- correctness parity: `true`

Median timing:

| Path | Median seconds |
| --- | ---: |
| `run_adaptive`, native C++ `native_adaptive_cpu_soa_2d` | `0.005515916971489787` |
| `run_cpu_python_reference` | `0.44625949999317527` |

Interpretation:

- This proves the second adaptive native path removes Python from the hot loop.
- The speedup is helped by the native SoA staging and bounding-box reject path.
- This does not prove broad geometry-family speedup.
- This does not compare against Embree, OptiX, Vulkan, HIPRT, or Apple RT.

## Boundary

Goal587 implements native adaptive `segment_intersection` only.  Other 2D
geometry workloads remain compatibility mode until separate goals promote them
with their own correctness and performance evidence.

The unrelated dirty Apple RT experiment remains outside this goal.
