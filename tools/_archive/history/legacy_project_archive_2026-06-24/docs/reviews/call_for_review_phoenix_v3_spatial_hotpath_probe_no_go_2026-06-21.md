# Call For Review: Phoenix V3 Spatial Hotpath Probe No-Go

Please critically review the Phoenix V3 Spatial RayJoin hotpath no-go packet.

## Files To Read

- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_hotpath_probe_no_go_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_hotpath_probe_no_go_2026-06-21.md`
- `docs/rebuild/v3/evidence/phoenix_v3_spatial_hotpath_probe_20260621/relation_status_y_then_x_sample2.json`
- `docs/rebuild/v3/evidence/phoenix_v3_spatial_hotpath_probe_20260621/device_filtered_prepared_points_validated_y_then_x_sample2.log`
- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.json`
- `scripts/v3_phoenix_spatial_rayjoin_hotpath_probe_no_go.py`
- `tests/v3_phoenix_spatial_rayjoin_hotpath_probe_no_go_test.py`
- `scripts/run_test_matrix.py`

## Context

Phoenix V3 is blocked from release. The release-surface gate still reports 7/9
capability-family coverage, with missing `aggregate_frontier` and
`point_location_topology_stream`. Spatial RayJoin is the current
`point_location_topology_stream` gap.

This probe used the verified POD:

- host: `213.173.108.14:11592`
- repo: `/root/rtdl_v3_rebuild_20260620/current`
- GPU: `NVIDIA RTX 4000 Ada Generation, 550.127.05`
- dataset: `data/rayjoin_public_cdb/br_county.cdb`
- protocol: query repeat 50, warmup 5, sample repeat 2
- exact authority count: 47,262

Fresh results:

- Best legal exact RTDL route:
  `relation_status_corrected_executor_validated`, point order `y_then_x`,
  47,262 rows, hot query `5.406518 ms`.
- Same-dataset RayJoin author Query timer from the existing author-basis packet:
  `1.865660 ms`.
- Therefore RayJoin author is still `2.898x` faster than the best legal RTDL
  hotpath in this probe.
- `device_filtered_prepared_points_validated` is rejected because it reports
  `47,570` instead of exact `47,262`.
- `exact_prepared_points_executor` is correct but much slower at `23.262223 ms`.

## Questions For Claude

1. Is the no-go conclusion sound?
2. Does this packet correctly keep `point_location_topology_stream` missing from
   Phoenix V3 M7 release coverage?
3. Are any public/user-facing claims still unsafe or under-fenced?
4. Is the evidence sufficient to stop repeating this Spatial route for V3 unless
   a real generic traversal optimization is designed?
5. What concrete next generic-engine work should Codex attempt after this, if
   the goal remains a high-performance V3 rather than app-specific tuning?

Please provide a verdict using one of:

- `approve-no-go`
- `approve-with-amendments`
- `block-no-go`

Lead with P0/P1 issues if any, then give actionable recommendations.
