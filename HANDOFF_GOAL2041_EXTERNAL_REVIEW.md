# Handoff: Goal2041 Embree CPU Partner Weak-Row Repair Review

Please perform an independent Gemini review of Goal2041.

## Context

Goal2039 collected all-thread local Linux Embree CPU-partner evidence and exposed slow rows. Goal2041 repairs those weak rows with generic v2 mechanisms:

- Embree generic prepared fixed-radius threshold/count for facility coverage, ANN candidate coverage, and Hausdorff threshold decision.
- CPU-partner bbox broadphase plus backend-neutral native exact summary for polygon pair overlap and polygon set Jaccard.

The important boundary is that some repairs speed up decision/summary contracts, not richer exact semantics such as exact K=3 facility ranking or exact Hausdorff witness extraction.

## Files To Read

- `docs/reports/goal2039_embree_cpu_partner_all_thread_local_linux_evidence_2026-05-14.md`
- `docs/reports/goal2041_embree_cpu_partner_weak_row_repair_2026-05-14.md`
- `docs/reports/goal2041_embree_cpu_partner_weak_row_repair_2026-05-14.json`
- `docs/reports/goal2041_embree_cpu_partner_all_thread_large_repaired_v2/summary.json`
- `examples/rtdl_facility_knn_assignment.py`
- `examples/rtdl_ann_candidate_app.py`
- `examples/rtdl_hausdorff_distance_app.py`
- `examples/rtdl_polygon_pair_overlap_area_rows.py`
- `examples/rtdl_polygon_set_jaccard.py`
- `scripts/goal2037_embree_cpu_partner_all_thread_runner.py`
- `tests/goal2041_embree_cpu_partner_weak_row_repair_test.py`

## Questions

1. Does Goal2041 honestly explain why the rows were slow?
2. Are the generic fixes app-agnostic with respect to the RTDL engine?
3. Does the report clearly state which app requirements are solved and which are still unsatisfied?
4. Do the artifact timings support the stated improvements?
5. Are there wording risks or missing tests that should block accepting Goal2041 as bounded evidence?

## Required Output

Write your review to:

`docs/reviews/goal2042_gemini_review_goal2041_embree_weak_row_repair_2026-05-14.md`

Use one of these verdicts exactly: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Please state explicitly that this is an independent Gemini review and distinct from Codex authoring.
