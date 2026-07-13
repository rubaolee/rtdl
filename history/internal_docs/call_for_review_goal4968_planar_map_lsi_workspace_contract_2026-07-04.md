# Call For Review: Goal4968 Planar-Map LSI Workspace Contract

Please review:

`history/internal_docs/goal4968_planar_map_lsi_workspace_contract_2026-07-04.md`

## Requested Verdict

One of:

- `approve_goal4968_generic_workspace_contract_and_prepared_hot_boundary`
- `approve_with_required_amendments`
- `block_until_goal4968_proves_generic_boundary_or_measurement`

## Review Questions

1. Is `PreparedOptixPlanarMapLsi2DQuery.prepare_workspace()` a generic
   planar-map LSI workspace contract rather than a RayJoin app shortcut?
2. Does the metadata boundary correctly avoid RayJoin overlay/application
   semantics?
3. Does the RayJoin paper app use the new workspace API only as an app-level
   benchmark consumer?
4. Do the POD results support the prepared-hot boundary:
   `prepare_session ~0.277s`, `prepare_workspace ~0.533s`,
   `hot pair-id rows ~0.0015s`, `writer_free_hot ~0.092s`?
5. Does the report correctly forbid claiming one-shot fresh overlay is
   `0.092s`?
6. Are the revised next goals correct: downstream prepared-hot breakdown,
   one-shot workspace cost reduction, and larger representative data?
