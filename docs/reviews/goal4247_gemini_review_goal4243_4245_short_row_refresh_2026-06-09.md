# Gemini Review: Goals 4243-4245 Short-Row Refresh

Date: 2026-06-09
Verdict: `accept`
Evidence Status: **Internal-Only**

## Summary

This review covers the refresh of current-head short rows (Goal 4243), the resulting update to the major performance target map (Goal 4244), and the hardening of RayJoin evidence and target-map structures (Goal 4245). The evidence provided is robust, maintains strict claim boundaries, and correctly implements the hardening requests from previous reviews.

## Assessment of Questions

### 1. Legitimacy of Short-Row Refresh (Goal 4243)
Goal 4243 successfully refreshes `hausdorff_xhd`, `contact_manifold`, and `triangle_counting` with dedicated long-repeat evidence at source commit `9a40f7f5`. Aggregate times for all three are now well above the 1.0s floor (Hausdorff: 13.0s, Contact Manifold: 10.3s, Triangle Counting: 2.1s), reducing reliance on older stress-test artifacts.

### 2. Scoping and Claim Boundaries
The three refreshed rows preserve their scoped meanings. The reports explicitly state that these benchmarks do not represent universal exact Hausdorff speedups, full physics solvers, or complete paper-system reproductions. These boundaries are verified in both documentation and automated tests (`tests/goal4243_short_row_long_repeat_refresh_test.py`).

### 3. Target Map Integrity (Goal 4244)
The target map in `src/rtdsl/current_major_performance_targets.py` was updated to reflect the new evidence. It remains a planning tool and does not authorize release or public claims. The implementation uses a frozen dataclass with a `__post_init__` hook that strictly forbids setting any authorization flag to `True`.

### 4. RayJoin and Structural Hardening (Goal 4245)
Goal 4245 correctly addresses the findings from Goal 4241:
- `tests/goal4239_rayjoin_dedicated_long_repeat_profile_test.py` now enforces `wrapper_elapsed_sec > 20.0`.
- `CurrentMajorPerformanceTarget` now structurally includes the `rtdl_beats_rayjoin_claim_authorized` guard, ensuring that any attempt to enable this claim would trigger a validation failure.

### 5. Remaining Items
The current "major performance target map" (Goal 4244) indicates that while NVIDIA-based evidence is nearing internal completeness, several gates remain before a formal release:
- **AMD/HIPRT Parity:** Requires actual AMD hardware for functional and timing validation.
- **Formal Release Packet:** Needs exact wording for public claims, a comprehensive documentation audit, and multi-AI consensus.
- **User Decision:** The "Major release candidate packet" remains at `pending_user_release_decision`.

## Conclusion

The evidence and hardening chain for Goals 4243-4245 are technically sound and maintain the project's high standards for evidence-based claims. The transition from "safe_but_short" rows to dedicated long-repeat evidence at the current head is a significant improvement in release readiness.

**The evidence remains internal-only.**
