# Goal652: Apple RT 2D Native-Assisted Any-Hit

Date: 2026-04-20

## Verdict

Codex local verdict: ACCEPT.

Consensus:

- Codex: ACCEPT
- Claude: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal652_claude_review_2026-04-20.md`
- Gemini 2.5 Flash: ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal652_gemini_flash_review_2026-04-20.md`

Goal652 moves Apple RT 2D `ray_triangle_any_hit` from stale-library
compatibility projection to a native-assisted Apple Metal/MPS traversal path
when `librtdl_apple_rt` is rebuilt from current source.

## Implementation

- Added `rtdl_apple_rt_run_ray_anyhit_2d(...)` in
  `/Users/rl2025/rtdl_python_only/src/native/apple_rt/rtdl_apple_rt_mps_geometry.mm`.
- The implementation reuses the established Apple 2D ray/triangle prism
  encoding:
  - each 2D triangle is extruded into a small 3D prism;
  - `MPSRayIntersector` runs nearest-intersection traversal with primitive
    masks;
  - each MPS candidate is checked by exact RTDL 2D ray/triangle acceptance;
  - once a ray has an accepted 2D hit, its mask is cleared and that ray is not
    searched in later passes/chunks.
- Added Python `ctypes` registration and dispatch in
  `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`.
- `run_apple_rt(..., native_only=True)` now prefers:
  - `rtdl_apple_rt_run_ray_anyhit_2d` for `Ray2D/Triangle2D`;
  - `rtdl_apple_rt_run_ray_anyhit_3d` for `Ray3D/Triangle3D`;
  - hit-count projection only as a stale-library fallback when symbols are
    absent.
- Updated Apple RT support-matrix wording to say 2D any-hit is MPS prism
  traversal with per-ray early-exit plus exact 2D acceptance.

## Tests

Added:

- `/Users/rl2025/rtdl_python_only/tests/goal652_apple_rt_2d_anyhit_native_test.py`

Updated:

- `/Users/rl2025/rtdl_python_only/tests/goal603_apple_rt_native_contract_test.py`

Local commands:

```text
make build-apple-rt
```

Result: OK.

```text
nm -gU build/librtdl_apple_rt.dylib | rg 'rtdl_apple_rt_run_ray_anyhit_2d|rtdl_apple_rt_run_ray_anyhit_3d'
```

Result:

```text
000000000000a724 T _rtdl_apple_rt_run_ray_anyhit_2d
0000000000006564 T _rtdl_apple_rt_run_ray_anyhit_3d
```

```text
PYTHONPATH=src:. RTDL_APPLE_RT_LIB=$PWD/build/librtdl_apple_rt.dylib python3 -m unittest tests.goal636_backend_any_hit_dispatch_test tests.goal651_apple_rt_3d_anyhit_native_test tests.goal652_apple_rt_2d_anyhit_native_test tests.goal603_apple_rt_native_contract_test -v
```

Result: 15 tests OK, 4 skips for unavailable non-macOS local GPU backends.

```text
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py tests/goal652_apple_rt_2d_anyhit_native_test.py
```

Result: OK.

```text
PYTHONPATH=src:. python3 -m unittest tests.goal512_public_doc_smoke_audit_test tests.goal646_public_front_page_doc_consistency_test tests.goal510_app_perf_doc_refresh_test tests.goal603_apple_rt_native_contract_test tests.goal645_v0_9_5_release_package_test -v
```

Result: 17 tests OK.

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result: valid true, 248 public commands across 14 docs.

```text
PYTHONPATH=src:. RTDL_APPLE_RT_LIB=$PWD/build/librtdl_apple_rt.dylib python3 -m unittest discover -s tests -p '*_test.py' -v
```

Result: 1225 tests OK, 180 skips.

External review notes:

- Gemini's first pass identified one stale contradiction in
  `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`; that was
  fixed before the final Gemini ACCEPT verdict.
- Claude found no blockers and confirmed the implementation is genuine
  MPS-backed traversal with per-ray early-exit and honest documentation.

## Documentation

Updated public-facing docs to remove the stale current-main claim that Apple RT
2D any-hit is only compatibility projection:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/features/ray_tri_anyhit/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/visibility_rows/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/feature_quickstart_cookbook.md`

## Honesty Boundary

- This is Apple Metal/MPS RT-backed/native-assisted traversal, not programmable
  shader-level any-hit.
- Exact 2D acceptance remains CPU-side after MPS prism candidate discovery.
- No Apple speedup claim is made here.
- Stale `librtdl_apple_rt` binaries without the new symbol still fall back to
  hit-count projection.
