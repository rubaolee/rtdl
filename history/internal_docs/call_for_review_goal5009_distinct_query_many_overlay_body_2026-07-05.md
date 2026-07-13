# Call For Review: Goal5009 Distinct-Query Full Binary Overlay Body

Please review:

```text
history/internal_docs/goal5009_distinct_query_many_overlay_body_result_2026-07-05.md
history/internal_docs/goal5009_distinct_query_many_overlay_probe.py
history/internal_docs/goal5009_distinct_query_many_overlay_artifacts_2026-07-05/rtdl_goal5009_distinct_query_many_overlay.json
```

## Requested Verdict Label

```text
approve_goal5009_overlay_query_many_measured_10x_not_reached_target_point_location_next
```

## Review Questions

1. Does Goal5009 correctly extend Goal5008 from LSI-only to the full
   writer-free binary overlay body?
2. Does the probe correctly avoid same-input replay by using three distinct
   same-domain query variants?
3. Is it correct that the full body must include per-query preparation costs,
   especially:

```text
prepare_lsi_query
prepare_left_point_location
```

4. Does the evidence support the stable full overlay body result:

```text
query 2: 1.470s
query 3: 1.491s
stable body: ~1.48s/query
```

5. Is it correct to treat query 1 (`5.638s`) as first full pipeline warmup, not
   the stable query-many body?
6. Does the result correctly preserve the regime boundary:

```text
prepared base / same scale-domain / distinct query batches
```

7. Is it correct that Goal5009 does **not** authorize the 10x claim, because
   current full overlay body is `~1.48s`, not `~0.42s`?
8. Does the breakdown correctly show that LSI is no longer the main blocker in
   this regime, and that point-location / downstream are now dominant?
9. Is the proposed next target correct: generic point-location query-many design
   before any further LSI work?
10. Should Goal5009 close with:

```text
completed_distinct_query_many_overlay_body_measured__10x_not_reached__next_target_point_location_and_downstream
```
