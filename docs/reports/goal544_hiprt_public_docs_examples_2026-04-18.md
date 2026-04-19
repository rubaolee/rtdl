# Goal 544: HIPRT Public Docs And Example Preview

Date: 2026-04-18

## Verdict

ACCEPT for bounded post-`v0.8.0` development use with 2+ AI consensus.

Goal 544 makes the new HIPRT surface visible to users without overclaiming it
as a released general backend. The public docs now describe HIPRT as an
experimental Linux HIPRT-SDK preview for exactly one RTDL shape:
Ray3D probes, Triangle3D build geometry, and `ray_triangle_hit_count`.

## Files Changed

- `/Users/rl2025/rtdl_python_only/examples/rtdl_hiprt_ray_triangle_hitcount.py`
- `/Users/rl2025/rtdl_python_only/tests/goal544_hiprt_docs_examples_test.py`
- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`

## Example Behavior

`examples/rtdl_hiprt_ray_triangle_hitcount.py` is designed to be safe for public
users:

- it always computes CPU Python reference rows first;
- it attempts HIPRT only after that;
- if HIPRT is unavailable, it prints JSON with `hiprt_available: false` and
  exits successfully;
- if HIPRT is available, it validates both one-shot `run_hiprt` and prepared
  `prepare_hiprt` parity against the CPU Python reference.

The example demonstrates the exact user-facing kernel form:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def hiprt_ray_triangle_hitcount_kernel():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])
```

## Local macOS Validation

Command:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 examples/rtdl_hiprt_ray_triangle_hitcount.py
```

Result:

- CPU Python reference emitted:
  - first batch: `[{ray_id: 1, hit_count: 2}, {ray_id: 2, hit_count: 0}, {ray_id: 3, hit_count: 0}]`
  - second batch: `[{ray_id: 4, hit_count: 2}, {ray_id: 5, hit_count: 0}]`
- HIPRT reported unavailable because no local macOS `librtdl_hiprt.dylib` is
  present.
- Exit status was zero.

Command:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal543_hiprt_dispatch_test tests.goal544_hiprt_docs_examples_test
```

Result:

- `Ran 5 tests`
- `OK (skipped=2)`

## Linux HIPRT Validation

Fresh sync target:

- `/tmp/rtdl_goal544_hiprt_docs_examples`

Command:

```bash
cd /tmp/rtdl_goal544_hiprt_docs_examples
HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
make build-hiprt HIPRT_PREFIX=$HIPRT_PREFIX
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=$HIPRT_PREFIX/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 examples/rtdl_hiprt_ray_triangle_hitcount.py
PYTHONPATH=src:. python3 -m unittest tests.goal540_hiprt_probe_test tests.goal541_hiprt_ray_hitcount_test tests.goal543_hiprt_dispatch_test tests.goal544_hiprt_docs_examples_test
```

Result:

- `make build-hiprt` built `build/librtdl_hiprt.so`.
- HIPRT probe:
  - version: `(2, 2, 15109972)`
  - API version: `2002`
  - device type: `1`
  - device name: `NVIDIA GeForce GTX 1070`
- Example parity:
  - `run_hiprt_first_batch: true`
  - `prepare_hiprt_first_batch: true`
  - `prepare_hiprt_second_batch: true`
- Targeted HIPRT test bundle:
  - `Ran 10 tests`
  - `OK`

## Public Documentation Boundary

The public docs now explicitly say:

- HIPRT is experimental and post-`v0.8.0`;
- HIPRT is not part of the released `v0.8.0` support matrix;
- current support is only Ray3D/Triangle3D `ray_triangle_hit_count`;
- there is no AMD GPU validation yet;
- there is no HIPRT CPU fallback;
- 2D RTDL ray/triangle semantics, DB workloads, graph workloads, and
  nearest-neighbor workloads are not HIPRT-supported yet.

## Consensus Review

External AI review files:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal544_external_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal544_gemini_flash_review_2026-04-18.md`

Consensus:

- Codex: ACCEPT
- Claude: ACCEPT
- Gemini Flash: ACCEPT

## Codex Review

Codex accepts this goal as a bounded documentation/example closure because:

- user-facing docs now expose the feature instead of hiding it in tests;
- the example is runnable on machines without HIPRT and validates parity on
  Linux when HIPRT is available;
- the wording keeps release, platform, backend, and workload boundaries clear;
- no performance claim was added.
