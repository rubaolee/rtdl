# RTDL v0.9.2 Support Matrix

Date: 2026-04-19

Status: release candidate after Goal601; tag pending explicit release action

## Scope

`v0.9.2` is scoped to Apple RT surface breadth and performance ergonomics on
Apple Silicon macOS.

It does not change the HIPRT, OptiX, Vulkan, Embree, graph, DB, or app-building
release contracts except where public docs need to link the current Apple RT
candidate evidence.

## Apple RT Dispatch Matrix

| Workload / predicate | `run_apple_rt` mode in v0.9.2 | Notes |
| --- | --- | --- |
| 3D `ray_triangle_closest_hit` | `native_mps_rt` | released in v0.9.1; v0.9.2 adds prepared reuse |
| 3D `ray_triangle_hit_count` | `native_mps_rt` | v0.9.2 native slice; correct but not performance-leading |
| 2D `segment_intersection` | `native_mps_rt` | v0.9.2 native slice; masked traversal plus exact refinement |
| remaining current predicates | `cpu_reference_compat` | callable through `run_apple_rt`; rejected when `native_only=True` |

The "remaining current predicates" are the rest of the 18 current RTDL
predicate surface documented in `rt.apple_rt_support_matrix()`. They are
callable for user convenience but are not Apple hardware-backed in this release
candidate.

## Native Apple RT Feature Matrix

| Primitive / workload | CPU Python reference | `run_cpu` | Embree | Apple RT | OptiX | Vulkan | HIPRT |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3D `ray_triangle_closest_hit` | supported | supported | supported | supported | future work | future work | future work |
| 3D `ray_triangle_hit_count` | supported | supported | supported | supported | supported where built | supported where built | supported on Linux HIPRT matrix |
| 2D `segment_intersection` | supported | supported | supported | supported | supported where built | supported where built | supported on Linux HIPRT matrix |

## Performance Evidence

Goal600 local Apple M4 artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal600_v0_9_2_pre_release_apple_rt_perf_macos_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal600_v0_9_2_pre_release_apple_rt_perf_macos_2026-04-19.json`

Goal601 full-surface characterization:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal601_v0_9_2_apple_rt_full_surface_perf_macos_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal601_v0_9_2_apple_rt_full_surface_perf_macos_2026-04-19.json`

Goal601 measures all currently callable `run_apple_rt` shapes against Embree.
It includes 19 measured rows because `ray_triangle_hit_count` has both 2D
compatibility and 3D native shapes. Rows marked `cpu_reference_compat` are API
compatibility timings, not Apple hardware-backed RT timings.

Measured medians:

| Workload | Input sizes | Embree median | Apple RT median | Apple/Embree | Parity | Stability |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `ray_triangle_closest_hit_3d` | 256 rays, 256 triangles | 0.002579126 s | 0.001410938 s | 0.547x | true | true |
| `ray_triangle_hit_count_3d` | 128 rays, 512 triangles | 0.002449166 s | 0.115251041 s | 47.057x | true | false |
| `segment_intersection_2d` | 128 left, 128 right | 0.007471208 s | 0.030149874 s | 4.035x | true | true |

Allowed public wording:

- Apple RT closest-hit is faster than Embree on the current local Apple M4
  fixture.
- v0.9.2 reduces Apple RT overhead for native slices and improves repeated-query
  ergonomics.
- Apple RT is correctness-credible for the native slices listed above.

Disallowed public wording:

- broad Apple RT speedup
- Apple RT is the mature backend
- Apple RT is faster than Embree generally
- all `run_apple_rt` predicates are Apple hardware-backed
- non-Apple-Silicon support

## Test Evidence

Goal600 local pre-release gate:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*test.py' -v
Ran 1118 tests in 108.847s
OK (skipped=171)
```

Apple RT focused suite:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal578_apple_rt_backend_test \
  tests.goal582_apple_rt_full_surface_dispatch_test \
  tests.goal595_apple_rt_perf_harness_test \
  tests.goal596_apple_rt_prepared_closest_hit_test \
  tests.goal597_apple_rt_masked_hitcount_test \
  tests.goal598_apple_rt_masked_segment_intersection_test -v
Ran 19 tests in 0.046s
OK
```

Public command audit:

```text
valid: true
public docs scanned: 14
public commands found: 244
```

Review consensus:

- Codex Goal600 report: ACCEPT
- Gemini-style external review: ACCEPT
- Claude review: ACCEPT
- Goal601 full-surface characterization review: ACCEPT
- Goal601 Gemini review: ACCEPT

## Platform Boundary

Validated Apple RT platform:

- macOS arm64 on Apple M4
- Apple Metal/MPS `MPSRayIntersector`
- local backend library built with `make build-apple-rt`

No claim is made for:

- Intel Mac Apple RT
- iOS
- non-Apple GPU support through this backend
- broad Apple speedup
- parity of native hardware execution for every `run_apple_rt` compatibility
  predicate
