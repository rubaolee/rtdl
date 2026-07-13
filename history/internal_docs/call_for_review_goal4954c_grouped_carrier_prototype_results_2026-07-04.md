# Call For Review: Goal4954-C Grouped Carrier Prototype Results

Date: 2026-07-04

Review target:

- `history/internal_docs/goal4954c_grouped_carrier_prototype_results_2026-07-04.md`
- `history/internal_docs/goal4954c_artifacts/grouped_carrier_summary_run1.json`
- `history/internal_docs/goal4954c_artifacts/grouped_carrier_summary_run2.json`
- `history/internal_docs/goal4954c_artifacts/grouped_carrier_summary_run3.json`
- `history/internal_docs/goal4954c_grouped_carrier_measure.py`
- `history/internal_docs/goal4954b_writer_free_binary_baseline_measurement_2026-07-04.md`

Requested verdict:

`approve_goal4954c_grouped_carrier_win_continue`

or:

`block_goal4954c_results_until_redone`

## Review Questions

1. Did Goal4954-C keep RTDL core/runtime unchanged?

2. Is the grouped carrier representation generic enough as an app-owned
   prototype?

3. Are the 3-run measurements valid and comparable to Goal4954-B?

4. Does the evidence support the claimed improvement:
   - writer-free hot path `5.309s -> 3.835s`;
   - construction+consumer `2.437s -> 1.022s`;
   - overall `1.384x` hot-path speedup?

5. Does the report correctly avoid overclaiming, given the result remains about
   `91x` slower than AuthorOfficial overlay compute?

6. Does it correctly preserve the distinction between:
   - app-owned RayJoin prototype win;
   - RTDL-core progress requiring a non-RayJoin proof?

7. Is the recommended next step reasonable:
   `Goal4954-D: non-RayJoin grouped-carrier proof + columnar reprojection/sort plan`?

8. Should Goal4954-C close with:

   `grouped_carrier_win_continue`

## Non-Authorization Boundary

Approval does not authorize:

- RTDL core promotion of this prototype;
- public API exposure;
- Layer 4 fusion;
- raw callback support;
- claim that RTDL is competitive with AuthorOfficial overlay compute.
