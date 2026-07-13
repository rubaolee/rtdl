# Call For Review: Goal5010-5012 Point-Location Query-Many

Please review:

```text
history/internal_docs/goal5010_5012_point_location_query_many_result_2026-07-05.md
history/internal_docs/goal5010_point_location_query_many_probe.py
history/internal_docs/goal5011_point_location_query_point_reuse_probe.py
history/internal_docs/goal5012_overlay_shared_point_query_probe.py
history/internal_docs/goal5010_point_location_query_many_artifacts_2026-07-05/rtdl_goal5010_point_location_query_many.json
history/internal_docs/goal5011_point_location_query_point_reuse_artifacts_2026-07-05/rtdl_goal5011_point_location_query_point_reuse.json
history/internal_docs/goal5012_overlay_shared_point_query_artifacts_2026-07-05/rtdl_goal5012_overlay_shared_point_query.json
```

## Requested Verdict Label

```text
approve_goal5010_5012_point_location_query_point_reuse_win_10x_not_reached
```

## Review Questions

1. Does Goal5010 correctly identify point-location preparation, not traversal,
   as the main point-location cost in the distinct-query full overlay body?
2. Does Goal5010 show the heavy direction is `right vertices in left map`, where
   the left/query map becomes the per-query point-location base?
3. Is it correct that `run_right_vertices_in_left` itself is fast (`~0.025s`),
   while `prepare_left_locator` and `prepare_right_query_points` dominate?
4. Does Goal5011 provide sufficient evidence that prepared right query points
   can be reused across same-domain left locators for this workload?
   - same positive counts;
   - same face hashes;
   - same samples;
   - same-domain locators.
5. Is this reuse generic point-location buffer reuse rather than a RayJoin
   overlay-specific shortcut?
6. Does Goal5012 correctly connect the reuse back to the full writer-free binary
   overlay body?
7. Does the evidence support the new stable full overlay query-many body:

```text
~1.22s/query
```

8. Is it correct that this is an improvement over Goal5009 (`~1.48s/query`) but
   still not the 10x target (`~0.42s/query`)?
9. Is the remaining main target correctly identified as generic left
   point-location locator preparation (`~0.445s/query`)?
10. Should the next goal be a decision/design gate for generic fixed-domain /
    resident point-location workspace, rather than more LSI work or
    RayJoin-specific core code?
11. Should Goal5010-5012 close with:

```text
completed_point_location_query_point_reuse_win__full_overlay_query_many_now_about_1_22s__10x_still_not_reached
```
