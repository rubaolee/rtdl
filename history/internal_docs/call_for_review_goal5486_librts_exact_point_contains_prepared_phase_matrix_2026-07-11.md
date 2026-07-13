# Call For Review: Goal5486 LibRTS Exact Point-Contains Prepared-Phase Matrix

Please strictly review Goal5486 and the result artifacts listed below.

## Files

```text
history/internal_docs/goal5486_librts_exact_point_contains_prepared_phase_matrix_result_2026-07-11.md
Paper-reproduction-apps/librts-paper/results/librts_goal5486_prepared_phase_batch.json
Paper-reproduction-apps/librts-paper/results/librts_goal5486_dtl_cnty_prepared_phase.json
Paper-reproduction-apps/librts-paper/results/librts_goal5486_USACensusBlockGroupBoundaries_prepared_phase.json
Paper-reproduction-apps/librts-paper/results/librts_goal5486_USADetailedWaterBodies_prepared_phase.json
Paper-reproduction-apps/librts-paper/results/librts_goal5486_parks_Europe_prepared_phase.json
Paper-reproduction-apps/librts-paper/results/librts_goal5486_lakes_bz2_prepared_phase.json
Paper-reproduction-apps/librts-paper/results/librts_goal5486_parks_bz2_prepared_phase.json
Paper-reproduction-apps/librts-paper/run_exact_point_contains_prepared_phase_batch.py
tests/goal5486_librts_prepared_phase_batch_test.py
```

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / revise
Blocking findings:
Required amendments:
Non-blocking notes:
Goal5486 claim boundary:
```

## Review Questions

1. Does the batch summary really contain six cases and six matched author/
   RTDL integer counts?
2. Do all per-case input paths remain inside the verified extraction root, and
   do the recorded SHA-256 values match the selected archive members?
3. Is the official archive identity (size and MD5) carried through without
   falsely claiming a full archive expansion?
4. Does the runner use the generic `prepare_aabb_index_2d` and prepared
   `count` API, with no LibRTS-specific RTDL primitive or native customization?
5. Are author internal Query Time, RTDL WKT load, RTDL index preparation,
   prepared query wall, and native primitive time kept as distinct fields?
6. Is the prepared-query matrix correctly described as phase evidence rather
   than an author-vs-RTDL performance ratio?
7. Does the report explicitly distinguish exact count equality from pointwise
   containment/pair-row equality, and preserve the separate Goal5467 relation
   evidence boundary?
8. Are Figure 6, full-paper reproduction, author RT-core equivalence, and
   Embree correctly left unclaimed?
9. Does the result expose the large-input WKT/MBR front-door cost without
   mislabeling it as a generic RT core cost?
10. Do the local tests verify the six-case mapping and fail-closed summary
    semantics without self-approving the external review state?

## Required Review Discipline

Please inspect the JSON and implementation directly rather than accepting the
summary prose alone. In particular, do not turn the prepared-query values into
a ratio unless the author and RTDL phase boundaries, hardware, runtime regime,
and input contract are independently shown to align. Do not promote this
matrix to Figure 6 reproduction or pointwise relation equality.
