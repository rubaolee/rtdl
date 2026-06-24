Now I have everything I need. Let me write the final review.

---

## Final Review: Phoenix V3 RTDBSCAN Component-Signature Optimized RTX Evidence

**Reviewer:** Claude (Sonnet 4.6) — final confirmation round
**Date:** 2026-06-21
**Prior ruling:** Approve only with changes — Option A (narrow to 65,536) or Option B (rerun large rows at repeat=5/warmup=1, disclose continuation/dataset/correctness boundaries)

---

### 1. Final Verdict

**APPROVED under Option B — one row-scoped M7 claim.**

All Option B conditions from the prior review are satisfied by the updated packet. The prior P0-A blocker (2 measured iterations at large scale) is resolved. The prior P0-B requirement (correctness basis documented) is resolved. The prior P1-B and P1-C requirements (dataset geometry, continuation bottleneck) are in the candidate wording. No new structural issues have appeared.

---

### 2. Exact Approved Wording

The candidate wording from the updated packet is accepted verbatim, with one correction: the floor figure updates from the stale `1.116x` (repeat=3 original run) to `1.102x` (repeat=5 rerun confirmed value). The packet itself already carries `1.102x` in the JSON — this is confirmation that the wording is correct as written:

> RTDL V3 includes a generic component-signature continuation route where prepared OptiX fixed-radius threshold columns feeding the same Numba component signature are **1.102x to 1.236x** faster end-to-end than the same-contract Embree route on zero-noise four-cluster synthetic clustered3d rows from 65,536 to 524,288 points on an RTX 4000 Ada pod; at 262,144 and 524,288 points, the Numba continuation still dominates wall time.

This wording is approved for M7 row-scoped publication. The floor (`1.102x`) now rests on 4 measured iterations (repeat=5, warmup=1), not 2. The peak (`1.236x`) at 65,536 points is also at repeat=5.

---

### 3. Required Caveats That Must Accompany Any Public Use

All of the following must remain in place in any document that cites this row. They are currently present in the packet and must not be stripped during promotion:

| Caveat | Status | Location in packet |
|---|---|---|
| Route is component-signature only, not full DBSCAN label publication | ✅ Present | `.md` interpretation section |
| Correctness at ≥65,536 points is OptiX/Embree intra-run agreement, not independent CPU reference | ✅ Present | Both JSON `large_scale_correctness_basis` fields |
| Dataset is zero-noise four-cluster synthetic `clustered3d` | ✅ Present | Candidate wording |
| Numba continuation dominates at ≥262,144 points | ✅ Present | Candidate wording |
| Hardware is a single RTX 4000 Ada pod, single run date | ✅ Present | Candidate wording pins hardware |
| Not a V2 comparison, not a paper claim, not a broad V3 claim | ✅ Present | All `*_authorized: false` flags and forbidden-wording list |

---

### 4. P0/P1 Blockers — Status After Update

**Prior P0-A (thin repeat count at 262,144 and 524,288):** RESOLVED.
The `large_repeat5` artifact confirms `repeat=5, warmup=1, measured_iterations=4` for both rows. `all_pairs_repeat5_warmup1: true`. Speedups at 262,144 (1.1236x) and 524,288 (1.1020x) are stable across 4 measured iterations. The prior floor of `1.116x` from 2 iterations moved to `1.102x` with 4 iterations — slightly less favorable, same direction, now defensible.

**Prior P0-B (correctness basis undisclosed):** RESOLVED.
Both JSON artifacts carry `"large_scale_correctness_basis": "OptiX/Embree intra-run canonical component-signature agreement, not independent CPU reference validation"`. The public wording does not imply reference-validated correctness.

**Prior P1-B (dataset geometry):** RESOLVED. Wording includes "zero-noise four-cluster synthetic clustered3d."

**Prior P1-C (continuation bottleneck):** RESOLVED. Wording includes the continuation-dominates clause.

**Remaining P1 (unchanged, not a blocker):** Single pod, single run date, no stddev. The approved wording mitigates this by pinning hardware explicitly. A second independent run would strengthen the evidence but is not required before M7 for a row this narrow.

**No new P0 or P1 blockers introduced by the updated packet.**

---

### One Narrow Scope Reminder

This approval covers exactly one capability row: `component_union`, component-signature continuation route, same-contract OptiX vs Embree, RTX 4000 Ada, `clustered3d` synthetic dataset, 65,536–524,288 points. It does not authorize:

- Any RTDBSCAN paper reproduction claim
- Any full DBSCAN end-to-end claim
- Any V3-over-V2 claim
- Any claim beyond the component-signature route
- Any generalization to noisy datasets, non-equal clusters, or other hardware

The `m7_promotion_authorized` flag in the JSON may now be set to `true` for this specific capability row. All other `*_authorized: false` fields remain correct and must not change.
