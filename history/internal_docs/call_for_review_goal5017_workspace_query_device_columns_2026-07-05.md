# Call For Review - Goal5017 Workspace Query Device-Column Lifecycle

Please review:

- `history/internal_docs/goal5017_workspace_query_device_columns_result_2026-07-05.md`
- `history/internal_docs/goal5017_workspace_query_device_columns_smoke_2026-07-05.json`
- `src/rtdsl/optix_runtime.py`
- `tests/goal4913_planar_map_workspace_api_test.py`

## Requested Verdict

`approve_goal5017_workspace_query_device_columns_public_lifecycle`

## Review Questions

1. Does Goal5017 correctly expose device-column point-location through the
   public `PlanarMapWorkspace2DOptixQuery` lifecycle rather than through a
   RayJoin app/private helper?

2. Are the new methods generic directed point-location / workspace-query
   capabilities, not hidden overlay/output-chain semantics?

3. Does the POD smoke prove the new public route can produce a device-resident
   `face_id` column on the top4 workload, with
   `app_specific_schema_allowed = false`?

4. Does the second POD smoke prove the public workspace can prepare base-map
   points once and consume them through a same-domain query-specific locator,
   while still disclosing that query-specific locator preparation remains paid?

5. Do the tests sufficiently verify that the workspace query routes through the
   public locator methods for prepared query points and face-id device columns?

6. Is the claim boundary honest: no 10x speedup claim, no author-parity claim,
   no full zero-copy claim, and no assertion that query-specific locator prepare
   cost is solved?

7. Should this goal close as an API/productization step, with performance work
   continuing on query-specific locator preparation and downstream continuation
   cost?
