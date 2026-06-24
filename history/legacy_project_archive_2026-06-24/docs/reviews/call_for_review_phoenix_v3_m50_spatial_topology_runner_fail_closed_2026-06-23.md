# Call For Review: Phoenix V3 M50 Spatial Topology-Stream Runner Fail-Closed Gate

Date: 2026-06-23

Please critically review whether M50 correctly hardens the Spatial/RayJoin
topology-stream M3 runner after M49.

Primary report:

- `docs/reports/phoenix_v3_m50_spatial_topology_stream_runner_fail_closed_2026-06-23.md`

Required supporting files:

- `scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py`
- `tests/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner_test.py`
- `docs/reports/phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md`
- `docs/reviews/phoenix_v3_claude_review_debt_register_2026-06-23.md`

Requested verdict labels:

- `accept_m50_runner_fail_closed_no_run`
- `revise_m50_before_next_work`
- `reject_m50_runner_still_runs_too_easily`

Review questions:

1. Does the runner now default to dry-run without calling the workload?
2. Is requiring both `--execute` and the M50 token sufficient for a fail-closed
   local gate?
3. Does M50 correctly align with M49's rule that Spatial/RayJoin is blocked
   except as generic topology-stream residency / full-M3 accounting work?
4. Does the dry-run packet preserve claim boundaries and avoid M7 promotion?
5. Do the tests cover both dry-run default and missing-token failure?
6. Are old/stale runner commands now safe by default?
7. Is any paid POD, all-app, release, or public speedup action accidentally
   authorized?
8. Is the goal-level four-question audit present and adequate?

Non-authorization to preserve:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no focused POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
