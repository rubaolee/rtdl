# Goal650 Review Verdict

Date: 2026-04-20
Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

## Findings

### Native early-exit any-hit — confirmed genuine

Both 2D and 3D any-hit GLSL shaders in `rtdl_vulkan_core.cpp` use
`rayPayloadEXT uint anyHit`, set `anyHit = 1u` on first accepted hit, and call
`terminateRayEXT` unconditionally after that. This is native Vulkan RT early
exit, not a projection from hit-count rows.

- 2D pipeline: `VK_RAY_TRACING_SHADER_GROUP_TYPE_PROCEDURAL_HIT_GROUP_KHR`
  with custom AABB intersection + dedicated any-hit stage (lines ~1676–1684,
  ~2461–2465 in core.cpp).
- 3D pipeline: `VK_RAY_TRACING_SHADER_GROUP_TYPE_TRIANGLES_HIT_GROUP_KHR`
  with hardware triangle geometry + dedicated any-hit stage (lines ~1766–1774,
  ~2574–2579 in core.cpp).

### ABI and Python wiring — correct

- `RtdlRayAnyHitRow { ray_id, any_hit }` is declared in `rtdl_vulkan_prelude.h`
  and matches the `_RtdlRayAnyHitRow` ctypes struct in `vulkan_runtime.py`.
- `rtdl_vulkan_run_ray_anyhit` and `rtdl_vulkan_run_ray_anyhit_3d` are
  exported in `rtdl_vulkan_api.cpp` and registered as optional symbols in
  `_register_argtypes`.
- `PreparedVulkanExecution.run()` checks for native symbol first, falls back
  to hit-count projection only for stale pre-Goal650 libraries — fallback is
  honest and documented.
- `run_raw()` requires native symbol and raises a clear error for stale
  libraries — no silent misbehavior.

### Apple RT boundary — correctly preserved

Apple RT is not touched by this goal. It remains documented as compatibility
(hit-count projection to `any_hit`). The report's stated rationale — different
Metal/MPS API constraints requiring separate 2D and 3D validation — is
sound. No overclaim.

### Test evidence

- Linux build + any-hit backend test suite: 8/8 pass (2D and 3D × dict and raw
  modes against CPU reference).
- Bounded timing probe: 0.0059 s vs 0.0069 s median whole-call time for 384×384
  dense-hit case. Consistent with early exit reducing traversal; appropriately
  described as bounded evidence, not a broad performance claim.
- macOS Python compile and 18-test combined suite: all OK.

### No issues found

The implementation is narrowly scoped to the stated goal. No regressions in
existing symbols, no overclaims, no stale fallback paths silently masquerading
as native.
