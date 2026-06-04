# Goal3263: Prepared Edge Layout Negative Probe and Gate

**Date:** 2026-06-03  
**Status:** accepted as a negative performance probe; gated off by default  
**Scope:** generic OptiX closed-shape membership predicate data layout

## Purpose

Claude's Goal3259 review identified the per-candidate closed-shape edge predicate as the remaining bottleneck after the z-point probe, single-pass predicate, and squared-boundary tuning chain. Goal3262 tested a generic prepared-edge layout: precompute each closed-shape edge as `(ax, ay, bx, by, dx, dy, len2, crossing_scale)` in the prepared handle and let the device predicate read that edge column instead of recomputing edge deltas.

The result was useful but negative. The layout compiled and preserved counts, but it slowed the RayJoin PIP same-slice path. Goal3263 therefore gates the prepared-edge layout behind `RTDL_OPTIX_POINT_PRIMITIVE_USE_PREPARED_EDGE_LAYOUT` and restores the split-vertex fallback as the default.

## Pod Evidence

| Artifact | Commit | Mode | RTDL PIP ms | RayJoin PIP ms | RTDL / RayJoin | Count | Candidate count pass first sample |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `goal3262_prepared_edge_layout_negative_probe_pod_2026-06-03.json` | `831df1b1` | prepared edge default | 0.381375 | 0.193993 | 1.966x | 1430 | 0.312286 ms |
| `goal3263_prepared_edge_layout_gated_default_pod_2026-06-03.json` | `2c77ff28` | split-vertex default | 0.324178 | 0.193278 | 1.677x | 1430 | 0.254995 ms |

Both artifacts are source-clean, record `query_axis: "z_point"`, preserve count 1430, and keep all claim-boundary flags false.

## Interpretation

The negative probe shows that this workload is not dominated by edge arithmetic after Goal3258. The prepared-edge AoS layout removes some arithmetic, but it also increases memory traffic per edge: instead of reading four vertex floats and computing deltas locally, each edge read pulls a larger record. On this A40 same-slice benchmark, that tradeoff loses.

The current default is therefore the proven split-vertex path. The prepared-edge layout remains available only as an explicit experimental mode for future datasets where arithmetic and division cost might dominate memory traffic.

## Boundary

This report does not authorize release, public speedup wording, broad RT-core claims, true zero-copy claims, RayJoin paper reproduction claims, or `RTDL beats RayJoin` claims. It records a negative engineering result and the follow-up guard that prevents the regression from becoming default behavior.

## Next Target

The next RayJoin PIP target should avoid increasing per-edge memory traffic. Better candidates are:

- a smaller SoA cache for only one or two expensive edge scalars, if measurements prove arithmetic-bound behavior on another dataset;
- shape-local edge blocking or warp-cooperative evaluation that reuses the same edge across multiple point probes;
- broader same-contract coverage before making z-point a public API mode.
