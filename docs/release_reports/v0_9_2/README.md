# RTDL v0.9.2 Release Package

This package records the `v0.9.2` Apple RT performance candidate line.

`v0.9.2` is the Apple developer usability/performance step after the narrow
`v0.9.1` Apple RT closest-hit release. It keeps the `v0.9.1` release boundary
intact until tagging, while documenting the candidate work that makes Apple RT
more useful on Apple Silicon macOS:

- all 18 current RTDL predicates are callable through `run_apple_rt`
- native Apple Metal/MPS RT slices now cover:
  - 3D `ray_triangle_closest_hit`
  - 3D `ray_triangle_hit_count`
  - 2D `segment_intersection`
- `run_apple_rt(..., native_only=True)` rejects compatibility paths instead of
  silently treating CPU-reference compatibility as Apple RT hardware execution
- prepared Apple RT closest-hit reuse is available for repeated queries
- masked chunked traversal reduces Apple RT setup/traversal overhead for
  hit-count and segment-intersection

This package does **not** claim broad Apple RT speedup. Goal600 evidence shows
closest-hit faster than Embree on the local Apple M4 fixture, but hit-count is
unstable and slower, and segment-intersection is stable but slower. Embree
remains the mature RTDL performance baseline.

Start here:

- [Support Matrix](support_matrix.md)
- [Release Statement](release_statement.md)
- [Audit Report](audit_report.md)
- [Tag Preparation](tag_preparation.md)
- [Goal 594 Plan](../../reports/goal594_v0_9_2_apple_rt_performance_plan_2026-04-19.md)
- [Goal 595 Performance Harness](../../reports/goal595_apple_rt_perf_harness_2026-04-19.md)
- [Goal 596 Prepared Closest-Hit](../../reports/goal596_v0_9_2_apple_rt_prepared_closest_hit_2026-04-19.md)
- [Goal 597 Masked Hit-Count](../../reports/goal597_v0_9_2_apple_rt_masked_hitcount_implementation_2026-04-19.md)
- [Goal 598 Masked Segment-Intersection](../../reports/goal598_v0_9_2_apple_rt_masked_segment_intersection_closure_2026-04-19.md)
- [Goal 599 Public Doc Refresh](../../reports/goal599_v0_9_2_apple_rt_public_doc_refresh_2026-04-19.md)
- [Goal 600 Pre-Release Gate](../../reports/goal600_v0_9_2_apple_rt_pre_release_gate_2026-04-19.md)
- [Goal 600 Apple RT Performance Artifact](../../reports/goal600_v0_9_2_pre_release_apple_rt_perf_macos_2026-04-19.md)
- [Goal 600 External Review](../../reports/goal600_external_pre_release_review_2026-04-19.md)
- [Goal 600 Claude Review](../../reports/goal600_claude_pre_release_review_2026-04-19.md)
- [Goal 601 Full-Surface Apple RT vs Embree Characterization](../../reports/goal601_v0_9_2_apple_rt_full_surface_perf_macos_2026-04-19.md)
