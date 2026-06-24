Review written to `docs/reviews/claude_phoenix_v3_twelve_row_release_readiness_review_2026-06-21.md`.

---

## Verdict: `approve-blocked-not-release`

### Direct answers to the five questions

**Q1 — Is twelve rows a responsible major release?**
No. Two concrete blockers prevent it independently: `point_location_topology_stream` has zero M7 rows (8/9 families covered, minimum is 9), and there is no fresh twelve-row aggregate 2-AI consensus — the existing consensus covered eleven rows and returned `not-release-ready-fix-p0`.

**Q2 — Is `blocked_not_release` honest and sufficient?**
Yes, with one P1 gap: the install/reproducibility gate still says `release_scope: source_tree_pod_gated_eleven_row`. The twelfth row (Barnes-Hut fused partner) was added after the install gate was reviewed. No functional problem — the Numba CUDA row uses the same pod environment — but the scope label is stale and a consensus reviewer will notice it.

**Q3 — Is the wording gate correct for twelve rows?**
Yes. All 12 row IDs are in `EXPECTED_ROW_SCOPED_M7_IDS`, the Barnes-Hut disclosures are in `REQUIRED_STRINGS`, and the gate passes with zero violations. P1: there is no explicit `POSITIVE_OVERCLAIM_PATTERNS` regex that catches `13.591x` used without the metadata-only context; the required-string check verifies the disclosure exists but not that the overclaim is absent from a new document.

**Q4 — Is the engine-queue closure correct?**
Yes, not too aggressive. All four closed items have real 2-AI reviews and concrete M7 contributions. The Spatial and Barnes-Hut RT-native closures to future-research are appropriate — the author-gap and M131 semantic-gate barriers are real, and the reopen conditions are measurable.

**Q5 — What must change before the next release decision?**

| Priority | Item |
|---|---|
| P0 | Get a fresh twelve-row 2-AI release-readiness consensus (fix P1-1 first) |
| P0 | Resolve `point_location_topology_stream`: either new M7 evidence (RTDL ≤ 1.866 ms on br_county.cdb) or explicit scope-floor reduction from 9 to 8 |
| P1-1 | Update install gate scope from `source_tree_pod_gated_eleven_row` to twelve-row |
| P1-2 | Obtain external review acceptance for app catalog, backend maturity, performance model |
| P1-3 | Get reviewer acceptance that the tutorial surface (07–15) is coherent for release review |
| P1-4 | Add `13.591x` overclaim scanner pattern to `v3_release_wording_gate.py` |
| P1-5 | Final placement and reviewer acceptance of negative-row wording (0.065x / 0.034x) |
