# Goal590 Apple RT Native Segment Intersection

Date: 2026-04-19

Status: ACCEPTED with Claude + Gemini review consensus

## Goal

Finish the current Apple Metal/MPS backend expansion by adding a native Apple RT path for 2D `segment_intersection`.

This is a bounded post-`v0.9.1` Apple RT slice. It does not claim full Apple backend parity, broad Apple hardware speedup, prepared Apple RT reuse, non-macOS support, or iOS support.

## Implementation

Files changed:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal582_apple_rt_full_surface_dispatch_test.py`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`

Native mode exposed by `apple_rt_predicate_mode("segment_intersection")`:

```text
native_mps_rt
```

The native lowering maps each left 2D segment to an MPS ray with bounded distance. Each right 2D segment is extruded into a thin 3D quadrilateral and traced through `MPSRayIntersector`. MPS is used for candidate discovery; the final intersection point and endpoint-inclusive RTDL semantics are enforced by the existing analytic 2D segment-intersection formula.

Important correctness details:

- output order is left-major to match `lsi_cpu`
- intersections at segment endpoints are preserved by using a small traversal `maxDistance` slack and then applying analytic bounds
- invalid or zero-length segments do not emit rows
- the direct helper `segment_intersection_apple_rt` is exported from `rtdsl.__all__`
- `run_apple_rt(..., native_only=True)` now accepts native 2D `segment_intersection`

## Test Evidence

Build and focused Apple RT tests:

```bash
make build-apple-rt && PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Result:

```text
Ran 9 tests
OK
```

The Goal582 segment-intersection test now includes multiple left/right intersections and an endpoint hit, so it checks row order and endpoint-inclusive parity against the CPU reference.

## Local Performance Smoke

Artifact:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal590_apple_rt_native_segment_intersection_perf_macos_2026-04-19.json
```

Summary:

- workload: `segment_intersection`
- left segments: 128
- right segments: 128
- candidate pairs: 16,384
- output rows: 16,384
- parity: true
- CPU Python reference median: 0.010794209083542228 s
- Apple RT native median: 0.0844811659771949 s

Interpretation: this is a correctness-oriented native Apple MPS path, not a speedup claim. The current implementation rebuilds a tiny MPS quadrilateral acceleration structure per right segment, so dispatch/build overhead dominates this small smoke workload.

## Current Apple RT Native Surface

After Goal590, the Apple RT backend has three native bounded slices:

- 3D `ray_triangle_closest_hit`
- 3D `ray_triangle_hit_count`
- 2D `segment_intersection`

All other current `run_apple_rt` predicates remain callable only through `cpu_reference_compat`.

## Review Consensus

External review artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal590_claude_review_2026-04-19.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal590_gemini_flash_review_2026-04-19.md`

Both reviews returned `ACCEPT`. Claude noted a minor variable-naming issue in `run_apple_rt`; that was fixed after review by renaming the normalized records from `rays`/`triangles` to `left_records`/`right_records`.
