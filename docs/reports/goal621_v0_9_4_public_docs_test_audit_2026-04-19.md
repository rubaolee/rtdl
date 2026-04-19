# Goal621: v0.9.4 Public Docs, Test, And Audit Gate

Date: 2026-04-19

## Verdict

Status: ACCEPTED with Codex + Gemini 2.5 Flash consensus.

Goal621 refreshes the public v0.9.4 release-target documentation after the
Apple Metal DB/graph work through Goal620 and reruns the local test/doc/audit
gates.

## Public Documentation Changes

Updated public-facing docs to remove stale "current v0.9.2" Apple wording and
describe the current `v0.9.4` target consistently:

- `README.md`
- `docs/README.md`
- `docs/rtdl_feature_guide.md`
- `docs/current_architecture.md`
- `docs/backend_maturity.md`
- `docs/capability_boundaries.md`
- `docs/release_facing_examples.md`
- `docs/tutorials/README.md`
- `examples/README.md`

Added a v0.9.4 release-target package:

- `docs/release_reports/v0_9_4/README.md`
- `docs/release_reports/v0_9_4/support_matrix.md`

The new support matrix records all 18 current `run_apple_rt` predicates and
their explicit Apple modes:

- `native_mps_rt`
- `native_mps_rt_2d_3d`
- `native_metal_compute`
- `native_metal_filter_cpu_aggregate`

It also records the CPU-side refinement, aggregation, uniqueness, or ordering
that remains part of each native/native-assisted path.

## Honesty Boundary

The refreshed docs keep these boundaries:

- Current released version remains `v0.9.1` until explicit release action.
- `v0.9.2` and `v0.9.3` are internal evidence lines absorbed into `v0.9.4`.
- Apple RT is real bounded Apple execution, but not a broad speedup claim.
- Embree remains the mature performance baseline.
- Apple Metal compute DB/graph paths are not described as MPS ray traversal.
- CPU exact refinement/materialization remains disclosed where used.

## Tests And Audits

Commands run locally on macOS:

```text
make build-apple-rt
PYTHONPATH=src:. python3 -m unittest tests.goal620_apple_rt_graph_triangle_match_test -v
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal582_apple_rt_full_surface_dispatch_test tests.goal595_apple_rt_perf_harness_test tests.goal596_apple_rt_prepared_closest_hit_test tests.goal597_apple_rt_masked_hitcount_test tests.goal598_apple_rt_masked_segment_intersection_test tests.goal603_apple_rt_native_contract_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal607_apple_rt_point_in_polygon_positive_native_test tests.goal608_apple_rt_segment_polygon_native_test tests.goal609_apple_rt_point_nearest_segment_native_test tests.goal610_apple_rt_polygon_pair_native_test tests.goal611_apple_rt_overlay_compose_native_test tests.goal616_apple_rt_compute_skeleton_test tests.goal617_apple_rt_db_conjunctive_scan_test tests.goal618_apple_rt_db_grouped_aggregation_test tests.goal619_apple_rt_graph_bfs_test tests.goal620_apple_rt_graph_triangle_match_test -v
PYTHONPATH=src:. python3 -m unittest tests.goal511_feature_guide_v08_refresh_test -v
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*test.py' -v
PYTHONPATH=src:. python3 scripts/goal497_public_entry_smoke_check.py
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
PYTHONPATH=src:. python3 -m unittest tests.goal512_public_doc_smoke_audit_test tests.goal531_v0_8_release_candidate_public_links_test tests.goal511_feature_guide_v08_refresh_test -v
git diff --check
```

Observed results:

- Goal620 dedicated suite: 6 tests OK.
- Apple focused regression suite: 79 tests OK.
- Full local discovery after doc/test refresh: 1178 tests OK, 171 skipped.
- Public entry smoke check: `valid: true`.
- Public command truth audit: `valid: true`, 14 public docs, 244 commands.
- Public doc smoke/link tests: 9 tests OK.
- `git diff --check`: no whitespace errors.

One first full-discovery run failed because
`tests/goal511_feature_guide_v08_refresh_test.py` still expected the older
`v0.9.2` phrase. The test was corrected to require the new `v0.9.4` target
wording, and the rerun passed.

## Codex Assessment

The public docs now describe the current v0.9.4 target consistently, and local
tests/audits pass. This is not a release action by itself; release still
requires explicit user authorization.

## External Review

Gemini 2.5 Flash reviewed the Goal621 report and changed public docs/release
target package and returned `ACCEPT` in:

- `docs/reports/goal621_external_review_2026-04-19.md`
