# Goal5017 - Workspace Query Device-Column Lifecycle

## Purpose

Goal5017 closes an API gap exposed by the RayJoin prepared-base query-many probes:
the public `PlanarMapWorkspace2DOptixQuery` could run point-location in host-row
form, but application code still had to reach through internal prepared locator
handles to get device-resident `face_id` columns.

This goal makes the device-column route a public generic workspace-query
lifecycle, not a RayJoin overlay shortcut.

## Code Changes

Touched files:

- `src/rtdsl/optix_runtime.py`
- `tests/goal4913_planar_map_workspace_api_test.py`

New public query-lifecycle methods on `PlanarMapWorkspace2DOptixQuery`:

- `PlanarMapWorkspace2DOptix.prepare_base_points_for_queries()`
- `prepare_query_points_in_base()`
- `prepare_base_points_in_query()`
- `query_points_in_base_face_id_device_columns(prepared_points)`
- `base_points_in_query_face_id_device_columns(prepared_points)`

These methods expose existing public directed point-location device-column
capabilities through the public workspace query object. They do not add overlay
semantics, output-chain logic, author-formatting logic, or RayJoin-specific core
primitives.

## Validation

Local tests:

```text
$env:PYTHONPATH='src'; py -3 -m unittest tests.goal4913_planar_map_workspace_api_test tests.goal5016_point_location_prepare_timing_test
```

Result:

```text
Ran 9 tests in 0.019s
OK
```

POD tests:

```text
cd /root/rtdl_goal4988
. .venv/bin/activate
export PYTHONPATH=src
python -m unittest tests.goal4913_planar_map_workspace_api_test tests.goal5016_point_location_prepare_timing_test
```

Result:

```text
Ran 9 tests in 0.005s
OK
```

POD native smoke:

- Input: top4 County x Zipcode CDBs.
- Operation: create public workspace, prepare a query, call
  `prepare_query_points_in_base()`, then call
  `query_points_in_base_face_id_device_columns(...)`.
- Artifact:
  `history/internal_docs/goal5017_workspace_query_device_columns_smoke_2026-07-05.json`

Key observed metadata:

```json
{
  "device_resident": true,
  "app_specific_schema_allowed": false,
  "engine_boundary": "generic_directed_point_location_id_column",
  "native_symbol": "rtdl_optix_prepared_directed_segment_point_location_2d_device_face_id_columns",
  "row_count": 1706639,
  "traversal_seconds": 0.004413117
}
```

Second POD smoke:

- Operation: call `PlanarMapWorkspace2DOptix.prepare_base_points_for_queries()`
  once, then consume that prepared base-point batch through a query-specific
  locator with `base_points_in_query_face_id_device_columns(...)`.
- This mirrors the Goal5012 shared right-vertex query-point reuse pattern, but
  exposes it through public workspace/query methods rather than a bootstrap
  locator handle.

Key observed metadata:

```json
{
  "device_resident": true,
  "app_specific_schema_allowed": false,
  "row_count": 9993104,
  "traversal_seconds": 0.01524035,
  "query_specific_locator_prepare_still_paid": true,
  "prepare_point_location_base_in_query_sec": 0.4303861930966377
}
```

## What This Proves

- A user of the public workspace/query API can obtain device-resident
  point-location face-id columns without importing or reaching into
  `rtdsl.rayjoin_overlay`.
- A user of the public workspace API can prepare base-map query points once and
  reuse that prepared point batch through same-domain query-specific locators.
- The route is generic directed point-location output: `field_name = face_id`,
  `engine_boundary = generic_directed_point_location_id_column`.
- The query object preserves the correct claim boundary:
  `public_generic_rtdl_workspace_query = true`,
  `application_continuation_inside_rtdl_core = false`,
  `raw_optix_callback_exposed = false`.

## What This Does Not Prove

- No 10x speedup claim.
- No author-performance parity claim.
- No full zero-copy claim.
- No claim that query-specific point-location locator prepare cost is solved.
- The POD shared-base-points smoke still reports
  `prepare_point_location_base_in_query_sec = 0.4303861930966377`; that cost is
  explicitly still paid.
- No claim that prepared-base query-many reaches the target `~0.42s`.

## Interpretation

This is an architecture/productization fix. It turns the already-measured
prepared-base query-many pattern from a probe that had to manipulate internal
locator handles into a cleaner public workspace-query lifecycle.

The remaining performance problem is unchanged:

- proven prepared-base same-domain query-many is still about `~1.22s/query`;
- the biggest remaining costs are query-specific locator preparation and
  downstream app continuation work;
- reaching `~0.42s` still requires further reductions beyond this API cleanup.

## Exit Label

`completed_workspace_query_device_column_lifecycle_public_api`
