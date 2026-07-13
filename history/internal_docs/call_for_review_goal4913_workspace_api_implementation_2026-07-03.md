# Call For Review — Goal4913 Planar-Map Workspace API Implementation

Date: 2026-07-03

Please review:

```text
history/internal_docs/goal4913_planar_map_workspace_api_implementation_2026-07-03.md
```

Implementation files:

```text
src/rtdsl/optix_runtime.py
src/rtdsl/__init__.py
tests/goal4913_planar_map_workspace_api_test.py
```

## Requested Verdict Labels

Choose one:

- `approve_goal4913_workspace_api_implemented`
- `approve_with_required_amendments`
- `block_goal4913_as_rayjoin_specific`
- `block_goal4913_as_unverified_or_too_broad`

## Review Questions

1. Does the implementation match the Goal4912-approved in-process workspace design?
2. Is the new API generic planar-map infrastructure rather than a hidden RayJoin route?
3. Does the implementation avoid importing or depending on `rtdsl.rayjoin_overlay`?
4. Does it correctly reuse public LSI and point-location prepared handles?
5. Are close/context-manager semantics sufficient for this first implementation?
6. Do the tests adequately cover export, lifecycle, env restoration, and boundary claims?
7. Is the report honest that this is productization of an already measured prepared-hot route, not a new performance claim?
8. Should the next goal be a POD smoke rewiring the Australia representative harness to use the workspace API and verifying byte equality plus no hot-body regression?

## Non-Authorization Boundary

Approval must not authorize:

- raw OptiX callback exposure;
- RayJoin-specific hidden kernels;
- cross-process OptiX GAS serialization;
- new broad performance claims;
- public release wording changes;
- V3/V4 resurrection.
