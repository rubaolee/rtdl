# Gemini Review: Goal3567 v2.9 Composite Packet

Date: 2026-06-06
Reviewer: Gemini (external read-only)
Verdict: **accept-with-boundary**

---

## Scope

This review covers Goal3567, which creates a composite performance packet for v2.9 by combining unchanged rows from Goal3558 with targeted evidence from Goal3565 to reflect the RayDB sum fast-path improvement.

Sources examined:
- `docs/reports/goal3567_v2_9_composite_packet_after_raydb_sum_fastpath_2026-06-06.md`
- `docs/reports/goal3567_v2_9_composite_packet_after_raydb_sum_fastpath_a5000/summary.json`
- `tests/goal3567_v2_9_composite_packet_after_raydb_sum_fastpath_test.py`
- `docs/reports/goal3565_raydb_sum_fastpath_a5000_2026-06-06.md`
- `docs/reviews/goal3566_claude_review_goal3563_3565_v29_raydb_sum_fastpath_2026-06-06.md`

---

## Q1 — Is the composite packet method acceptable and clearly disclosed: 9 unchanged rows reused from the Goal3558 full 10-second packet, 2 RayDB rows replaced with Goal3565 targeted A5000 evidence?

**Yes, the composite packet method is acceptable and clearly disclosed.**
The Goal3567 report explicitly states its nature as a composite packet, detailing that 9 rows are reused from Goal3558 and 2 RayDB rows are replaced with Goal3565 targeted A5000 evidence. A clear rationale for this approach (avoiding a time-consuming rerun due to CPU-heavy initial rows) is provided. Both the human-readable report and the `summary.json` artifact consistently document the provenance of each row, with the `evidence_source` field explicitly identifying the origin of the data.

---

## Q2 — Does the packet correctly close Claude Goal3566's required packet-refresh item without pretending it is a raw all-row rerun?

**Yes, the packet correctly closes Claude Goal3566's required packet-refresh item.**
Goal3567 directly addresses the "Update the v2.9 summary packet" requirement highlighted as a blocking precondition in Claude's Goal3566 review. The report explicitly states its purpose is to refresh the v2.9 all-app performance table. Crucially, it clearly identifies itself as an "explicit composite packet, not a raw all-row rerun," avoiding any misrepresentation and upholding transparency regarding the data collection method.

---

## Q3 — Are the RayDB replacements numerically and semantically sound for internal v2.9 packet triage?

**Yes, the RayDB replacements are numerically and semantically sound.**
The speedup values for `raydb_optix_partner_resident_sum` (from `0.944269x` to `1.585627x`) and `raydb_optix_partner_resident_count` (from `0.972533x` to `1.009085x`) in Goal3567 directly match the validated results from Goal3565. The semantic justification for these improvements, as described in Goal3565 (reduction of global atomics for small dense grouped-i64 sum/sum_count via shared memory accumulation), is technically sound and directly addresses the identified weak rows. Claude's Goal3566 review also confirms the soundness of the Goal3565 evidence.

---

## Q4 — Do the report/artifact/test preserve all claim boundaries: no release, public speedup, broad RT-core, whole-app, true-zero-copy, paper reproduction, or package-install authorization?

**Yes, the report, artifact, and test consistently preserve all specified claim boundaries.**
The "Boundaries" section in the Goal3567 report explicitly lists all prohibited claims, reiterating that the evidence is for "internal benchmark evidence only." The `summary.json` artifact contains a `claim_boundary` object where `internal_results_only` is true and all other specified claims are false. Furthermore, the `tests/goal3567_v2_9_composite_packet_after_raydb_sum_fastpath_test.py` rigorously enforces these boundaries through assertions, verifying both the artifact's JSON fields and the presence of the "does not authorize" language in the report.

---

## Q5 — What, if anything, remains before v2.9 can be closed as an internal performance version and v2.10/performance-next can start?

The primary remaining item before v2.9 can be closed as an internal performance version is the **completion of this external Gemini review of the composite packet**.

Following this review, a decision is needed on whether the "remaining near-parity negatives" (i.e., rows with speedups slightly below `1.0x` that were reused from Goal3558) should be addressed as part of v2.9 cleanup or deferred to v2.10/performance-next.

The "recommended (non-blocking)" items identified in Claude's Goal3566 review also persist:
1.  **Symmetric count trial depth for Goal3565:** The count sanity probe used 3 trials, while the sum probe used 5. While sufficient for a sanity check, 5 trials would offer symmetric statistical coverage.
2.  **Single-pod evidence:** All measurements for Goals 3563–3565 were performed on a single A5000 pod. This is acceptable for internal closeout, but any external-facing claims would necessitate independent pod confirmation.
3.  **Chain review incorporating Goal3563–3565:** While this Gemini review provides an external perspective, a self-authored addendum from the primary author could further consolidate the audit trail.

---

## Summary

Goal3567 successfully creates a transparent and justified composite performance packet for v2.9, effectively incorporating the improvements from Goal3565 while reusing stable data from Goal3558. This approach correctly addresses the packet-refresh requirement from Claude's Goal3566 review without misrepresenting the data collection process. All RayDB replacements are numerically and semantically sound, and stringent claim boundaries are maintained and enforced across all documentation and tests.

With the completion of this external review, the path is clear for the internal closeout of v2.9, with the remaining decision pertaining to the treatment of minor near-parity regressions.