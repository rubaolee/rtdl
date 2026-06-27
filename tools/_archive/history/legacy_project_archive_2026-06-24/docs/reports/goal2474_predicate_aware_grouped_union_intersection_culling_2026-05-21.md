# Goal2474 - Predicate-aware grouped-union intersection culling

Date: 2026-05-21

Status: pod validated as part of Goal2475 on 2026-05-21. This is a generic
OptiX fixed-radius grouped-union culling change, not a DBSCAN-specific native
path. It is not a standalone public performance claim.

## Purpose

Goal2473 showed that the current grouped-union path records only about
1.19x-1.23x parent atomic attempts per point at benchmark scale. That weakens
the hypothesis that duplicate global parent atomics alone dominate the
remaining native time. The next optimization target is therefore to reduce
reported intersections and anyhit callbacks that cannot change generic grouped
connectivity or fallback candidates.

## Change

The OptiX grouped-union intersection program now applies the same generic
predicate logic that anyhit already used as a safety check:

- all-items mode reports only `target > source`;
- predicated mode with a predicate-true source reports only
  `target > source && target_predicate`;
- predicated mode with a predicate-false source reports only
  `target_predicate`, because those hits can update the fallback candidate;
- hits that cannot affect parent union or fallback state are rejected before
  `optixReportIntersection`.

The anyhit checks remain in place for safety. Python metadata records:

```text
grouped_union_intersection_culling_policy =
  all_items_target_gt_source_before_anyhit
  predicate_aware_connectivity_and_fallback_before_anyhit
```

## Boundary

- No native DBSCAN ABI or vocabulary was added.
- The change is expressed only in generic fixed-radius grouped-union terms:
  predicate flags, source, target, parent union, and fallback candidate.
- Default app behavior and output contracts are unchanged.
- This is expected to affect mixed-predicate rows most. All-items rows already
  had `target > source` culling from Goal2465.
- Performance claims are blocked unless reviewed together with the Goal2475
  pod evidence.

## Pod Validation

An earlier pod endpoint
`ssh root@69.30.85.171 -p 22118 -i /Users/rl2025/.ssh/id_ed25519_rtdl_codex`
was checked after the local implementation and returned `Connection refused`.

Goal2474 was pod-validated as part of the Goal2475 build and benchmark run,
because Goal2475 includes the predicate-aware intersection culling introduced
here plus the same-root culling extension.

Successful pod endpoint:

```text
ssh root@69.30.85.177 -p 22181 -i /Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

Environment:

```text
host: ecdc0a16bb30
gpu: NVIDIA RTX A5000, driver 570.211.01
cuda nvcc: Build cuda_12.8.r12.8/compiler.35583870_0
OptiX headers: NVIDIA/optix-dev v8.0.0
```

Focused Goal2457-2475 tests passed on the pod: 61 tests OK.

The combined Goal2474+Goal2475 grouped-stream column-signature timing improved
the previous Goal2472 unblocked baseline:

- 32,768 clustered points: total median improved from 0.043300 s to
  0.041628 s; grouped-native median improved from 0.031052 s to 0.025131 s.
- 65,536 clustered points: total median improved from 0.110211 s to
  0.098348 s; grouped-native median improved from 0.082476 s to 0.066053 s.

The exact evidence and replay commands are recorded in:

```text
docs/reports/goal2475_same_root_grouped_union_intersection_culling_2026-05-21.md
docs/reports/goal2475_same_root_culling_pod/
```
