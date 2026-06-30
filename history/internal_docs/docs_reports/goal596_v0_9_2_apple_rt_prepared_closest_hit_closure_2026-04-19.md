# Goal596: v0.9.2 Apple RT Prepared Closest-Hit Closure

Date: 2026-04-19

Status: ACCEPT

## Scope

Goal596 adds a prepared Apple Metal/MPS RT path for 3D
`ray_triangle_closest_hit`. The prepared path builds the triangle acceleration
structure once and reuses the Metal device, command queue, MPS intersector,
vertex buffer, and acceleration structure across repeated ray batches.

## Code Artifacts

```text
/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm
/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py
/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py
/Users/rl2025/rtdl_python_only/tests/goal578_apple_rt_backend_test.py
/Users/rl2025/rtdl_python_only/tests/goal596_apple_rt_prepared_closest_hit_test.py
/Users/rl2025/rtdl_python_only/scripts/goal596_apple_rt_prepared_closest_hit_perf.py
```

## Public Python API

```python
with rt.prepare_apple_rt_ray_triangle_closest_hit(triangles) as prepared:
    rows = tuple(prepared.run(rays))
```

The handle rejects use after `close()` and frees the native prepared object
through the Apple RT dylib.

## Native ABI

New native entry points:

```text
rtdl_apple_rt_prepare_ray_closest_hit_3d
rtdl_apple_rt_run_prepared_ray_closest_hit_3d
rtdl_apple_rt_destroy_prepared_ray_closest_hit_3d
```

The Apple RT dylib version is now `(0, 9, 2)`.

## Performance Artifact

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal596_apple_rt_prepared_closest_hit_perf_macos_2026-04-19.json
/Users/rl2025/rtdl_python_only/docs/reports/goal596_apple_rt_prepared_closest_hit_perf_macos_2026-04-19.md
```

Final local run summary:

| Backend path | Median | CV | Stable | Matches CPU |
| --- | ---: | ---: | --- | --- |
| `apple_rt_one_shot` | 0.002771604 s | 0.651 | false | true |
| `apple_rt_prepared` | 0.000441375 s | 0.646 | false | true |
| `embree` | 0.002656104 s | 0.111 | true | true |

Prepared / one-shot Apple RT median ratio: 0.159x.

Prepared / Embree median ratio: 0.166x.

Important boundary: Apple RT timings remain unstable above the Goal595
coefficient-of-variation threshold, so the ratios are engineering-triage
evidence and not public speedup wording.

## Verification

Build:

```text
make build-apple-rt
```

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal596_apple_rt_prepared_closest_hit_test tests.goal578_apple_rt_backend_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Result:

```text
Ran 12 tests in 0.030s
OK
```

Performance artifact:

```text
PYTHONPATH=src:. python3 scripts/goal596_apple_rt_prepared_closest_hit_perf.py --warmups 5 --repeats 20 --cv-threshold 0.15
```

Result: JSON and Markdown artifacts written successfully.

## Consensus

Codex verdict: ACCEPT. The prepared API is functionally correct and
substantially reduces repeated-call median latency in the local fixture, while
the report preserves the required honesty boundary around unstable Apple RT
timing.

External review:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal596_external_review_2026-04-19.md
```

External verdict: ACCEPT. The reviewer found no correctness issues, accepted
the public surface and bounded performance wording, and noted only non-blocking
defensive observations.
