# RTDL v0.9.1 Support Matrix

Date: 2026-04-18

Status: released as `v0.9.1`

## Scope

`v0.9.1` adds the first Apple RT backend slice to the existing v0.9 line.

New support:

- `run_apple_rt`
- 3D `ray_triangle_closest_hit`
- macOS Apple Silicon
- Apple Metal/MPS `MPSRayIntersector`

Kept from `v0.9.0`:

- HIPRT `run_hiprt` parity coverage for the accepted 18-workload Linux matrix
- prepared HIPRT reuse for the documented bounded paths
- CPU reference, `run_cpu`, and Embree support for 3D `ray_triangle_closest_hit`

## Backend Matrix For Closest-Hit

| Primitive / workload | CPU Python reference | `run_cpu` | Embree | Apple RT | OptiX | Vulkan | HIPRT |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ray_triangle_closest_hit` 3D | supported | supported | supported | supported | future work | future work | future work |

## Apple RT Evidence

Implementation report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal578_v0_9_1_apple_rt_backend_bringup_2026-04-18.md`

Public-doc/example integration:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal579_v0_9_1_apple_rt_public_doc_example_integration_2026-04-18.md`

Pre-release gate:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal580_v0_9_1_apple_rt_pre_release_gate_2026-04-18.md`

Review consensus:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal578_gemini_flash_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal578_claude_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal579_gemini_flash_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal579_claude_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal580_gemini_flash_review_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal580_claude_review_2026-04-18.md`

## Local Apple M4 Test Evidence

Build:

```bash
make build-apple-rt
```

Focused test:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test -v
```

Result:

```text
Ran 4 tests
OK
```

Full suite:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests
```

Result:

```text
Ran 239 tests
OK
```

## Explicit Non-Claims

- no full Apple backend parity
- no Apple RT support beyond 3D `ray_triangle_closest_hit`
- no prepared Apple RT reuse
- no Intel Mac support claim
- no iOS support claim
- no measured Apple hardware speedup claim
- no OptiX, Vulkan, or HIPRT closest-hit support yet
