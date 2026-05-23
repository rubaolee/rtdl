# Goal2473 - Grouped-union atomic scale telemetry

Date: 2026-05-21

Status: pod evidence collected. This is diagnostic telemetry for the next
generic grouped-continuation optimization; it is not a new native optimization
and does not authorize a performance claim.

## Purpose

Goal2472 showed that launch-level query-range blocking is correct but slower
than the unblocked grouped-union path. Before designing a true segmented or
proposal-reduction continuation, Goal2473 measures the actual parent/fallback
atomic counts at the current RT-DBSCAN benchmark scale using the Goal2471
telemetry counters.

The question is whether the remaining grouped-union cost is primarily a large
duplicate global-atomic storm, or whether the next design must also address RT
hit traversal/reporting and anyhit overhead.

## Pod

```text
ssh root@69.30.85.171 -p 22118 -i /Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

Environment:

```text
host: dd76e004260f
gpu: NVIDIA RTX A5000, driver 570.211.01
cuda nvcc: Build cuda_12.8.r12.8/compiler.35583870_0
OptiX headers: NVIDIA/optix-dev v8.0.0
```

The pod tree was a filtered rsync of the local dirty Goal2467-2473 working
tree. Because `.git` was intentionally excluded from that pod sync, report JSON
`source_commit` is empty; the local base commit at sync time was
`a9193856547bf692069955a3dbaf6c3e00c09b1b`.

## Command

```text
PYTHONPATH=src:. python scripts/goal2473_grouped_union_atomic_scale_pod_runner.py \
  --repeat-count 3 \
  --output docs/reports/goal2473_grouped_union_atomic_scale_pod.json
```

Artifacts:

```text
docs/reports/goal2473_grouped_union_atomic_scale_pod.json
```

## Results

The runner warms the prepared OptiX+CuPy grouped-stream adapter to compute and
cache threshold flags, then directly measures the native grouped-union call
without telemetry and with telemetry. Values below are tail medians after
discarding repeat 1.

| points | path | all core | parent attempts | parent successes | attempts / point | parent success rate | fallback attempts | fallback successes | baseline native sec | telemetry native sec |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 32,768 | predicated self-query | false | 40,436.0 | 32,763.0 | 1.2340 | 0.8102 | 5.0 | 4.0 | 0.031314 | 0.031195 |
| 65,536 | all-items self-query | true | 77,890.5 | 65,532.0 | 1.1885 | 0.8413 | 0.0 | 0.0 | 0.083171 | 0.083804 |

## Interpretation

The current optimized grouped-union path is not issuing tens or hundreds of
global parent atomics per point. Parent attempts are only about 1.19x-1.23x the
point count, and most attempts succeed. This means a naive proposal-reduction
design that only tries to remove duplicate parent atomics is unlikely to create
a large win on the current benchmark rows.

The 65,536-point all-items route still spends about 83 ms in native grouped
union while recording only about 78k parent atomic attempts. The next
optimization should therefore investigate RT hit traversal/reporting and anyhit
work avoided by earlier culling, not just global atomicMin pressure.

## Boundary

- No DBSCAN-specific native ABI was added.
- This uses existing generic fixed-radius grouped-union telemetry.
- The data is diagnostic and does not authorize public speedup wording.
- RT-DBSCAN remains the stress benchmark; the next native primitive must remain
  app-independent.

## Next Step

Do not proceed with a proposal-reduction design that assumes global parent
atomic duplication is the dominant cost. The next design should either:

- reduce the number of reported intersections before anyhit, for example by
  stronger generic culling or a traversal contract that avoids hits that cannot
  change connectivity; or
- restructure the grouped-continuation kernel so useful connectivity proposals
  are produced with fewer anyhit callbacks, while preserving fail-closed
  fallback and generic fixed-radius/grouped-union vocabulary.

Goal2471 telemetry should remain in the loop, but it is now evidence that
atomic-count reduction alone is not enough for the current benchmark shape.
