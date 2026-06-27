# Phoenix V3 Serious Paired Benchmark Preregistration

Date: 2026-06-22
Status: `active_run_in_progress`

This document fixes the analysis rules before the active serious pod run
finishes. It exists to stop cherry-picking after results are known.

## Active Run

```text
run_id: phoenix_v3_serious_v2x_paired_20260622_074100
hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
remote_base: /root/rtdl_v3_rebuild_20260620
remote_run_dir: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_serious_v2x_paired_20260622_074100
trees: v2_14, current
```

The run compares V2.14 and current Phoenix V3 on the same pod, same data, and
same benchmark scripts:

```text
goal2626_large: --scale large --case-repeat 3
goal2636_stress: --tier stress --case-repeat 3
goal3828_full: full benchmark scale profile runability/status evidence
```

## Primary Question

Does Phoenix V3 provide broad, material performance improvement over V2.x as an
RTRDL language/runtime, not merely selected app-row wins?

## Primary Analysis Rules

1. Compare only same-suite, same-app, same-comparison-group, same-backend,
   same-case rows with a valid `primary_metric_sec` in both V2.14 and current
   Phoenix V3.
2. Compute `v3_speedup_vs_v2 = v2_primary_metric_sec / v3_primary_metric_sec`.
3. Use geometric mean for the overall speedup and per-app speedup.
4. Treat `goal3828_full` as runability/status evidence only unless a later
   audited analyzer proves its wrapper elapsed fields are comparable hot-path
   metrics.
5. Require V2.14 and current Phoenix V3 to use the same `primary_metric_source`
   for each compared row; mismatched metric sources are evidence, not
   release-consideration rows.
6. Count rows as:
   - V3 faster: speedup > 1.05x;
   - similar: 0.95x <= speedup <= 1.05x;
   - V3 slower: speedup < 0.95x.

The promoted benchmark app set is fixed before results are known:

```text
hausdorff_xhd
spatial_rayjoin
rt_dbscan
robot_collision
raydb_style
barnes_hut
librts_spatial_index
rtnn
triangle_counting
contact_manifold
```

## Release-Consideration Bar

The active run cannot authorize release by itself. It can only move V3 from
`redo_required` back into release consideration if all of these hold:

```text
all_required_suites_finished: true
missing_promoted_apps: []
primary_metric_source_mismatch_count: 0
same_metric_comparison_count: broad enough to cover all 10 promoted benchmark apps
overall_geomean_v3_speedup_vs_v2: >= 1.20x
app_geomean_speedup_vs_v2: at least 8 of 10 benchmark apps > 1.05x
app_regression_floor: no app geomean < 0.95x without a documented, accepted reason
surprising_or_negative_rows_explained: true
optimizations_are_generic_runtime_capabilities: true
release_authorized: false until external review and local gates accept the packet
```

If the overall geomean is near 1.0x, or if improvements are concentrated in a
few rows while most apps remain parity, Phoenix V3 remains `redo_required`.

## OptiX-vs-Embree Explanation Rule

For each app/comparison group with both Embree and OptiX rows:

```text
v2_optix_vs_embree = v2_embree_sec / v2_optix_sec
v3_optix_vs_embree = v3_embree_sec / v3_optix_sec
```

If both ratios are below 1.0x, the issue is not automatically a V3 regression:
the workload or route may not fit RT cores, or the OptiX route may be carrying
build/materialization/continuation overhead. If V2.14 is above 1.0x and V3 falls
below 1.0x, it is a V3 regression candidate. If both are above 1.0x but V3 loses
margin, the route needs generic runtime investigation before any public claim.

## What Counts As V3 Work

Benchmark-app-specific native engines do not count as V3. The only acceptable
fixes after this run are reusable RTRDL runtime/language improvements such as:

- prepared graph reuse and compile/cache amortization;
- device-resident stream values where RTDL controls movement;
- generic grouped reductions, compaction, summaries, and component union;
- same-stream phase accounting and transfer/build/query split;
- backend-neutral contracts that keep OptiX and Embree comparisons fair.

## Goal-Level Decision Audit

Decision: pre-register the serious paired benchmark analysis bar before the
active run finishes.

1. Was I foolish? No for this decision.
2. If yes, what actions made it foolish? The foolish path would be waiting for
   results and then inventing a favorable bar.
3. Was there another path? Yes. I could have reported only raw rows and argued
   later, but that repeats the previous scoped-evidence mistake.
4. Can I now try a different path? Yes. The active run is judged against this
   pre-registered bar, and V3 stays `redo_required` unless the evidence clears
   it.
