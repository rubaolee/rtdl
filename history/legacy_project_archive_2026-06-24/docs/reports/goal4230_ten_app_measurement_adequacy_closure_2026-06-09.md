# Goal4230 Ten-App Measurement Adequacy Closure

Date: 2026-06-09

Status: internal release-prep measurement adequacy accepted with boundary

## Purpose

Goal4225 proved that all ten current benchmark front doors execute cleanly on
RTX 4000 Ada, but several rows were intentionally labeled as short health rows
or current-scale rows rather than claim-grade timing rows. Goal4230 reconciles
the supporting stress/long-repeat artifacts and records whether each benchmark
now has at least one second-level measurement source.

This is still not a release authorization. It closes a measurement-readiness
gap, not the final docs, AMD, or 3-AI release-consensus gates.

## Adequacy Table

| App | Supporting evidence | Aggregate timing source | Aggregate sec | Reading |
| --- | --- | --- | ---: | --- |
| `hausdorff_xhd` | Goal4185 | `repeat_protocol.measured_query_total_sec` | `17.03616939485073` | adequate second-level repeated-query evidence |
| `spatial_rayjoin` | Goal4225 | representative mixed-route profile wall time | `9.245572708547115` | adequate representative mixed-route profile; contract split remains visible |
| `rt_dbscan` | Goal4228 | `prepared_query_repeat_protocol.elapsed_sec_total` | `1.7432705983519554` | adequate long-repeat evidence for current single-pass route |
| `robot_collision` | Goal4225 | `run_summary.phase_timing_seconds.traversal.total_sec` | `2.062663112` | adequate resident repeated traversal evidence |
| `contact_manifold` | Goal4186 | `native_collect_total_sec` | `2.063397765159607` | adequate repeat-aware collect-k aggregate evidence |
| `raydb_style` | Goal4225 | `metadata.prepared_phase_timing_summary.native_call_wall.total_sec` | `2.9750420674681664` | adequate primitive-first grouped-count evidence |
| `barnes_hut` | Goal4229 | `prepared_force_repeat_protocol.force_kernel_total_sec` | `1.7285085022449493` | adequate Numba force-summary aggregate evidence |
| `librts_spatial_index` | Goal4185 | `repeat_protocol.query_sec_total` | `1.749403476715088` | adequate prepared AABB-index repeated-query evidence |
| `rtnn` | Goal4189 | sum of `runner_payload.elapsed_runs_sec` | `1.704869568347931` | adequate prepared ranked-summary repeated-query evidence |
| `triangle_counting` | Goal4185 | `timing_ms.run_backend / 1000` | `2.063972443342209` | adequate repeated generic RT-graph summary evidence |

## What This Means

The current NVIDIA/OptiX benchmark surface no longer has a basic
measurement-floor gap for the ten promoted apps. The remaining project-level
work is not another small timing tweak:

- final docs audit and public wording pass,
- fresh multi-AI review over the exact release claims,
- AMD/HIPRT functional and timing evidence on real AMD hardware,
- optional longer release matrix if the user wants a formal public performance
  table rather than an internal release-prep packet.

## Boundary

Goal4230 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording, or
app-specific native-engine logic.
