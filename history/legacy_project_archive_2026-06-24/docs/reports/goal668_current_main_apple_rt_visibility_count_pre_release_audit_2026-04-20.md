# Goal668: Current-Main Apple RT Visibility-Count Pre-Release Audit

Date: 2026-04-20

Status: accepted hold-ready audit

## Scope

This audit covers the current-main Apple RT prepared/prepacked 2D
visibility-count slice after Goal667. It does not authorize a tag by itself; it
records test, docs, performance, and review evidence for the next release
decision.

## Implementation State

Implemented and rebuilt from source:

- Native Apple RT prepared 2D any-hit handle:
  `rtdl_apple_rt_prepare_ray_anyhit_2d`
- Native prepared row path:
  `rtdl_apple_rt_run_prepared_ray_anyhit_2d`
- Native profile path:
  `rtdl_apple_rt_profile_prepared_ray_anyhit_2d`
- Native scalar count path:
  `rtdl_apple_rt_count_prepared_ray_anyhit_2d`
- Python public API:
  `prepare_apple_rt_ray_triangle_any_hit_2d`,
  `prepare_apple_rt_rays_2d`, `PreparedAppleRtRayTriangleAnyHit2D`
- Public example:
  `examples/rtdl_apple_rt_visibility_count.py`

## Correctness

Correctness evidence:

- prepared Apple RT 2D any-hit rows match direct Apple RT 2D any-hit rows in
  focused tests
- packed ray-buffer path matches unpacked path
- scalar count path matches row-materialized blocked-ray count
- large Goal666 benchmark uses backend-agreement correctness across Apple RT,
  Embree, and Shapely/GEOS for dense, mixed, and sparse cases

Local test evidence:

```text
Focused Apple RT/backend tests: 23 tests OK
Full local discovery: 1243 tests OK, 180 skips
```

## Performance

Regenerated report:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal666_mac_visibility_count_perf_2026-04-20.md
```

Key repeated-query medians:

| Case | Apple RT packed count | Embree row count | Shapely/GEOS count |
| --- | ---: | ---: | ---: |
| dense blocked, 32768 rays / 8192 triangles | 0.001330064 s | 0.015297282 s | 0.297816304 s |
| mixed visibility, 32768 rays / 8192 triangles | 0.001182773 s | 0.015251223 s | 0.252873766 s |
| sparse clear, 32768 rays / 8192 triangles | 0.000910397 s | 0.014742673 s | 0.196451636 s |

Claim boundary:

- valid: Apple RT is faster in this harness for repeated scalar blocked-ray
  count when both scene and rays are reusable/prepacked
- invalid: Apple RT is broadly faster than Embree, faster for full emitted
  rows, or accelerated through Apple ray-tracing hardware for DB/graph
  workloads

## Documentation

Public docs refreshed:

- `README.md`
- `docs/README.md`
- `docs/quick_tutorial.md`
- `docs/release_facing_examples.md`
- `docs/current_main_support_matrix.md`
- `docs/backend_maturity.md`
- `examples/README.md`

Doc audit evidence:

```text
Public command truth audit: valid true, 250 commands, 14 docs
Public front-page/doc consistency tests: 11 tests OK
Current-main support-matrix/doc boundary tests: 14 tests OK
git diff --check: clean
```

## AI Consensus

Codex verdict:

ACCEPT. The implementation, regenerated performance report, and public docs
match the intended narrow claim.

Claude verdict:

PASS in:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal667_claude_apple_rt_visibility_count_release_review_2026-04-20.md
```

Claude's only non-blocking observation was that the scalar count path currently
uses nearest-hit existence over the prepared MPS prism acceleration structure
rather than a lower-level true any-hit kernel. That boundary is now documented
in the support matrix, backend maturity page, and Apple RT support notes.

## Audit Verdict

ACCEPT.

This slice is ready for the next release decision as a bounded current-main
Apple RT app-performance improvement. The correct release wording is:

RTDL now has a Mac Apple RT prepared/prepacked 2D visibility-count path that can
make repeated scalar blocked-ray count apps fast on Apple Silicon. It is not a
claim about full row-output performance, DB/graph ray-tracing hardware
acceleration, or broad Apple RT superiority over Embree.
