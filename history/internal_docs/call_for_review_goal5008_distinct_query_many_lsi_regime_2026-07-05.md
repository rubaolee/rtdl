# Call For Review: Goal5008 Distinct-Query Prepared-Base LSI Regime

Please review:

```text
history/internal_docs/goal5008_distinct_query_many_lsi_regime_result_2026-07-05.md
history/internal_docs/goal5008_distinct_query_many_lsi_probe.py
history/internal_docs/goal5008_distinct_query_many_lsi_artifacts_2026-07-05/rtdl_goal5008_distinct_query_many_lsi.json
```

## Requested Verdict Label

```text
approve_goal5008_lsi_distinct_same_domain_query_many_regime_demonstrated
```

## Review Questions

1. Does the probe avoid same-input prepared-query replay and instead create new
   query handles with distinct query inputs?
2. Is it acceptable that the distinct same-domain query batches use the same
   full top4 geometry domain with shifted IDs and tiny in-domain perturbations,
   rather than separate CDB files, for the purpose of testing LSI workspace reuse?
3. Does the evidence show the prepared-base / same-domain / distinct-query LSI
   regime exists?

```text
distinct_same_domain_query_1: 0.1172s
distinct_same_domain_query_2: 0.1178s
distinct_same_domain_query_3: 0.1176s
```

4. Does the grouped-range timing support the interpretation that the expensive
   right-side workspace is reused across same-domain distinct queries?

```text
grouped_range_ensure ~= 0.000001s for all three distinct same-domain queries
```

5. Does the far-domain query correctly preserve the Goal5003 boundary that
   changing scale domain rebuilds the workspace?

```text
distinct_far_domain_query: 1.484s
scaled_cache_ensure: 0.615s
grouped_range_ensure: 0.867s
```

6. Is it correct to authorize `query-many` wording for **LSI only**, with the
   qualifier `prepared base / same scale-domain / distinct query batches`?
7. Is it correct that this still does **not** authorize a full overlay 10x claim,
   because reprojection/sort/PIP/midpoint/carrier/downstream were not measured
   for the distinct query batches?
8. Is Goal5009 correctly proposed as the next step: measure the full writer-free
   binary overlay body on the same distinct same-domain query batches?
9. Should Goal5008 close with:

```text
completed_lsi_distinct_same_domain_query_many_regime_demonstrated__overlay_query_many_still_unproven
```
