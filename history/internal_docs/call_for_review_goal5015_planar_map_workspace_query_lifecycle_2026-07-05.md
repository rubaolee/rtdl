# Call For Review - Goal5015 Planar-Map Workspace Query Lifecycle

Date: 2026-07-05

Please review:

```text
history/internal_docs/goal5015_planar_map_workspace_query_lifecycle_result_2026-07-05.md
```

Code touched:

```text
src/rtdsl/optix_runtime.py
src/rtdsl/__init__.py
tests/goal4913_planar_map_workspace_api_test.py
```

## Review Questions

1. Does `PlanarMapWorkspace2DOptix.prepare_query(...)` correctly formalize the
   prepared-base / distinct-query lifecycle as a generic RTDL workspace concept?
2. Does `PlanarMapWorkspace2DOptixQuery` keep RayJoin app semantics out of RTDL
   core?
3. Does the metadata honestly disclose that query-specific locator prepare is
   still paid?
4. Is it correct that Goal5015 is an architectural ownership step, not a
   performance win?
5. Do the tests cover export, lifecycle, close behavior, generic claim boundary,
   and query-specific locator disclosure?
6. Should the next goal target the real floor:
   `resident_or_reusable_directed_point_location_locator_construction`?

Requested verdict label:

```text
approve_goal5015_generic_workspace_query_lifecycle_inserted
```
