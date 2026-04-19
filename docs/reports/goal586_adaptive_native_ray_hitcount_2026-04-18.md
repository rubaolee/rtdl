# Goal586: Adaptive Native 3D Ray/Triangle Hit-Count

Status: accepted, 3-AI implementation consensus reached

Date: 2026-04-18 local EDT

Consensus:

- Codex: ACCEPT, focused correctness and bounded local performance evidence
  pass.
- Gemini Flash: ACCEPT in
  `/Users/rl2025/rtdl_python_only/docs/reports/goal586_gemini_flash_review_2026-04-18.md`.
- Claude: ACCEPT in
  `/Users/rl2025/rtdl_python_only/docs/reports/goal586_claude_review_2026-04-18.md`.

Post-review fix:

- Claude noted that `rtdl_adaptive_free_rows` should carry
  `RTDL_ADAPTIVE_EXPORT` to avoid a future hidden-symbol break if the build is
  hardened with `-fvisibility=hidden`; this was fixed before commit.

## Purpose

Goal586 starts native adaptive backend implementation after the Goal585
compatibility skeleton.  The first native slice is deliberately narrow:
`ray_triangle_hit_count_3d`.

## Files Changed

- `/Users/rl2025/rtdl_python_only/Makefile`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_adaptive.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/adaptive_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal585_adaptive_backend_skeleton_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal586_adaptive_native_ray_hitcount_test.py`

## Native Path

New build target:

```bash
make build-adaptive
```

Built artifact on macOS:

```text
/Users/rl2025/rtdl_python_only/build/librtdl_adaptive.dylib
```

Native mode:

```text
native_adaptive_cpu_soa_3d
```

The C++ implementation stages triangles into a structure-of-arrays working set:

- triangle IDs
- base vertex columns
- `edge1` columns
- `edge2` columns

The hot loop then evaluates finite ray/triangle hits using the staged triangle
columns.  This is an adaptive CPU-native path, not a vendor RT API path.

## Runtime Behavior

If `librtdl_adaptive` is built:

- `rt.adaptive_available()` returns `True`
- `rt.adaptive_version()` returns `(0, 1, 0)`
- `rt.adaptive_predicate_mode(ray_triangle_hit_count_3d_kernel)` returns
  `mode="native_adaptive_cpu_soa_3d"` and `native=True`
- `rt.run_adaptive(...)` uses the native C++ path for 3D ray/triangle hit-count

If the library is not built:

- the same public API remains available
- the workload falls back to `cpu_reference_compat`
- no fake native-performance claim is exposed

## Correctness Test

Command:

```bash
make build-adaptive
PYTHONPATH=src:. python3 -m unittest \
  tests.goal585_adaptive_backend_skeleton_test \
  tests.goal586_adaptive_native_ray_hitcount_test -v
```

Result:

```text
Ran 3 tests in 0.002s

OK
```

The focused tests verify:

- the 18-workload Goal585 support matrix still exists
- the built native library upgrades only `ray_triangle_hit_count_3d`
- native mode metadata is visible
- native adaptive rows match `run_cpu_python_reference`

## Local Performance Smoke

Raw JSON:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal586_adaptive_native_ray_hitcount_perf_macos_2026-04-18.json
```

Fixture:

- host: local macOS
- rays: `512`
- triangles: `1024`
- candidate pairs: `524288`
- repeats: `5`
- correctness parity: `true`

Median timing:

| Path | Median seconds |
| --- | ---: |
| `run_adaptive`, native C++ `native_adaptive_cpu_soa_3d` | `0.002294874982908368` |
| `run_cpu_python_reference` | `0.2392301670042798` |

Interpretation:

- This proves the first adaptive native path removes Python from the hot loop.
- This does not prove broad adaptive backend speedup across the 18-workload
  matrix.
- This does not compare against Embree, Apple RT, OptiX, Vulkan, or HIPRT yet.
  Those comparisons remain later performance gates.

## Boundary

This goal implements native adaptive 3D hit-count only.  The Goal584 proposal
also named closest-hit as part of the ray/triangle family; closest-hit remains
future work and must not be claimed as native adaptive support from Goal586.

The unrelated dirty Apple RT experiment remains outside this goal.
