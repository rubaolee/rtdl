# Antigravity Review — Goal4820 Core Directed-Segment Point-Location and Overlay Midpoint Fix

Date: 2026-06-30

Verdict: `approve_goal4820_core_fix_and_author_public_sample_correctness_gate_passed`

## Review Summary

Antigravity reviewed:

- `history/internal_docs/call_for_review_goal4820_core_directed_segment_point_location_and_overlay_midpoint_fix_2026-06-30.md`

and approved Goal4820.

## Answers Recorded

1. The OptiX SoS reported-distance fix is a valid RTDL
   directed-segment point-location contract repair. Encoding the equal-depth
   SoS slope preference into the reported hit distance prevents OptiX traversal
   pruning from bypassing deterministic tie-breaking. It is not a RayJoin-only
   shortcut.

2. The per-map midpoint face fix is a valid product/data-model repair for
   directed overlay continuation. The old single `mid_point_polygon_id` field
   allowed map 1 assignment to overwrite map 0 assignment on the same
   intersection object. The two-slot model is a fundamental correctness repair,
   not a hidden RayJoin kernel.

3. The author public sample correctness gate now passes byte-for-byte:
   identical byte length `16631243` and identical SHA256
   `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`.

4. Retaining the SoS core patch is acceptable and recommended even though this
   specific public-sample byte-equality failure was repaired by the midpoint
   face overwrite fix. The author-provided determinism note exposes a genuine
   core nondeterminism risk for other inputs.

5. The implementation avoided Embree and avoided public docs/tutorial/release
   surface changes.

6. The focused tests are sufficient before moving to controlled performance:
   - `test_overlay_midpoint_faces_are_stored_per_map`
   - `test_overlay_output_chain_writer_is_not_legacy_seed`
   - `Goal4373RayjoinCdbPointLocationRouteTest`

7. Goal4820 should close and authorize the next goal: controlled performance
   comparison against the author binary on the same public sample, with no broad
   performance claim.

## Non-Authorization

This review does not authorize:

- full RayJoin Section 5.7 eight-pair claims;
- broad RTDL performance claims;
- Embree work;
- V3/V4 release resurrection;
- app-specific hidden native kernels.
