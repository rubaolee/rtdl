# Goal579: v0.9.1 Apple RT Public Doc/Example Integration Review

**Verdict: ACCEPT**

**Reviewer: Gemini Flash**
**Date: 2026-04-18**

## Review Summary

Goal579 successfully integrates the Apple RT backend slice (Goal578) into the public-facing documentation and example surface. The integration preserves the "active candidate" status of `v0.9.1` and maintains strict honesty boundaries regarding the current narrow scope of Apple Silicon support.

## Public Integration Highlights

- **Example Surface:** Added `examples/rtdl_apple_rt_closest_hit.py`, which provides a clean, JSON-reporting reference for the new candidate backend. It correctly handles backend unavailability and focuses on the supported `ray_triangle_closest_hit` primitive.
- **Support Matrix:** The `v0.9` support matrix clearly separates the released `v0.9.0` HIPRT/closest-hit surface from the `v0.9.1` Apple RT candidate line.
- **Front Page:** `README.md` and `docs/README.md` are updated to include the Apple RT candidate in the version status, backend roles, and tutorial paths.
- **Boundaries:** `docs/capability_boundaries.md` and `docs/current_architecture.md` are updated with specific non-claims (no full parity, no speedup claim, closest-hit only) to prevent overclaiming.

## Honesty Boundary & Non-Claims

The following boundaries were successfully preserved in the public documentation:
- `v0.9.0` remains the latest released tag.
- `v0.9.1` Apple RT is an active candidate on `main` only.
- Apple RT currently means `MPSRayIntersector` on Apple Silicon macOS.
- Support is currently restricted to **3D `ray_triangle_closest_hit`**.
- No full backend parity claim is made.
- No Apple hardware speedup or RT-core performance claim is made.

## Blockers
- None.

## Notes
- The integration is surgically applied to all relevant high-level docs and tutorials.
- The messaging is consistent across the repository, ensuring users are not misled about the current state of Apple RT support.
