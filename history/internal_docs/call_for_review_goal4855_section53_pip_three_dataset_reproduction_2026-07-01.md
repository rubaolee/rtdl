# Call For Review - Goal4855 RayJoin Section 5.3 PIP Three-Dataset Reproduction

Please review:

`history/internal_docs/goal4855_section53_pip_three_dataset_reproduction_2026-07-01.md`

Raw artifacts:

`history/internal_docs/goal4855_section53_pip_final_stream/`

Runner:

`history/internal_docs/goal4855_rayjoin_section53_pip_public_front_door.py`

Requested verdict label:

`approve_goal4855_close_section53_three_dataset_reproduction_no_performance_win_claim`

## Review Questions

1. Does the report correctly scope the work to RayJoin paper Section 5.3 PIP,
   not Section 5.7 polygon overlay?

2. Does the runner avoid the bundled RayJoin overlay helper and use the directed
   point-location primitive as the RTDL execution route?

3. Is the user-side streaming CDB adapter an acceptable internal reproduction
   mechanism, given that it records the internal packed-layout reach as product
   debt rather than hiding it?

4. Are the three datasets enough to close the user-authorized bounded Section
   5.3 reproduction line for now: County x Zipcode, Block x Water, and Australia
   Lakes x Parks representative?

5. Is the performance interpretation honest, especially the statement that RTDL
   does not beat AuthorPatch hot Query in this run?

6. Does the report correctly separate cold CDB input/serialization time from
   hot query/traversal time?

7. Is it correct not to claim byte-level PIP output equivalence, since the
   captured AuthorPatch `query_exec -query=pip` path does not emit per-point
   classifications or an answer file?

8. Should Goal4855 close with label
   `completed_section53_three_dataset_workload_reproduction__no_performance_win_claim`?

## Non-Authorization

This review request does not authorize:

- Section 5.7 overlay claims
- all-eight-pair Section 5.3 claims
- broad RTDL/RayJoin performance claims
- public release wording changes
- hidden RayJoin-specific RTDL core changes
- treating the streaming packed-layout adapter as a polished public API
