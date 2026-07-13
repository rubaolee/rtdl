# Call For Review: Goal5004 Updated v2.14.3 Performance Matrix

Please review:

```text
history/internal_docs/goal5004_updated_v2_14_3_performance_matrix_2026-07-05.md
history/internal_docs/goal5004_updated_performance_matrix_artifacts_2026-07-05/fresh_after_accounting_fix_top4.json
history/internal_docs/goal5002_lsi_compile_prewarm_artifacts_2026-07-05/tiny_lsi_prewarm_then_fresh.json
history/internal_docs/goal5003_lsi_workspace_floor_artifacts_2026-07-05/lsi_workspace_floor_probe_top4.json
history/internal_docs/goal4999_device_midpoint_query_points_artifacts_2026-07-04/device_query_midpoint_top4_repeat5.json
```

Relevant code/test changes:

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
tests/goal4999_device_query_point_location_handoff_test.py
```

## Requested Verdict Label

```text
approve_goal5004_corrected_v2_14_3_matrix_fresh_headline_5s
```

or:

```text
revise_goal5004_before_docs_release_boundary
```

## Review Questions

1. Is the `writer_free_hot_sec` accounting fix correct?

   Specifically, should the device-resident carrier route include:

   ```text
   midpoint_points_map0_device_query_points_sec
   midpoint_points_map1_device_query_points_sec
   ```

   rather than the old host-columnar midpoint keys?

2. Does the new POD artifact support the corrected fresh top4 writer-free
   binary route number?

   ```text
   writer_free_hot_sec = 5.003915s
   LSI = 2.628660s
   downstream = 2.375255s
   rows = 428322
   descriptor pairs = 15014
   ```

3. Does Goal5004 correctly separate the three regimes?

   ```text
   fresh one-shot top4:           5.003915s
   generic compile-prewarm diag:  4.584897s
   same prepared-query replay:    0.332861s
   ```

4. Is it correct to keep the fresh LSI workspace cost in the fresh headline
   after Goal5003 showed scale-domain dependency?

5. Does the report avoid author-performance parity, true query-many, top4
   author ratio, pure replay headline, and full-zero-copy claims?

6. Are the local regression checks sufficient for this accounting/reporting
   change?

   ```text
   py -3 -m unittest tests.goal4999_device_query_point_location_handoff_test tests.goal4990_binary_repeat_protocol_test
   py -3 -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
   ```

7. Is the recommended next goal correct?

   ```text
   Goal5005: v2.14.3 Documentation And Release Boundary Update After Corrected Matrix
   ```

## Non-Authorization Boundary

This review should not approve:

- using `0.33s` as a fresh or true query-many headline;
- top4 author-performance ratio without top4 AuthorOfficial timing;
- hiding LSI workspace from fresh timing;
- author parity claims;
- full zero-copy claims;
- RayJoin-specific RTDL core optimization.
