# Call For Review: Goal4954-D Non-RayJoin Grouped Carrier Proof And Reprojection/Sort Plan

Date: 2026-07-04

Review target:

- `history/internal_docs/goal4954d_non_rayjoin_grouped_carrier_proof_and_reprojection_sort_plan_2026-07-04.md`
- `history/internal_docs/goal4954d_non_rayjoin_grouped_carrier_proof.py`
- `history/internal_docs/goal4954d_non_rayjoin_grouped_carrier_proof.json`
- `history/internal_docs/goal4954c_grouped_carrier_prototype_results_2026-07-04.md`

Requested verdict:

`approve_goal4954d_non_rayjoin_grouped_carrier_proven`

or:

`block_goal4954d_until_redone`

## Review Questions

1. Does the non-RayJoin proof actually avoid RayJoin, CDB, AuthorOfficial, and
   paper text dependencies?

2. Does the proof establish that the grouped carrier is a generic spatial/dataflow
   representation candidate?

3. Does the report correctly avoid claiming that the grouped carrier has already
   been promoted into RTDL core?

4. Is the reprojection/sort discussion honest about exact rational correctness
   versus numeric binary-operator performance?

5. Is Option B reasonable:
   - paper sink retains exact route for correctness;
   - binary operator may use numeric columnar route for database-style consumers?

6. Does the report correctly preserve the owner invariant:
   RTDL generic, RayJoin app?

7. Should Goal4954-D close with:

   `non_rayjoin_grouped_carrier_proven__reprojection_sort_plan_ready`

## Non-Authorization Boundary

Approval does not authorize:

- RTDL core promotion yet;
- public API exposure;
- Layer 4 fusion;
- raw callbacks;
- weakening the paper-output correctness anchor.
