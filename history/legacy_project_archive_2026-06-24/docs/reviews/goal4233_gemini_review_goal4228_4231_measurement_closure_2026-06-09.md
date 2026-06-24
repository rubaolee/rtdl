# Independent Gemini Review: Goals4228-4231 Measurement Closure

Date: 2026-06-09
Verdict: `accept-with-boundary`

## Overview

This independent review covers the measurement-closure chain (Goals 4228-4231). The work focuses on closing the internal measurement-adequacy gap for the ten promoted benchmark apps by ensuring all rows clear the one-second hot-path floor and by hardening the timing contracts for key workloads.

## Questions & Answers

### 1. Does Goal4228 legitimately close the RT-DBSCAN hot-path measurement-floor gap without changing the route policy or overclaiming?

**Yes.** Goal 4228 reruns the promoted `optix_rt_core_grouped_stream_numba_column_signature_3d` route with 20 repeats (and 2 warmups), resulting in a total measured query time of ~1.74s. This clears the 1.0s floor required for release-prep evidence. The route policy remains the unblocked single-pass grouped stream, consistent with the profile-aware boundary policy established in Goal 4222. The artifacts and reports maintain strict internal-only framing.

### 2. Does Goal4229 correctly harden Barnes-Hut force-summary timing by exposing real aggregate timing fields rather than relying on median-times-repeat proxy evidence?

**Yes.** The update to `rtdl_barnes_hut_force_app.py` introduces a `prepared_force_repeat_protocol` that records `force_kernel_runs_sec` and `force_kernel_total_sec`. This eliminates the reliance on median-based proxies for long-repeat evidence. The pod artifact for Goal 4229 demonstrates this hardening by recording 200 iterations with a total kernel time of ~1.73s, clearing the measurement floor with high-fidelity evidence.

### 3. Does Goal4230 accurately show that all ten promoted benchmark apps now have at least one second-level measurement source above the one-second hot-path or representative-profile floor?

**Yes.** The adequacy table in Goal 4230 reconciles evidence from Goals 4185, 4186, 4189, 4225, 4228, and 4229. Every app now has a recorded aggregate or representative wall time exceeding 1.0s. This reconcile confirms that the project no longer has "short health row" gaps in its primary NVIDIA/OptiX benchmark surface.

### 4. Does Goal4231 update the major performance target map honestly: measurement adequacy is internally closed, while release action, public claims, docs audit, consensus, and AMD/HIPRT hardware evidence remain unapproved or pending?

**Yes.** The update to `src/rtdsl/current_major_performance_targets.py` accurately reflects the status of the project. `ten_app_measurement_adequacy_closure` is correctly set to `done_internal_evidence`. Crucially, the map maintains `needs_broader_evidence`, `blocked_pending_hardware`, and `pending_user_release_decision` for the subsequent gates. All "authorized" flags (e.g., `release_authorized`, `public_speedup_claim_authorized`) are programmatically enforced to remain `False`.

### 5. Are the tests strong enough to catch measurement-floor regressions and claim-boundary leakage?

**Yes.** The test suite (`tests/goal4228_*`, `tests/goal4229_*`, `tests/goal4230_*`, and `tests/goal4219_*`) is robust.
- `Goal4230TenAppMeasurementAdequacyClosureTest` asserts that every app's aggregate timing exceeds 1.0s.
- `Goal4219MajorPerformanceTargetMapTest` validates the entire target map, ensuring required statuses are present and all authorization flags are `False`.
- Individual artifact tests check for schema version, commit hash, and worktree cleanliness.

### 6. What should be the next major engineering target before any user-requested formal release packet?

According to the target map in Goal 4231 and the analysis in Goal 4230, the next critical engineering targets are:
1.  **AMD/HIPRT Functional Parity**: Establishing baseline functional parity on actual AMD hardware is the most significant hardware-level gap remaining.
2.  **Final Docs Audit & Wording Pass**: Cleaning the public-facing documentation and finalizing the exact claim wording for the intended release.
3.  **Multi-AI Release Consensus**: Obtaining fresh, formal consensus over the final release claims once the docs and hardware evidence are ready.

## Boundary Compliance

This review **does not** authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper-reproduction wording, true-zero-copy wording, automatic partner selection, AMD performance wording, or app-specific native-engine logic. This evidence is accepted as **internal measurement-adequacy readiness** only.
