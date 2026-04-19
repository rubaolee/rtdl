# Goal583: Apple RT Native 3D Ray-Triangle Hit-Count

Status: implemented, external AI reviewed, accepted

Date: 2026-04-18 local EDT

## Scope

User requirement: all RTDL workloads must be able to run this Mac RT.

Goal582 made all 18 current predicates callable through `run_apple_rt`, but most
of that coverage was CPU-reference compatibility dispatch. Goal583 starts the
native Apple RT parity expansion by adding a second native Apple Metal/MPS RT
primitive:

- 3D `ray_triangle_hit_count`

This does not finish all native Apple RT workloads. It reduces the native gap
from 1 native predicate to 2 native 3D ray/triangle predicate modes.

## Implementation

Native file:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`

New C ABI:

- `rtdl_apple_rt_run_ray_hitcount_3d`

Execution strategy:

- Use Apple Metal/MPS `MPSRayIntersector`.
- For each triangle, build a one-triangle `MPSTriangleAccelerationStructure`.
- Run `MPSIntersectionTypeAny` for all rays against that triangle.
- Increment each ray's hit count when MPS reports a hit.
- Emit one `{ray_id, hit_count}` row per ray, including zero-hit rays.

This is correctness-oriented native MPS RT coverage. It is not the final
throughput design because it rebuilds one-triangle acceleration structures in a
loop. The reason for this design is correctness: MPS exposes nearest/any
queries, not a direct all-hit count output, so per-triangle any-hit avoids
same-distance undercounting from repeated nearest traversal.

Python runtime file:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`

New Python API:

- `ray_triangle_hit_count_apple_rt(rays, triangles)`

`run_apple_rt` now routes:

- 3D `ray_triangle_closest_hit` to native MPS RT
- 3D `ray_triangle_hit_count` to native MPS RT
- other supported predicates to CPU reference compatibility unless
  `native_only=True`, in which case they are rejected

## Test Evidence

Build:

```bash
cd /Users/rl2025/rtdl_python_only
make build-apple-rt
```

Result: pass.

Full local test suite:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 239 tests in 61.593s
OK
```

External review evidence:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal583_gemini_flash_review_2026-04-18.md`: ACCEPT
- `/Users/rl2025/rtdl_python_only/docs/reports/goal583_claude_review_2026-04-18.md`: ACCEPT

Claude noted one non-blocking stale error message in `run_apple_rt` that still
said only 3D closest-hit was native. That message was corrected after review to
name both native modes: 3D closest-hit and 3D hit-count.

Focused Apple RT tests:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Result:

```text
Ran 8 tests in 0.086s
OK
```

The new test is:

- `test_ray_triangle_hit_count_native_matches_cpu_reference`

It verifies:

- `run_apple_rt(ray_triangle_hit_count_3d_kernel, native_only=True, ...)`
  matches `run_cpu_python_reference`
- `ray_triangle_hit_count_apple_rt(...)` direct helper matches
  `run_cpu_python_reference`

Compile check:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m compileall -q src/rtdsl tests/goal578_apple_rt_backend_test.py tests/goal582_apple_rt_full_surface_dispatch_test.py
```

Result: pass.

## Current Native Apple RT Coverage

Native MPS RT today:

- 3D `ray_triangle_closest_hit`
- 3D `ray_triangle_hit_count`

Compatibility dispatch today:

- 2D `ray_triangle_hit_count`
- 2D geometry predicates
- nearest-neighbor predicates
- graph predicates
- bounded DB predicates
- pathology/overlap/Jaccard predicates

## Honesty Boundary

Correct public statement after Goal583:

> `run_apple_rt` can run every current RTDL predicate on Apple Silicon macOS.
> Native Apple MPS RT execution currently covers 3D closest-hit and 3D
> hit-count. Other predicates are still CPU-reference compatibility dispatch
> until native Apple encodings are implemented and tested.

Incorrect public statement after Goal583:

- All RTDL workloads are native Apple RT hardware accelerated.
- Apple RT has performance parity with OptiX/Vulkan/HIPRT/Embree.
- The broader 2D, nearest-neighbor, graph, and DB workloads are native Apple RT.

## Current Verdict

Codex local verdict: ACCEPT as the next native Apple RT expansion step, not as
completion of full native Apple RT parity.

External AI consensus: ACCEPT from Gemini Flash and Claude.
