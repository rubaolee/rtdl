I now have everything I need. Here is the formal review.

---

## External AI Review — Phoenix V3 AABB Native Query-Handle Final M7 Review

**Reviewer:** Claude (Sonnet 4.6), acting as external AI reviewer  
**Date:** 2026-06-21  
**Review scope:** Two exact stable candidate row IDs only

---

### Verdict: `approve-with-conditions`

One P0 blocker remains open that this review cannot close. Two P1 items require documented caveats in the promotion record. Subject to those conditions, the evidence is sufficient to promote the two rows to M7.

---

### Answers to Review Questions

**Q1 — Reusable generic capability, not Contact Manifold-specific?**

Yes. The capability tag is `aabb_candidate_stream`. The primitive contract is `generic_prepared_aabb_index_query_2d_native_query_handle`. The Contact Manifold is the calling harness, not the subject of the claim. The native cache metrics (`native_range_intersection_entries`, `range_intersection_hits`) are AABB index metrics, not solver metrics. The optimization — reusing a prepared native box-query handle across repeated `range_intersection_rows` calls — is a property of the `AABB_INDEX_QUERY_2D` primitive, not of the Contact Manifold solver. The boundary is correctly drawn.

**Q2 — Same-contract comparison for both rows?**

Yes. Both Embree and OptiX are invoked under the identical `generic_prepared_aabb_index_query_2d_native_query_handle` contract. The raw oracle evidence confirms both backends return identical row counts against the same fixtures (10 and 13 rows respectively). The `jittered_grid` dataset, warmup, repeat, and hardware are uniform across both candidate rows. The fact that OptiX prepare is slower than Embree does not break contract parity — it is a disclosed sub-phase difference within the same end-to-end operation.

**Q3 — Evidence sufficient for M7 promotion?**

Yes, with the caveat in the P1 section below.

- Two serious rows at the predeclared scales (32,768 and 65,536): ✓
- Six fresh independent POD runs, three per scale: ✓
- Weakest fresh cold-plus-collect speedup: 1.644x, against a 1.20x floor: ✓
- Independent closed-boundary CPU AABB oracle with four fixture types (zero-overlap, duplicate-prone, edge-touch, dense many-to-many): ✓
- OptiX fail-closed overflow documented: ✓
- Source manifest SHA-256: ✓
- Stable candidate row IDs defined without promotion: ✓

The local gate evidence is complete. The one remaining required procedural step is Codex consensus (Q7 below).

**Q4 — Draft wording avoids hiding slower OptiX prepare?**

Yes. Both draft rows explicitly use "cold prepare plus collect wall time" as the speedup metric. The prepare note in the row wording gate states "OptiX prepare remains slower than Embree on this row" and forbids prepare-only claims. The aggregate metric absorbs the slower prepare phase; a net speedup of 1.637–1.719x despite slower prepare is internally consistent with a fast collect phase and proves the case without misrepresenting the sub-phases.

**Q5 — Exact public wording permitted if approved**

For `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`:

> On an NVIDIA RTX 4000 Ada Generation GPU, RTDL's OptiX native prepared-query-handle route for `AABB_INDEX_QUERY_2D range_intersection_rows` was **1.719x** faster than the RTDL Embree route on a jittered-grid workload with 32,768 AABBs and 32,768 packed box queries (cold prepare plus collect wall time; warmup=3, repeat=50). Query total was **1.867x** faster. OptiX prepare alone remains slower than Embree; the speedup applies to end-to-end prepared-session time. This result is row-scoped and does not claim Contact Manifold solver acceleration, broad AABB-index acceleration, or V3-over-V2 speedup.

For `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`:

