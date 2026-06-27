# Independent Gemini Review of Goal2041: Embree CPU Partner Weak-Row Repair

**Review Date:** 2026-05-14

**Reviewer:** Gemini (Independent Reviewer)

This is an independent Gemini review of Goal2041, distinct from Codex authoring.

## Overall Assessment

Goal2041 effectively addresses the performance bottlenecks identified in Goal2039 for several Embree CPU-partner rows. The report clearly diagnoses the root causes of slowness as mismatches between benchmark implementations and actual application requirements, or inefficient candidate discovery strategies. The proposed generic fixes, leveraging fixed-radius threshold/count and CPU-partner bounding box broadphase with native exact summaries, demonstrate substantial performance improvements. The documentation is meticulous in outlining what has been solved and what remains an unsatisfied requirement, providing clear boundaries for the claims. The artifact timings strongly support the stated improvements, and the associated tests confirm the success of the repairs and adherence to defined boundaries.

## Responses to Questions

### 1. Does Goal2041 honestly explain why the rows were slow?

Yes, Goal2041 honestly and explicitly explains the root cause for each of the slow rows. For instance:
- `facility_knn_assignment` and `ann_candidate_search` were slow because they used expensive KNN row materialization or reranking for what were fundamentally simpler coverage decisions.
- `hausdorff_distance` was slow due to a mismatch between an exact distance summary requirement and a simpler threshold decision.
- `polygon_pair_overlap_area_rows` and `polygon_set_jaccard` suffered from inefficient candidate discovery using multiple positive LSI/PIP probes.

These explanations are specific and directly address the observed performance issues by identifying where the original benchmarks or implementations diverged from the most efficient path for the required contract.

### 2. Are the generic fixes app-agnostic with respect to the RTDL engine?

Yes, the generic fixes are designed to be app-agnostic. The report emphasizes the design lesson that "RTDL should keep the engine app-agnostic, but v2 needs explicit generic partner-side candidate and reduction policies." The implemented repairs reinforce this:
- **"Embree generic prepared fixed-radius threshold/count"**: This is a fundamental geometric primitive, applicable across various contexts for point-in-radius type queries, making it inherently app-agnostic.
- **"CPU-partner bbox broadphase + native exact summary"**: Bounding box broadphase is a standard spatial filtering technique, and the "native exact summary" implies the RTDL engine handles the core geometric computation in an engine-agnostic way, driven by a partner-side (Python) candidate policy.
The use of generic primitives and partner-side policies ensures that the RTDL engine itself remains flexible and reusable.

### 3. Does the report clearly state which app requirements are solved and which are still unsatisfied?

Yes, the report provides excellent clarity on this point in its "Design Boundary" section. It explicitly states that the "v2 Embree CPU-partner performance problem for the tested summary/decision contracts" is solved. Crucially, it then lists unsatisfied requirements:
- Exact K=3 facility fallback ranking at large scale.
- Exact ANN ranking or recall/latency optimization.
- Exact Hausdorff distance and witness extraction at large scale.
- Broad general polygon overlay.
This clear distinction prevents any ambiguity regarding the scope of the current repairs.

### 4. Do the artifact timings support the stated improvements?

Yes, the artifact timings robustly support the stated improvements. The "Repairs" table in `goal2041_embree_cpu_partner_weak_row_repair_2026-05-14.md` shows significant speedups for all repaired rows:
- `facility_knn_assignment`: 73.55x
- `polygon_pair_overlap_area_rows`: 6.28x
- `polygon_set_jaccard`: 15.70x
- `hausdorff_distance`: 91.44x
- `ann_candidate_search`: 55.90x
These improvements are substantial and are confirmed by the `goal2041_embree_cpu_partner_weak_row_repair_2026-05-14.json` data and validated by `tests/goal2041_embree_cpu_partner_weak_row_repair_test.py`. The "repaired full 16-row matrix passed on local Linux" further confirms the overall success.

### 5. Are there wording risks or missing tests that should block accepting Goal2041 as bounded evidence?

No, there are no significant wording risks or missing tests that should block accepting Goal2041 as bounded evidence.
- **Wording Risks**: The report's "Claim Boundary" sections are meticulously crafted to avoid over-claiming, explicitly stating what is *not* allowed to be claimed (e.g., "v2.0 release readiness", "broad all-app speedup claims", "exact ranked KNN solved"). This precise language effectively mitigates wording risks.
- **Missing Tests**: The `tests/goal2041_embree_cpu_partner_weak_row_repair_test.py` provides good coverage, verifying:
    - The explicit nature of report boundaries.
    - That the entire repaired matrix passes.
    - That the stated speedups are achieved (with minimum thresholds).
    - That the repaired rows correctly utilize the intended generic partner paths.
Given the explicit declaration of unsatisfied requirements, the current test suite is sufficient for validating the claims made by Goal2041.

## Verdict

`accept-with-boundary`

Goal2041 successfully identifies and rectifies performance issues in critical Embree CPU-partner workflows by implementing well-reasoned, generic solutions. The report is clear, concise, and backed by strong empirical evidence and appropriate testing. The defined boundaries are well-articulated, ensuring a clear understanding of the scope and limitations of the achieved improvements.
