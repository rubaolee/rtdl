**Verdict: accept_with_boundary**

Gates 1–3 disposition:

| Gate | Requirement | Evidence | Status |
|------|-------------|----------|--------|
| 1 | Post-fix Barnes-Hut geomean ≥ 0.900x | 15.811x (four-row: Embree/OptiX × 32K/131K) | ✓ Closed |
| 2 | Explicit single-query prepare penalty boundary | 0.1137s @ 32K, 0.4912s @ 131K slower than V2.14 single-query; amortizes ~4 repeated queries; claims scoped to prepared/repeated-query only | ✓ Closed |
| 3 | Release-facing wording scan | v3_release_wording_gate.py → pass, violations [] | ✓ Closed |

**Remaining required item:**
- **Gate 4: Codex consensus** — not yet written; this verdict satisfies the precondition for Codex to proceed.

**Scope boundary (unchanged):** M24 is accepted as a focused Barnes-Hut prepared-query residency blocker fix only. No release authorization, no public claim authorization, no broad or whole-app performance authorization is granted or implied. The single-query penalty boundary stated in gate 2 must be reproduced verbatim in any release-adjacent documentation before M24 can contribute to a release claim.
