---

## Goal1263 External Review — Structured Response

**Reviewer:** Claude (Sonnet 4.6), acting as one of three required AI reviewers  
**Date:** 2026-05-04  
**Scope:** Goal1262 full-matrix intake + Goal1263 polygon-pair scale sweep

---

### Verdict: ACCEPT WITH CHANGES

---

### Q1 — Is the Goal1262 interpretation correct?

**Yes, with one minor precision note.**

The three-part characterization holds:

- **DB (`execution_unblocked_but_not_public_speedup_ready`):** Confirmed. The two blockers (100k ceiling, Jaccard parity) are resolved. The performance evidence is mixed: 100k one-shot total favors OptiX (0.900), but warm-query median at both scales favors Embree (1.104 at 30k, 1.270 at 100k). "Unblocked but not speedup-ready" is the correct call. No objection.

- **Graph and Jaccard (`correct_but_total_optix_slower`):** Confirmed. Graph total ratios are 1.489 and 1.287; Jaccard total ratios are 2.925 and 1.972. Correctness passes. Total path is slower at all scales. Wording is accurate.

- **Polygon-pair (`best_current_positive_candidate`):** Confirmed. At 40k both candidate and pipeline favor OptiX; the 10k candidate ratio of 1.205 (slower) is not suppressed in the report and should not be. The report handles it correctly by distinguishing candidate and pipeline at 10k. No objection.

**Precision note:** The 100k one-shot total OptiX speedup (0.900) in DB should not silently migrate into any summary as a positive data point, because warm-query median at 100k is 1.270. The current intake wording handles this correctly, but reviewers downstream should be warned: the 0.900 figure is real but cherry-picked if cited without the 1.270 companion.

---

### Q2 — Does Goal1263 provide sufficient same-contract evidence?

**Yes, with the `candidate_count_matches_expected` flag noted.**

Goal1263 adds two new scales (80k, 160k) on the same machine (RTX A5000), same scripts, same output mode, same `--chunk-copies 512`. Combined with Goal1262's 40k result, the evidence is:

| Scale | Candidate ratio | Pipeline ratio | Parity |
|------:|----------------:|---------------:|--------|
| 40k   | 0.835           | 0.791          | true   |
| 80k   | 0.682           | 0.827          | true   |
| 160k  | 0.707           | 0.815          | true   |

Three consecutive scales, all parity-passing, all showing material speedups on both candidate and pipeline. The scale trend is coherent: candidate advantage grows from 40k to 80k then stabilizes, pipeline advantage is consistent. This is sufficient same-contract evidence to treat `polygon_pair_overlap_area_rows` as a **bounded positive OptiX performance candidate** for external review.

The `candidate_count_matches_expected: false` flag (discussed in Q4) does not invalidate this conclusion but must be disclosed.

---

### Q3 — Is the proposed boundary acceptable?

**Yes, the boundary is correctly drawn.**

The three-part boundary holds:

1. **RT-assisted LSI/PIP candidate discovery + native C++ exact area continuation:** Accurate. The OptiX script (`goal877_polygon_overlap_optix_phase_profiler.py`) handles candidate discovery; the exact area computation is delegated to native C++. The pipeline timing includes both phases.

2. **Not monolithic GPU polygon overlay:** Correct. No full-polygon rasterization or GPU-resident area kernel is claimed. OptiX is doing intersection-test-accelerated candidate filtering only.

3. **Not whole-app speedup / not broad GIS acceleration:** Correct. The evidence is limited to one application row (`polygon_pair_overlap_area_rows`) at one scale range (40k–160k) on one GPU (RTX A5000). DB, graph, and Jaccard are not positive candidates under current evidence.

This boundary is tight enough to be defensible and specific enough to be useful.

---

### Q4 — Is `candidate_count_matches_expected: false` acceptable for positive wording?

**Conditionally acceptable — requires disclosure and a scheduled reconciliation item. Does not block positive wording.**

**Why it does not block:** Summary parity is `true` at all four scales (10k, 40k, 80k, 160k). Summary parity means the final computed overlap areas match between Embree and OptiX. If the candidate set were unsoundly pruned (i.e., missing true pairs), summary parity would fail. It does not. Therefore the OptiX candidate set is at least sufficient for correctness of the output, regardless of whether the diagnostic count matches a profiler expectation.

