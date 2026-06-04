# Handoff: Review RayJoin Current-Best And Negative Probe Chain

Please perform a read-only review and write the result to:

`docs/reviews/goal3305_claude_review_goal3303_3304_rayjoin_current_best_and_negative_probes_2026-06-04.md`

## Current Commit

`ed62ddc7`

## Context

The RayJoin same-slice work has just closed three tuning directions and
refreshed the current-best RTDL route:

- Goal3300: boundary-event rows plus grouped count are app-agnostic but a bad
  PIP performance route.
- Goal3303: prepared closed-shape edge layout is slower, and `crossing_only`
  boundary mode fails correctness (`129 != 1430`).
- Goal3304: latest current-best route is
  `device_filtered_validated + inclusive + z_point + scalar count pipeline`.

The key engineering question is whether the next optimization target should be
generic scalar-count launch/packing/residency overhead, rather than another
semantic shortcut or materialized event stream.

## Files To Inspect

- `docs/reports/goal3300_rayjoin_boundary_event_count_route_2026-06-04.md`
- `docs/reports/goal3300_boundary_event_same_slice_pod_2026-06-04.json`
- `docs/reports/goal3303_rayjoin_scalar_count_negative_tuning_probes_2026-06-04.md`
- `docs/reports/goal3303_prepared_edge_scalar_count_probe_pod_2026-06-04.json`
- `docs/reports/goal3304_current_best_rayjoin_same_slice_2026-06-04.md`
- `docs/reports/goal3304_current_best_rayjoin_same_slice_pod_2026-06-04.json`
- `tests/goal3300_rayjoin_boundary_event_count_route_test.py`
- `tests/goal3303_rayjoin_scalar_count_negative_tuning_probes_test.py`
- `tests/goal3304_current_best_rayjoin_same_slice_test.py`
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`

## Questions

1. Are the negative conclusions for boundary-event materialization,
   prepared-edge layout, and crossing-only boundary mode supported by
   artifacts/tests?
2. Does Goal3304 honestly identify the current-best RTDL route without
   overclaiming a RayJoin win or paper reproduction?
3. Do all claim-boundary flags remain blocked?
4. Is the next engineering target sound: app-agnostic scalar-count
   launch/packing/residency overhead, while preserving inclusive boundary
   semantics?
5. Are there any inconsistencies in counts, timing units, route names, or
   visible contracts that should be fixed before the next pod run?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Lead with findings by severity, then summarize.
