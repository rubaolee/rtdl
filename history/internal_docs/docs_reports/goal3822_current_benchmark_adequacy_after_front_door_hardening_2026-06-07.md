# Goal3822 Current Benchmark Adequacy After Front-Door Hardening

Date: 2026-06-07

Status: implemented locally.

## Purpose

Goal3822 refreshes the current benchmark adequacy source of truth after the
Goal3818-3820 benchmark front-door hardening pass.

This is deliberately narrower than a release packet. It records that the
current learner-facing benchmark story now has:

- one bounded executable A5000 smoke command for all ten promoted benchmark
  apps;
- repaired Hausdorff and contact-manifold command contracts from the first
  smoke pass;
- an explicit triangle-counting native timing route instead of the slower
  `--optix-graph-mode auto` fallback;
- an executable RTNN prepared OptiX ranked-summary app mode instead of only a
  plan/evidence route.

The source of truth remains:

`src/rtdsl/v2_9_benchmark_adequacy.py`

The current version string is:

`rtdl.v2_10.benchmark_adequacy_after_goal3820.v2`

## Front-Door Deltas

| Benchmark app | Previous adequacy wording | Goal3822 wording |
| --- | --- | --- |
| `rtnn` | prepared primitive/aggregate path with earlier plan and packet evidence | executable `--mode prepared_optix_ranked_summary` front door, with Goal3820 A5000 JSON evidence at 4096 and 65536 points |
| `triangle_counting` | generic RT graph summary primitive | generic RT graph summary primitive with explicit `--optix-graph-mode native` for current native timing probes |

The Goal3819 triangle-counting probe is route-selection evidence only. It
records `rt_core_accelerated=false` and keeps triangle-count RT-core claim
authorization false.

The Goal3820 RTNN probe is front-door evidence only. It records an executable
prepared OptiX ranked-summary app mode, but it does not authorize RTNN paper
reproduction wording or public speedup wording.

## Current Matrix

| Benchmark app | Adequacy | Current front-door note |
| --- | --- | --- |
| `hausdorff_xhd` | adequate | Goal3818 command contract repaired and executable |
| `spatial_rayjoin` | strong | existing promoted routes remain executable |
| `rt_dbscan` | strong | existing promoted route remains executable |
| `robot_collision` | strong | existing promoted primitive route remains executable |
| `contact_manifold` | adequate | Goal3818 command contract repaired and executable |
| `raydb_style` | adequate | existing primitive-first grouped reduction route remains executable |
| `barnes_hut` | adequate | existing promoted route remains executable |
| `librts_spatial_index` | adequate | existing prepared AABB route remains executable |
| `rtnn` | adequate | Goal3820 adds executable `prepared_optix_ranked_summary` app mode |
| `triangle_counting` | adequate | Goal3819 documents explicit native mode for timing hygiene |

## Boundary

Goal3822 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, true-zero-copy wording, automatic
partner selection, AMD performance wording, paper-reproduction wording, package
installation wording, or app-specific native-engine logic.

It is an internal consistency refresh: the benchmark adequacy metadata and
learner docs now point to the current executable app front doors that were
actually run.
