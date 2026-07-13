# Goal5015 - Planar-Map Workspace Query Lifecycle

Date: 2026-07-05

## Purpose

Goal5015 starts the v2.14.4 performance direction after v2.14.3 stabilized at:

```text
warm-process fresh fast-pack:        ~4.22s
prepared same-domain distinct query: ~1.22s/query
left locator prepare floor:          ~0.46-0.47s/query
```

The next architectural problem is:

```text
RTDL prepared workspace is not strong enough to make query-specific geometry
preparation a reusable product concept.
```

The first step is not a RayJoin app shortcut.  It is to formalize the generic
prepared-base / distinct-query lifecycle in RTDL itself.

## Implementation

Changed:

```text
src/rtdsl/optix_runtime.py
src/rtdsl/__init__.py
tests/goal4913_planar_map_workspace_api_test.py
```

New public lifecycle object:

```python
PlanarMapWorkspace2DOptixQuery
```

New method:

```python
PlanarMapWorkspace2DOptix.prepare_query(...)
```

Conceptual usage:

```python
with prepare_planar_map_workspace_2d_optix(base_left, base_right) as workspace:
    with workspace.prepare_query(query_left) as query:
        pairs = query.run_lsi_pair_id_rows()
        query_faces = query.run_query_points_in_base()
        base_faces = query.run_base_points_in_query()
```

This gives RTDL a generic lifecycle shape:

```text
base workspace -> distinct query workspace -> LSI / point-location operations
```

The RayJoin app is not the owner of this lifecycle anymore.

## Claim Boundary

Authorized:

- RTDL now has a generic query-side workspace lifecycle object.
- The object exposes query setup timings through metadata.
- The object explicitly records that query-specific locator prepare is still
  paid.
- The object does not import `rayjoin_overlay`.
- The object does not expose raw OptiX callbacks.
- The object does not add a RayJoin overlay kernel to RTDL core.

Not authorized:

- Claiming the `~0.46-0.47s/query` locator floor is reduced.
- Claiming 10x.
- Claiming full device-resident or zero-copy execution.
- Claiming author-performance parity.

## Why This Matters

Before this goal, the v2.14.3 query-many work existed mostly as app/probe
protocol.  That made the next optimization ambiguous: should it live in the app,
in the native point-location primitive, or in a reusable RTDL workspace?

Goal5015 fixes the ownership boundary:

```text
future locator-residency optimization belongs under the generic workspace query
lifecycle, not inside a RayJoin-specific app path.
```

## Validation

Command:

```text
$env:PYTHONPATH='src'; py -3 -m unittest tests.goal4913_planar_map_workspace_api_test
```

Result:

```text
Ran 5 tests in 0.017s
OK
```

## Next Step

Goal5016 should target the actual floor:

```text
resident_or_reusable_directed_point_location_locator_construction
```

It should start with a native/source phase audit of locator construction and
must answer:

1. How much of `~0.46s/query` is host packing vs native structure build?
2. Is there an OptiX refit/update route for same topology / same domain?
3. Can the route remain generic across a non-RayJoin point-location workload?
4. If no, should v2.14.4 accept `~1.2s/query` as the current non-fusion floor?

Recommended exit label:

```text
completed_goal5015_generic_workspace_query_lifecycle_inserted
```
