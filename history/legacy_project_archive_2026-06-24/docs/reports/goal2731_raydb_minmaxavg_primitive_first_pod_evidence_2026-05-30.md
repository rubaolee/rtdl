# Goal2731: RayDB Min/Max/Avg Primitive-First Pod Evidence

Date: 2026-05-30
Status: accepted as follow-up pod evidence for Claude Goal2729 risk 1

## Purpose

Claude's Goal2729 review accepted the RayDB primitive-first correction with one immediate measurement gap: Goal2727 measured prepared fused grouped reduction versus prepared hit-stream+Triton for `count` and `sum`, but not for `min`, `max`, or `avg_as_sum_count`.

Goal2731 closes that gap on the same RTX A5000 pod grid.

## Artifact

`docs/reports/goal2731_pod_artifacts/goal2731_raydb_primitive_first_minmaxavg_gap_pod_69_30_85_171_2026-05-30.json`

Pod:

- host: `69.30.85.171`
- port: `22167`
- GPU: `NVIDIA RTX A5000, 570.211.01, 24564 MiB`
- commit: `dab6e510da9e094646f7418ff6e05f5addf96dbd`
- repeats: `3`
- warmup: `1`
- group count: `256`

## Results

| Rows | Mode | Prepared fused grouped-reduction sec | Prepared hit-stream+Triton sec | Hit-stream relative to fused primitive |
| ---: | --- | ---: | ---: | ---: |
| 250000 | min | 0.001901 | 0.352522 | 185.4x slower |
| 250000 | max | 0.001814 | 0.266547 | 146.9x slower |
| 250000 | avg_as_sum_count | 0.001941 | 0.317794 | 163.7x slower |
| 1000000 | min | 0.002228 | 0.294435 | 132.1x slower |
| 1000000 | max | 0.002181 | 0.274932 | 126.1x slower |
| 1000000 | avg_as_sum_count | 0.002182 | 0.270163 | 123.8x slower |

All cases reported `matches_cpu_reference = true`.

## Interpretation

The Goal2727 conclusion generalizes to the remaining RayDB scalar grouped reductions measured here. For `min`, `max`, and `avg_as_sum_count`, the prepared fused generic RTDL primitive remains far faster than emitting a typed hit stream and performing the continuation in Triton.

This strengthens the Goal2728 planner rule:

- RayDB grouped scalar reductions should route to the prepared fused generic grouped-reduction primitive.
- Typed hit-stream handoff should remain available for continuations that the fused primitive set cannot express.
- The result still does not authorize public speedup or true-zero-copy wording.

## Boundary

This closes the immediate `min`/`max`/`avg_as_sum_count` measurement gap identified by Claude. It does not close the other Goal2729 risks:

- evidence is still from one RTX A5000 class GPU;
- true-zero-copy remains unauthorized;
- Goal2726 diagnostic ratios must not leak into public performance wording;
- source-inspection tests remain supplementary to artifact-backed tests.

