# Call For Review: Phoenix V3 RayDB M28 Grouped-Reduction Evidence

Date: 2026-06-20

Reviewer: Claude or Gemini

## Request

Please critically review the Phoenix V3 RayDB M28 grouped-reduction evidence.

The goal is not to approve V3 release. The goal is to decide whether this
bounded M28 work can be accepted as internal generic grouped-reduction evidence
under the Phoenix V3 / Goal4392 rebuild rules.

## Files To Review

Primary evidence and report:

- `docs/rebuild/v3/phoenix_v3_raydb_m28_grouped_reduction_pod_evidence_2026-06-20.md`
- `docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620/m28_raydb_grouped_reduction_524288.json`
- `docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620/m28_raydb_grouped_reduction_524288.log`
- `docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620/overlarge_1048576_attempt_status.txt`
- `docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620/m28_raydb_grouped_reduction_1048576.log`

Supporting code and tests:

- `scripts/v3_0_m28_raydb_prepared_grouped_refresh.py`
- `tests/v3_phoenix_raydb_m28_evidence_test.py`
- `scripts/v3_release_wording_gate.py`
- `scripts/run_test_matrix.py`

Status docs touched:

- `docs/rebuild/v3/README.md`
- `docs/rebuild/v3/v3_current_status_2026-06-20.md`

## Facts To Check

- The successful run used 524,288 generated rows and 2,048 groups on an NVIDIA
  RTX 4000 Ada Generation pod.
- The same generic app-agnostic grouped i64 reduction primitive is used for
  Embree and OptiX.
- No RayDB SQL engine, planner, transaction system, or app-specific native
  engine logic is introduced by this packet.
- CPU reference parity passed on all rows.
- All rows report:
  - `prepared_steady_state=true`
  - `prepared_primitive_payload_reused=true`
  - `prepared_ray_batch_reused=true`
  - `partner_continuation_required=false`
  - `public_speedup_claim_authorized=false`
- Prepared hot-query same-contract ratios are:
  - count: Embree 14.881 ms, OptiX 1.700 ms, Embree/OptiX 8.752x
  - sum: Embree 2104.065 ms, OptiX 13.316 ms, Embree/OptiX 158.010x
- The `sum` row has heavy setup/cold prepare costs:
  - Embree `workload_build_sec`: 217.964 s
  - Embree `cold_prepare_total_sec`: 218.028 s
  - OptiX `workload_build_sec`: 213.265 s
  - OptiX `cold_prepare_total_sec`: 215.843 s
- Therefore the result is hot-query evidence only, not end-to-end database or
  application speedup evidence.
- The 1,048,576-row exploratory attempt was stopped after more than 20 minutes
  without producing JSON and is preserved as an overlarge attempt.
- Phoenix M7-qualified release rows remain 0.

## Questions

1. Is this evidence honestly classified as internal generic grouped-reduction
   evidence?
2. Are the timing boundaries strong enough, especially around hot-query ratios
   versus the 213s+ workload/build/cold-prepare costs?
3. Is the preserved 1,048,576-row overlarge attempt handled honestly?
4. Does the evidence avoid app-specific native engine logic?
5. Does the test enforce the right claims and non-claims without overfitting to
   a desired result?
6. What P0/P1 changes are required before Codex can close this bounded RayDB
   M28 evidence goal?

## Required Verdict Format

Please return:

- verdict: approve / approve-with-required-fixes / request-changes
- P0 findings
- P1 findings
- P2 suggestions
- final recommendation

## Goal-Level Decision Audit

Decision: request external review before closing the RayDB M28 bounded evidence
goal.

1. Was I foolish?

   No. External review is required before closure and is the correct guard
   against repeating unsupported release claims.

2. If yes, what actions made the decision foolish?

   The foolish action would be to treat the 158.010x hot-query ratio as a
   release-ready or end-to-end RayDB speedup claim before review.

3. Was there another path?

   Yes. I could continue to the next benchmark app immediately, but that would
   leave this evidence unclosed and ambiguous.

4. Can I now try a different path that actually solves the problem?

   Yes. The current path asks the external reviewer to attack the timing
   boundary, app-generic status, overlarge-run handling, and claim wording
   before any bounded closure.
