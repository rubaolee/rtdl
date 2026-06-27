# Phoenix V3 Grouped-Stream Runner Route Pod A/B

Date: 2026-06-22
Status: `m1_2_runner_route_pod_ab_neutral_not_release`

## Summary

This report records the focused same-RT-hardware pod A/B for the first
runner-backed Set-A probe route:

```text
PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D.run
```

The test compares:

- before: direct fixed-radius self-query adapter refresh;
- after: `run_fixed_radius_count_threshold_3d_self_query_prepared_session`
  runner-backed refresh.

This is route evidence, not release evidence and not a performance win.

## Pod And Artifacts

```text
pod: root@213.173.108.14 -p 11592
hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
remote_run: /root/rtdl_v3_rebuild_20260620/phoenix_v3_grouped_stream_runner_route_ab_20260622_162958
local_evidence: docs/rebuild/v3/evidence/phoenix_v3_grouped_stream_runner_route_ab_20260622
before: before_direct_adapter
after: after_runner_route
script: scripts/goal2467_grouped_stream_baseline_pod_runner.py
args: --point-count 32768 --point-count 65536 --repeat-count 7 --signature-mode column
```

## Result

| point_count | before tail median sec | after tail median sec | before/after speedup | signatures |
| ---: | ---: | ---: | ---: | :--- |
| 32768 | 0.0510850064 | 0.0513217002 | 0.9954x | match |
| 65536 | 0.1256630532 | 0.1256152429 | 1.0004x | match |

Geomean before/after speedup:

```text
0.9979x
```

Interpretation:

- Correctness/signature stability passed for both focused rows.
- The runner-backed route is essentially neutral on this focused route.
- The route does not produce a material speedup.
- The result is acceptable as Gap-1 route evidence, but not as a V3 performance
  breakthrough.

Native grouped-union medians were also effectively unchanged:

| point_count | before native median sec | after native median sec | after/before ratio |
| ---: | ---: | ---: | ---: |
| 32768 | 0.0329074636 | 0.0333334841 | 1.0129x |
| 65536 | 0.0897802263 | 0.0902051963 | 1.0047x |

## Route Metadata Probe

A live 4096-point metadata probe after the patch confirmed:

```text
prepared_execution_session_runner_used: true
productized_execution_path: prepared_execution_session_runner
core_flag_refresh_runtime_executed: true
runner_schema: rtdl.v3.phoenix.prepared_execution_session_runner.m1
runner_status: executed_not_release_authorization
runner_runtime_executed: true
runner_release_authorized: false
runner_public_speedup_claim_authorized: false
runner_broad_v3_faster_than_v2_claim_authorized: false
count_adapter: fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns
```

## Non-Claims

This packet does not claim:

- V3 is release-ready.
- V3 broadly beats V2.x.
- The runner-backed grouped-stream route is faster.
- Another all-app pod run is authorized.
- True zero-copy is implemented or authorized.
- Numba grouped-stream has equivalent evidence.
- V4/C ABI/embedding scope belongs in Phoenix V3.

## Next Work

This closes the first Set-A runner-route evidence item as neutral, not winning.
The next Phoenix V3 step should not be another all-app run. It should either:

1. route a second Set-A family through the runner, preferably AABB native query
   handle or grouped reduction/component continuation; or
2. identify a runner-level optimization that removes measurable overhead across
   multiple runner-backed routes.

Full all-app V2.x vs V3 remains blocked until at least two Set-A probes show
material focused evidence and Set A / Set B classification is frozen.

## Goal-Level Decision Audit

Decision: record the grouped-stream runner-route pod A/B as neutral evidence,
not release progress.

1. Was I foolish?
   No for this decision. The data is being recorded honestly: the route exists
   and executes, but it is not faster.
2. If yes, what actions made the decision foolish?
   The foolish action would be to call a 0.9979x focused result a V3
   performance improvement.
3. Was there another path that would have avoided getting stuck on this idea?
   Yes: skip pod evidence and continue architecture work. That would hide the
   overhead question instead of measuring it.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep the runner route as Gap-1 evidence, then seek material speed from
   a second Set-A route or a reusable runner-level overhead reduction, not from
   wording or all-app reruns.