> On an NVIDIA RTX 4000 Ada Generation GPU, RTDL's OptiX native prepared-query-handle route for `AABB_INDEX_QUERY_2D range_intersection_rows` was **1.637x** faster than the RTDL Embree route on a jittered-grid workload with 65,536 AABBs and 65,536 packed box queries (cold prepare plus collect wall time; warmup=3, repeat=50). Query total was **1.743x** faster. OptiX prepare alone remains slower than Embree; the speedup applies to end-to-end prepared-session time. This result is row-scoped and does not claim Contact Manifold solver acceleration, broad AABB-index acceleration, or V3-over-V2 speedup.

**Q6 — Exact public wording that must remain forbidden**

- Any claim that OptiX prepare is faster than Embree prepare for this workload.
- Any wording attributing the speedup to "Contact Manifold solving," "physics engine acceleration," "collision detection," or related solver framing.
- "Phoenix V3 is faster than V2" or any aggregate V3-over-V2 speedup claim.
- "AABB index queries are faster with OptiX" (too broad — applies only to the jittered-grid prepared-session route at the two specific scales).
- "RTDL is release-ready," "V3 is production-ready," or any release-readiness claim.
- Speed claims at scales, datasets, or hardware not covered by the evidence (non-jittered datasets, non-RTX 4000 Ada, scales other than 32,768 and 65,536).
- Claims that all `AABB_INDEX_QUERY_2D` operations are accelerated (only `range_intersection_rows` with native query-handle reuse is in evidence).

**Q7 — P0/P1 blockers still open?**

**P0 — Open:**

`codex_consensus_response_missing_after_external_review`

This review closes `external_ai_review_missing` and `external_public_wording_review_missing` (the draft wording reviewed above is approved row-scoped). However, the process requires a Codex consensus response after external review. This review does not substitute for that step. M7 promotion must not be recorded until Codex consensus is obtained and logged.

**P1 — Caveat required, not a promotion blocker:**

Source provenance carries a noted gap: `git_head` returns `fatal: not a git repository`. The SHA-256 source manifest (`f7d8a0ae6e39c691bf7c949b23741181abcc24fc3e3ef405f73c7a113d1e4422`) satisfies the fallback provenance gate per the Huygens review, but the M7 promotion record must explicitly note the absence of a `git_head` and confirm the SHA-256 manifest as the provenance artifact. This is not a promotion blocker, but omitting the note would be.

**P1 — Wording addition required:**

The approved public wording above (Q5) includes the prepare-phase disclosure. That sentence ("OptiX prepare alone remains slower than Embree") must not be omitted in any published form. Its removal would make the wording misleading.

**Q8 — Approval scope?**

This approval is **row-scoped only** to the two exact stable candidate row IDs listed above. It does not authorize:

- Any other `aabb_candidate_stream` rows.
- Any Contact Manifold solver rows.
- Any V3-over-V2 aggregate claim.
- Aggregate Phoenix V3 release authorization.
- Any row outside the `jittered_grid` / RTX 4000 Ada / native-query-handle configuration.

---

### P0 Blockers

| # | Blocker | Status |
|---|---------|--------|
| P0-1 | `codex_consensus_response_missing_after_external_review` | **Open** — must be obtained before M7 rows are recorded |

### P1 Items (must be documented in promotion record)

| # | Item |
|---|------|
| P1-1 | git_head absence — note that provenance rests on SHA-256 manifest only, no git commit |
| P1-2 | Approved wording must include the prepare-phase disclosure sentence; omission is forbidden |

---

### Final Statement

**The two rows `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50` and `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50` may be promoted to M7 once the Codex consensus step is completed.** The local evidence base (raw oracle, stability, source provenance, fail-closed overflow, stable row IDs, draft wording) is sufficient. This review closes `external_ai_review_missing` and `external_public_wording_review_missing`. The sole remaining hard gate before M7 is `codex_consensus_response_missing_after_external_review`.

**Aggregate Phoenix V3 release authorization remains false.** This approval covers exactly two row-scoped measurements on one hardware configuration under one dataset. It does not constitute evidence of general AABB acceleration, Contact Manifold solver improvement, V3-over-V2 speedup, or release readiness.
