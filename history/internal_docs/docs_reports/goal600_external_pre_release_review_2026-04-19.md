# Goal600: External Pre-Release Review

Date: 2026-04-19

## Review of Apple RT v0.9.2 Candidate

**Verdict:** ACCEPT

**Reasoning:**
I have reviewed the pre-release gate document (`docs/reports/goal600_v0_9_2_apple_rt_pre_release_gate_2026-04-19.md`), the performance artifacts, the updated public documentation, and the stale-test cleanup claims.

- **Performance Claims:** The performance measurements are accurately reflected in the reports. The documentation correctly identifies that while `ray_triangle_closest_hit` is faster than Embree on Apple RT, `ray_triangle_hit_count` and `segment_intersection` are still slower. It also correctly highlights the instability in the hit-count workload.
- **Honesty Boundary:** The documentation (`docs/backend_maturity.md` and others) properly maintains the boundary that Embree remains the mature, optimized baseline, and does not overstate Apple RT as a broad speedup release.
- **Test Alignment:** The stale tests have been updated to align with the current `v0.9.1` released state and the `v0.9.2` candidate state, removing obsolete assumptions without modifying runtime product behavior.

The candidate is locally release-ready and meets the criteria for the v0.9.2 release.
