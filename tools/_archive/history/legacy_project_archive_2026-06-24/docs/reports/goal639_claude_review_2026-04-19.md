# Goal 639 Review: HIPRT Native Early-Exit Any-Hit

Date: 2026-04-19
Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

## Evidence

**Early-exit loop break — confirmed.**
`ray_anyhit_kernel_source_3d()` and `ray_anyhit_kernel_source_2d()` in
`rtdl_hiprt_core.cpp:775,784` replace the hit-count increment with:

```cpp
any_hit = 1u;
break;
```

This is a genuine kernel-loop early exit, not a post-hoc projection.

**Native ABI symbols — confirmed.**
`rtdl_hiprt_run_ray_anyhit_2d` (api.cpp:453) and
`rtdl_hiprt_run_ray_anyhit_3d` (api.cpp:186) are both exported as `extern "C"`
functions using the HIPRT geometry/traversal/Orochi launch path.

**Python dispatch — confirmed.**
`hiprt_runtime.py` defines `_RtdlRayAnyHitRow`, `ray_triangle_any_hit_2d_hiprt`,
`ray_triangle_any_hit_3d_hiprt`, and the unified `ray_triangle_any_hit_hiprt`
dispatcher (lines 904–1026). The stale-library fallback via hit-count projection
remains when native symbols are absent.

**Performance claims — appropriately bounded.**
The report and `docs/features/ray_tri_anyhit/README.md` explicitly state:
- No whole-call speedup is claimed; timing is dominated by setup/JIT overhead.
- HIPRT validation ran on NVIDIA/Orochi (GTX 1070), not AMD hardware.
- Vulkan and Apple RT remain compatibility paths.

No overclaiming detected.

## Notes

- The kernel source substitution approach (text replace on the hitcount kernel)
  is unconventional but correct; the `break` lands inside the traversal loop
  body, which is the right location for early exit.
- Linux test run passed 6 of 10 tests (4 skipped for unrelated backends),
  validating 2D and 3D correctness against the CPU oracle.