**Why it must be disclosed:** `candidate_count_matches_expected: false` indicates a gap between the profiler's internal expected-count model and the actual OptiX output. This could mean:
- The expected-count field is computed from an Embree-path assumption that does not transfer to the OptiX path (i.e., the diagnostic contract is too strict); or
- OptiX returns a different (possibly larger) candidate superset that still yields correct areas.

Neither explanation undermines the speedup claim, but both represent a diagnostic contract that is not fully validated. Public wording that describes OptiX as "correct" must qualify this as correctness-by-summary-parity under the current profiler contract, not correctness-by-full-diagnostic-agreement.

**Required action:** Schedule `candidate_count_matches_expected` diagnostic reconciliation as a tracked v1.2 item. The reconciliation does not block the bounded v1.1 positive candidate claim.

---

### Q5 — Exact allowed and disallowed wording

#### Allowed wording

- "OptiX candidate discovery is faster than Embree for `polygon_pair_overlap_area_rows` at 40k, 80k, and 160k on the RTX A5000, with ratios of 0.835, 0.682, and 0.707 respectively."
- "The OptiX observed pipeline is faster than Embree at 10k, 40k, 80k, and 160k, with a ~1.2x total-pipeline speedup at 160k."
- "RT-assisted candidate discovery shows a ~1.4x speedup at 80k–160k scales."
- "`polygon_pair_overlap_area_rows` is the strongest current v1.1 OptiX/Embree positive candidate, with consistent speedups at three of four tested scales."
- "Correctness is confirmed by summary parity at all tested scales under the current profiler contract."
- "This is a bounded positive candidate for RT-assisted LSI/PIP candidate discovery plus native C++ exact area continuation."

#### Disallowed wording

- ~~"OptiX polygon overlay is faster"~~ — implies monolithic GPU overlay which does not exist in this pipeline.
- ~~"GPU polygon overlay acceleration"~~ — same reason.
- ~~"RTDL is faster with OptiX"~~ — DB, graph, and Jaccard are not positive candidates; this over-generalizes.
- ~~"OptiX speeds up polygon overlap"~~ — too broad; only the candidate-discovery phase, not the full overlap computation.
- ~~"Whole-app speedup"~~ — not supported.
- ~~"Broad GIS acceleration"~~ — not supported.
- ~~"OptiX is correct for polygon pair"~~ (unqualified) — must include the summary-parity qualification and note the unresolved `candidate_count_matches_expected` diagnostic.
- ~~Any speedup claim for DB, graph, or Jaccard~~ — these are not public speedup candidates under current evidence.

---

### Required Changes Before Consensus

1. **Disclose the diagnostic flag.** Any public statement on polygon-pair correctness must include language such as: *"Correctness is judged by summary-parity under the current profiler contract; candidate-count diagnostics are not yet fully reconciled and are a tracked v1.2 item."*

2. **Do not cite the DB 100k one-shot total (0.900) as a positive data point** in any summary that omits the warm-query median (1.270). If DB appears in any public context, both figures must appear together with the `execution_unblocked_but_not_public_speedup_ready` label.

3. **Confirm second and third AI reviewers explicitly accept the `candidate_count_matches_expected` boundary** before the consensus file is written. This review accepts it conditionally; the other two reviewers should assess independently.

---

### Additional Tests or Pod Reruns Required

**No additional pod reruns required before consensus** under the current bounded claim. The existing 4-scale dataset (10k, 40k, 80k, 160k) on RTX A5000 is sufficient for the bounded positive candidate claim.

**Recommended but not blocking:**
- A single verification run at one intermediate scale (e.g., 20k or 60k) would make the scale trend unambiguous and remove any concern about cherry-picking.
- Diagnostic reconciliation of `candidate_count_matches_expected` should be run before any future strengthening of the correctness claim beyond summary-parity.

---

### Summary

Goal1262's interpretation is sound. Goal1263 provides sufficient same-contract evidence at three consecutive larger scales. The proposed boundary is correctly drawn. The `candidate_count_matches_expected: false` flag is acceptable with disclosure and a scheduled reconciliation item — it does not block the bounded positive wording. Two required changes (diagnostic disclosure language, DB data presentation discipline) must be incorporated before the consensus file is written and public docs are changed.
