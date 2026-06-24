# Gemini Review: Goals 4239-4240 RayJoin Long-Repeat Evidence Chain

Date: 2026-06-09
Reviewer: Gemini CLI
Verdict: `accept`
Evidence Status: **Internal-only**

## Overview

This review covers the RayJoin dedicated long-repeat evidence (Goal 4239) and the subsequent update to the major performance target map (Goal 4240). The evidence chain successfully addresses the measurement adequacy gap identified in previous reviews by providing a high-confidence, clean-source profile exceeding the 10-second threshold.

## Assessment against Review Questions

### 1. RayJoin Dedicated Long-Repeat Evidence (Goal 4239)
**Does it legitimately close the gap?**
Yes. Goal 4239 provides a **20.76s** representative mixed-route run on an NVIDIA RTX 4000 Ada. The run uses clean source commit `048d940c` (confirmed by `git_status_short == ""` and test verification). This significantly improves upon the earlier Goal 4230 representative row by providing a dedicated, repeatable profile suitable for internal performance tracking and future rehearsal.

### 2. Contract Split Preservation
**Does the report preserve the Numba/RTDL/OptiX split?**
Yes. The report and raw data (`rayjoin_long_repeat.stdout.json`) explicitly maintain the split:
- **PIP one-shot:** Numba CUDA JIT remains the recommended route (RTDL/OptiX is ~4x slower for this bounded slice).
- **Repeated PIP:** RTDL/OptiX prepared batch executor shows a 1.234x throughput improvement.
- **LSI Scalar Count:** RTDL/OptiX prepared primitive is ~262x faster than Numba.
- **Overlay Active Count:** RTDL/OptiX prepared primitive is ~213x faster than Numba.

The "automatic dispatch remains disabled" claim is verified by the JSON metadata and associated tests.

### 3. Major Performance Target Map (Goal 4240)
**Is the update honest and bounded?**
Yes. `src/rtdsl/current_major_performance_targets.py` has been updated to cite Goal 4239 under the `rayjoin_contract_split_route_policy` and `release_grade_long_run_packet` targets. 
- **Honesty:** The status for RayJoin route policy is correctly moved to `done_internal_evidence`.
- **Boundaries:** All authorization flags (release, public speedup, paper reproduction, etc.) remain strictly `False`. The Python class implementation itself enforces these boundaries with `ValueError` guards, and the tests explicitly check for "forbidden true paths" in the exported metadata.

### 4. Test Sufficiency
**Are the tests sufficient?**
Yes. `tests/goal4239_rayjoin_dedicated_long_repeat_profile_test.py` and `tests/goal4219_major_performance_target_map_test.py` provide comprehensive coverage:
- **Provenance:** Verifies git commit, clean status, and hardware.
- **Integrity:** Verifies count matches and schema versions.
- **Boundaries:** Recursively scans the payload for unauthorized claim flags.
- **Stability:** Confirms the manual route split remains visible and stable under long-run conditions.

### 5. Next Major Target
**What is the next step?**
The next major hurdles before a formal release packet are:
1.  **AMD/HIPRT Functional Parity:** Status is `blocked_pending_hardware`. Real AMD hardware is required to validate the HIPRT backend.
2.  **Release Grade Packet Assembly:** Transitioning from `done_internal_evidence` to a formal public release matrix requires an explicit packet containing exact artifact provenance, a documentation audit, and fresh multi-AI consensus over specific public claims.

## Verdict

The evidence is technically sound, the provenance is clean, and the claim boundaries are rigorously maintained. Goal 4239 successfully hardens the RayJoin performance story without overreaching.

**Accept.**
