# Call For Review: Phoenix V3 Triangle Prepared-Graph Candidate Intake

Date: 2026-06-20

Reviewer: Claude or Gemini

## Request

Please critically review the Phoenix V3 Triangle prepared-graph candidate
intake.

The goal is not to approve V3 release and not to qualify a Triangle M7 row. The
goal is to decide whether this focused intake honestly extracts the current
Triangle evidence from the all-app calibrated artifact and correctly keeps it
as internal candidate evidence with M7 blockers visible.

## Files To Review

Primary report and intake:

- `docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md`
- `docs/rebuild/v3/evidence/phoenix_v3_triangle_prepared_graph_20260620/triangle_prepared_graph_intake_summary.json`
- `docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json`

Builder and tests:

- `scripts/v3_phoenix_triangle_prepared_graph_intake.py`
- `tests/v3_phoenix_triangle_prepared_graph_intake_test.py`
- `scripts/run_test_matrix.py`
- `scripts/v3_release_wording_gate.py`

Status docs touched:

- `docs/rebuild/v3/README.md`
- `docs/rebuild/v3/v3_current_status_2026-06-20.md`

## Facts To Check

- The intake extracts four rows from the all-app calibrated artifact:
  - Embree and OptiX for `triangle_count_rt_graph_2a1_cliques_20000`;
  - Embree and OptiX for `triangle_count_rt_graph_2a1_cliques_80000`.
- Both groups use the same contract:
  `rt_graph_2a1_mapped_to_generic_ray_triangle_any_hit`.
- Both groups use the same primary metric source:
  `timing_ms.query_median_ms converted-ms-to-sec`.
- All rows match the triangle-count oracle.
- Phase timing validation accepts under `rtdl.partner.v2.4`.
- Embree rows are not RT-core accelerated; OptiX rows are RT-core accelerated.
- Claim flags remain blocked.
- Reported internal hot-query ratios are:
  - 20,000 cliques: 116.060x OptiX over Embree;
  - 80,000 cliques: 347.232x OptiX over Embree.
- The packet explicitly keeps status as:
  `internal_triangle_prepared_graph_candidate_not_m7`.
- The report says the rows are synthetic K4 clique ladders, not paper datasets,
  not graph database workloads, not full triangle-counting app evidence, and
  not M7-qualified release rows.

## Questions

1. Does the intake honestly classify Triangle as internal candidate evidence,
   not closure?
2. Is `prepared_graph_chunk` the right generic capability label for this
   candidate, or should it be weakened until the M113/M120 prepared-graph chunk
   executor linkage is proven?
3. Are the M7 blockers complete enough?
4. Does the report make hot-query query-median timing versus end-to-end timing
   clear enough?
5. Does the test enforce the right facts without overfitting?
6. What P0/P1 fixes are required before Codex can close this bounded intake
   packet as reviewed internal candidate evidence?

## Required Verdict Format

Please return:

- verdict: approve / approve-with-required-fixes / request-changes
- P0 findings
- P1 findings
- P2 suggestions
- final recommendation

## Goal-Level Decision Audit

Decision: request external review before accepting the Triangle focused intake.

1. Was I foolish?

   No. The intake is deliberately conservative and asks review before closure.

2. If yes, what actions would make the decision foolish?

   It would be foolish to quote the 347.232x row as release performance or
   public RT-Graph evidence without external review and M7 qualification.

3. Was there another path?

   Yes. I could rerun the pod immediately, but the current artifact first needs
   classification.

4. Can I now try a different path that actually solves the problem?

   Yes. The review path tests whether the current Triangle artifact can serve
   as internal candidate evidence and identifies the exact gap before any pod
   rerun.
