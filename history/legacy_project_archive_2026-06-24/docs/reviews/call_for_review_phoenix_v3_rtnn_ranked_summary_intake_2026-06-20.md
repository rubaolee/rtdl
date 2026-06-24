# Call For Review: Phoenix V3 RTNN Ranked-Summary Candidate Intake

Date: 2026-06-20

Reviewer: Claude or Gemini

## Request

Please critically review the Phoenix V3 RTNN ranked-summary candidate intake.

The goal is not to approve V3 release and not to qualify an RTNN M7 row. The
goal is to decide whether this focused intake honestly extracts the current
RTNN ranked-summary evidence from the all-app calibrated artifact and correctly
keeps it as internal candidate evidence with wall-timing blockers visible.

## Files To Review

Primary report and intake:

- `docs/rebuild/v3/phoenix_v3_rtnn_ranked_summary_intake_2026-06-20.md`
- `docs/rebuild/v3/evidence/phoenix_v3_rtnn_ranked_summary_20260620/rtnn_ranked_summary_intake_summary.json`
- `docs/rebuild/v3/evidence/v3_claim_grade_all_benchmarks_calibrated_20260620/summary.json`

Builder and tests:

- `scripts/v3_phoenix_rtnn_ranked_summary_intake.py`
- `tests/v3_phoenix_rtnn_ranked_summary_intake_test.py`
- `scripts/run_test_matrix.py`
- `scripts/v3_release_wording_gate.py`

Status docs touched:

- `docs/rebuild/v3/README.md`
- `docs/rebuild/v3/v3_current_status_2026-06-20.md`

## Facts To Check

- The intake extracts six rows from the all-app calibrated artifact:
  - Embree and OptiX for clustered 65,536-point ranked summary;
  - Embree and OptiX for shell 65,536-point ranked summary;
  - Embree and OptiX for uniform 65,536-point ranked summary.
- All rows use the same exact fixed-radius ranked-summary contract per pair.
- Aggregate summaries match between backends.
- Hot elapsed OptiX/Embree ratios are:
  - clustered: 3.333x;
  - shell: 1.182x;
  - uniform: 1.084x.
- Wall OptiX/Embree ratios are:
  - clustered: 0.625x;
  - shell: 0.316x;
  - uniform: 0.303x.
- Therefore OptiX wins the hot metric but loses wall timing for all three
  distributions.
- Status remains `internal_rtnn_ranked_summary_candidate_not_m7`.
- Claim flags remain blocked, including public speedup, universal RTNN
  acceleration, paper reproduction, and true zero-copy.

## Questions

1. Does the intake honestly classify RTNN as internal candidate evidence, not
   closure?
2. Is `ranked_summary` the right generic capability label with
   `distribution_specific_candidate_wall_regression` as the status?
3. Are the M7 blockers complete enough?
4. Is the hot-metric win versus wall-timing loss clear enough in the report and
   JSON?
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

Decision: request external review before accepting the RTNN focused intake.

1. Was I foolish?

   No. The intake is deliberately conservative and asks review before closure.

2. If yes, what actions would make the decision foolish?

   It would be foolish to quote the clustered 3.333x hot-row win as universal
   RTNN acceleration while OptiX wall timing is slower for all three rows.

3. Was there another path?

   Yes. I could rerun the pod immediately, but the current artifact first needs
   classification.

4. Can I now try a different path that actually solves the problem?

   Yes. The review path tests whether the current RTNN artifact can serve as
   internal candidate evidence and identifies the exact gap before any pod
   rerun.
