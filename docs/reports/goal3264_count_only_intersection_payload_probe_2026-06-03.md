# Goal3264: Count-Only Intersection Payload Probe

**Date:** 2026-06-03  
**Status:** small positive optimization, not a release claim  
**Scope:** generic OptiX closed-shape membership count-only path

## Purpose

After Goal3263 showed that a prepared-edge AoS layout increased memory traffic and regressed the RayJoin PIP benchmark, Goal3264 tested a different generic idea: avoid invoking the any-hit program for count-only closed-shape membership.

The intersection program already decides whether the query point satisfies the closed-shape predicate. In count-only mode (`output == nullptr && output_capacity == 0`), it can increment payload slot 2 directly and return, while row-output modes still report intersections through any-hit.

## Pod Evidence

| Artifact | Commit | RTDL PIP ms | RayJoin PIP ms | RTDL / RayJoin | Count | Candidate count pass first sample |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `goal3263_prepared_edge_layout_gated_default_pod_2026-06-03.json` | `2c77ff28` | 0.324178 | 0.193278 | 1.677x | 1430 | 0.254995 ms |
| `goal3264_count_only_intersection_payload_pod_2026-06-03.json` | `4cfea7d7` | 0.322377 | 0.193930 | 1.662x | 1430 | 0.255590 ms |

Both artifacts are source-clean, record `query_axis: "z_point"`, preserve count 1430, and keep all claim-boundary flags false.

## Interpretation

This is a correct but small win. It removes avoidable count-only any-hit work, but the measured candidate-count phase is essentially unchanged. That means the dominant remaining cost is still the point/closed-shape predicate and the per-edge memory/control pattern, not the any-hit shader dispatch itself.

The optimization stays because it is generic, simple, and does not regress the normal path. It should not be used to claim a broad speedup.

## Boundary

This report does not authorize release, public speedup wording, broad RT-core claims, true zero-copy claims, RayJoin paper reproduction claims, or `RTDL beats RayJoin` claims.

## Next Target

The next performance work should focus on edge reuse rather than more scalar arithmetic removal:

- shape-local edge blocking that lets multiple point probes reuse loaded edge coordinates;
- warp-cooperative predicate evaluation for points testing the same shape;
- additional datasets to decide whether z-point should become a documented public mode.
