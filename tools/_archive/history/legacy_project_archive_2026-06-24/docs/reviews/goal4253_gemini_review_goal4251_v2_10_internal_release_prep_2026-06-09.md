# Independent Review: Goal4251 v2.10 Internal Release-Prep Packet

- Date: 2026-06-09
- Reviewer: Gemini
- Verdict: `accept`

## Summary

This review covers the Goal4251 v2.10 internal release-prep packet, which synthesizes recent evidence from Goals 4235, 4239, 4243, 4248, 4249, and 4250. The packet accurately represents the current project state—strong internal NVIDIA/OptiX evidence for the promoted benchmark surface—while strictly maintaining non-authorizing boundaries for public claims and release action.

## Reviewer Questions

### 1. Does Goal4251 accurately summarize Goals4235, 4239, 4243, 4248, 4249, and 4250 without overstating release readiness?

**Yes.** Goal4251 provides a concise and accurate summary of the recent evidence chain:
- **Goal4235:** Validates ten benchmark front doors.
- **Goal4239/4243:** Refreshes RayJoin and Hausdorff/contact/triangle with dedicated long-repeat evidence.
- **Goal4248:** Confirms zero hard blockers in the current public documentation scan.
- **Goal4249/4250:** Updates the target map and validates the full slice on the RTX 4000 Ada pod.

The report repeatedly emphasizes that this is "internal pre-release evidence, not the exact public release packet" and concludes that "it is not enough to press a release button by itself."

### 2. Are the blocked gates complete and correctly framed, especially release, broad speedup, whole-app, RayJoin superiority, paper reproduction, package install, true zero-copy, automatic partner selection, and AMD/HIPRT wording?

**Yes.** The "Still Blocked Or Deferred" section is comprehensive. It correctly frames:
- **Broad/Whole-App Speedup:** Blocked as evidence is contract-scoped and does not cover non-RT phases.
- **RayJoin/Paper Reproduction:** Blocked; apps are reconstruction instruments, not full reproductions.
- **Package Install:** Explicitly identified and repaired in Goal4248; remains blocked in the Goal4251 boundary.
- **True Zero-Copy:** Blocked; residency evidence exists but is not a general product guarantee.
- **Automatic Partner Selection:** Blocked; choice remains explicit and user-owned.
- **AMD/HIPRT:** Blocked pending actual AMD hardware.

### 3. Does Goal4251 preserve the principle that RTDL is a generic language/runtime with explicit user-chosen partners, not an app library or hidden dispatcher?

**Yes.** This principle is preserved through:
- The explicit blocking of "Automatic partner/backend selection."
- The framing of the RayJoin policy as a "contract-split" rather than a single app-micro-tuned number.
- The "Still Blocked" reasoning stating "Partner and backend choice stays explicit and user-owned."
- The "Reviewer Questions" section itself, which prompts for confirmation of this specific design rule.

### 4. Does the target map remain structurally non-authorizing after Goal4249?

**Yes.** The implementation in `src/rtdsl/current_major_performance_targets.py` is structurally non-authorizing. The `CurrentMajorPerformanceTarget` class includes a `__post_init__` check that raises a `ValueError` if any authorization flag (e.g., `release_authorized`, `public_speedup_claim_authorized`) is set to `True`. All currently defined targets in the map have these flags set to `False`.

### 5. Assuming no AMD claim is made, what evidence or wording remains before a formal release packet can be assembled?

The following items are identified as remaining requirements:
- **Formal Release Packet:** An explicit assembly of artifact provenance for the release candidate.
- **Final Public Claim Wording:** Exact text for public-facing release notes/claims, which requires a separate review.
- **Fresh Release Consensus:** The mandatory multi-AI consensus over the final, exact release packet and wording.
- **Explicit User Decision:** A directive to transition from "release-prep" to "release."

## Final Verdict

The packet is a high-quality synthesis of internal readiness. It successfully closes the v2.10 evidence loop without leaking authorization or overstating the current capabilities.

**Verdict: `accept`**
