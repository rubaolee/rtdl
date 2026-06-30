# Goal582: Apple RT Full-Surface Compatibility Dispatch

Status: implemented, external AI reviewed, accepted

Date: 2026-04-18 local EDT

## Scope

User goal: make the Apple RT backend support all RTDL features/workloads.

The honest implementation boundary is:

- `run_apple_rt` is now callable for all 18 current RTDL predicates on Apple
  Silicon macOS after `make build-apple-rt`.
- 3D `ray_triangle_closest_hit` remains the only native Apple Metal/MPS RT path.
- All other predicates currently execute through CPU Python reference
  compatibility dispatch and are explicitly marked `cpu_reference_compat`.
- `run_apple_rt(..., native_only=True)` rejects compatibility paths instead of
  silently pretending they are Apple hardware execution.

This goal is therefore a full public-dispatch coverage step, not full native
Apple RT backend parity.

## Code Changes

- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
  - added `APPLE_RT_NATIVE_PREDICATES`
  - added `APPLE_RT_COMPATIBILITY_PREDICATES`
  - added `apple_rt_predicate_mode(predicate_name)`
  - added `apple_rt_support_matrix()`
  - extended `run_apple_rt(..., native_only=False, **inputs)`
  - kept native 3D closest-hit on Apple Metal/MPS
  - routed non-native supported predicates through CPU Python reference
    compatibility after requiring the Apple RT library/runtime to load
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
  - exported `apple_rt_predicate_mode`
  - exported `apple_rt_support_matrix`
  - added both names to `__all__` after Gemini noted the omission
- `/Users/rl2025/rtdl_python_only/tests/goal582_apple_rt_full_surface_dispatch_test.py`
  - added full-surface dispatch parity test for all 18 current predicates
  - added support-matrix mode test
  - added `native_only=True` rejection test for compatibility paths

## Predicate Coverage

Goal582 tests these 18 predicates through `run_apple_rt`:

- `bfs_discover`
- `bounded_knn_rows`
- `conjunctive_scan`
- `fixed_radius_neighbors`
- `grouped_count`
- `grouped_sum`
- `knn_rows`
- `overlay_compose`
- `point_in_polygon`
- `point_nearest_segment`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`
- `ray_triangle_closest_hit`
- `ray_triangle_hit_count`
- `segment_intersection`
- `segment_polygon_anyhit_rows`
- `segment_polygon_hitcount`
- `triangle_match`

Mode classification:

- `ray_triangle_closest_hit`: `native_mps_rt` for 3D Ray3D/Triangle3D data
- all other listed predicates: `cpu_reference_compat`

## Test Evidence

Focused Apple RT plus Goal582 test:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Result:

```text
Ran 7 tests in 0.014s
OK
```

Post-review Goal582-focused rerun after the `__all__` export fix:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Result:

```text
Ran 3 tests in 0.009s
OK
```

Full default local suite:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 239 tests in 61.755s
OK
```

Compile check:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m compileall -q src/rtdsl tests/goal582_apple_rt_full_surface_dispatch_test.py
```

Result: pass.

External review evidence:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal582_gemini_flash_review_2026-04-18.md`: ACCEPT
- `/Users/rl2025/rtdl_python_only/docs/reports/goal582_claude_review_2026-04-18.md`: ACCEPT

Gemini observed that `apple_rt_predicate_mode` and
`apple_rt_support_matrix` were imported but missing from `__all__`; this was
fixed after the review.

## Documentation Updates

Public docs were updated to distinguish native Apple RT from compatibility
dispatch:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`

## Honesty Boundary

Correct public statement after Goal582:

> On Apple Silicon macOS, `run_apple_rt` can execute all current RTDL predicates
> through a single public dispatcher. Only 3D `ray_triangle_closest_hit` is
> currently native Apple Metal/MPS RT execution; the other predicates are
> compatibility dispatch through the CPU Python reference path.

Incorrect public statements after Goal582:

- Apple RT has full native backend parity.
- Apple RT hardware accelerates all RTDL workloads.
- Apple RT has measured speedup beyond the closest-hit slice.
- Apple RT supports non-macOS platforms.
- Apple RT prepared reuse exists.

## Current Verdict

Codex local verdict: ACCEPT as a full-surface dispatch coverage step with
explicit native-versus-compatibility mode boundaries.

External AI consensus: ACCEPT from Gemini Flash and Claude.
