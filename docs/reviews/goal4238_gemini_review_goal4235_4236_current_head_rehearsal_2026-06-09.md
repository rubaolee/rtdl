# Independent Gemini Review: Goal4235-4236 Current-Head Rehearsal

Date: 2026-06-09
Verdict: `accept-with-boundary`

## Executive Summary

This review accepts the Goal4235-4236 current-head rehearsal chain. The evidence
provided in Goal4235 confirms that the current source head (`72690687`) is
operationally healthy across all ten promoted benchmark front doors on the
RTX 4000 Ada platform. The target-map update in Goal4236 correctly reflects this
health state while maintaining a rigorous boundary against unauthorized public
performance claims.

**This review does not authorize release action or public performance claims.**
The current results are internal rehearsal data only.

## Question Response

### 1. Execution Proof (Goal4235)

**Does Goal4235 legitimately prove that the current source head `72690687` executes all ten promoted benchmark front doors on RTX 4000 Ada with a clean pod worktree and 10/10 JSON-pass results?**

**Yes.**
- The `current_scale_profile_packet.json` records `all_pass: true` and `json_pass_count: 10`.
- The `runtime_environment` block confirms the source commit `72690687`, a clean `working_tree_clean: true`, and the presence of the "NVIDIA RTX 4000 Ada Generation" GPU.
- Individual stdout payloads for all ten rows have been inspected and show successful `pass` status with expected semantic metadata.

### 2. Claim Boundary Preservation

**Does the packet preserve the difference between current-head route health, measurement adequacy, and formal release/performance claims?**

**Yes.**
- Every inspected artifact (packet, report, and individual stdout JSONs) carries explicit `claim_boundary` text distinguishing internal health from public claims.
- All authorization flags (e.g., `release_authorized`, `public_speedup_claim_authorized`, `broad_rt_core_claim_authorized`) are set to `false` in the data and enforced in the code.

### 3. Target Map Integrity (Goal4236)

**Does Goal4236 update the target map honestly by pointing current route health at Goal4235 while leaving release action, public speedup wording, paper reproduction wording, automatic partner selection, true-zero-copy wording, AMD/HIPRT evidence, and app-specific engine logic unauthorized?**

**Yes.**
- The implementation in `src/rtdsl/current_major_performance_targets.py` correctly maps `ten_app_current_route_health` to the Goal4235 reading.
- Other targets like `release_grade_long_run_packet` and `amd_hiprt_functional_parity` are correctly identified as needing broader evidence or being blocked by hardware.
- The `CurrentMajorPerformanceTarget` dataclass uses a `__post_init__` hook to hard-fail if any authorization flag is set to true, ensuring the boundary cannot be accidentally breached in the source.

### 4. Test Strength

**Are the tests strong enough to catch stale commit provenance, failed rows, claim-boundary leakage, and route-policy drift?**

**Yes.**
- `tests/goal4235_current_head_rehearsal_after_measurement_closure_test.py` performs deep recursive checks for forbidden `true` flags in the packet and all row payloads.
- The tests verify specific route-policy details (e.g., Numba requirements for specific rows, RayJoin route splits) that would fail if the runtime drifted.
- The tests explicitly check the git commit short hash and worktree cleanliness.

### 5. Next Steps

**What should be the next major target before any formal release packet?**

The next major target should be **Goal4239: Release-Grade Long-Run Packet**.
While Goal4235 proves health on short/representative scales, a formal release
requires:
1. Assembly of the exact public claim wording.
2. A comprehensive documentation/user-manual audit.
3. Fresh multi-AI consensus over the final release artifact.
4. AMD/HIPRT functional evidence (once hardware is available).

## Final Verdict

The Goal4235-4236 chain is accepted with the boundary that it remains an
internal health rehearsal. The technical execution is clean, the planning map
is honest, and the validation tests are robust.
