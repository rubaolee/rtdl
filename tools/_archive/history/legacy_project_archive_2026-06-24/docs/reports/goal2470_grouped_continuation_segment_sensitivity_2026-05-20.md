# Goal2470 - Grouped-continuation segment sensitivity

Date: 2026-05-20

Status: Mac-local design evidence only. This is not a native implementation,
not pod timing, and not a performance claim.

## Purpose

Goal2467 defined the next generic primitive target:

```text
generic_fixed_radius_blocked_grouped_component_continuation_3d
```

Goal2469 closed the immediate benchmark-consumer row-materialization issue.
The next performance problem is again the native grouped-union continuation:
reduce global atomic pressure or intermediate storage without introducing a
DBSCAN-specific native ABI.

This report uses the Goal2467 CPU simulator to test one design question before
native work:

> Would simple fixed-size hit-stream segmentation be enough, or does the native
> prototype need smarter spatial/duplicate-reduction structure?

## Method

Command shape:

```text
PYTHONPATH=src:. python - <<'PY'
from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    make_rt_dbscan_points,
    fixed_radius_pairs_and_neighbor_counts_3d,
    simulate_fixed_radius_blocked_grouped_component_continuation_3d,
)

for n in [512, 1024, 2048]:
    pts = make_rt_dbscan_points("clustered3d", point_count=n, seed=20260520)
    _, counts = fixed_radius_pairs_and_neighbor_counts_3d(pts, radius=0.055)
    flags = tuple(c >= 12 for c in counts)
    for segment_target_hits in [64, 128, 256, 512, 1024, 2048]:
        _, metadata = simulate_fixed_radius_blocked_grouped_component_continuation_3d(
            pts,
            radius=0.055,
            predicate_flags=flags,
            neighbor_counts=counts,
            segment_target_hits=segment_target_hits,
        )
PY
```

The simulator partitions the generic fixed-radius hit stream and deduplicates
segment-local union proposals before applying global parent updates. It is a
semantic and telemetry oracle, not a native performance proxy.

## Results

`baseline` is predicate-true pair count before segment-local deduplication.
`attempts` is deduplicated global parent atomic attempts in the simulator.
`reject` is `1 - attempts / baseline`.

| Points | Segment target hits | Hit pairs | Segments | Attempts | Baseline | Reject | Successes |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 512 | 64 | 17,138 | 268 | 16,878 | 17,078 | 0.0117 | 499 |
| 512 | 128 | 17,138 | 134 | 16,258 | 17,078 | 0.0480 | 499 |
| 512 | 256 | 17,138 | 67 | 13,943 | 17,078 | 0.1836 | 499 |
| 512 | 512 | 17,138 | 34 | 9,311 | 17,078 | 0.4548 | 499 |
| 512 | 1,024 | 17,138 | 17 | 5,408 | 17,078 | 0.6833 | 499 |
| 512 | 2,048 | 17,138 | 9 | 2,985 | 17,078 | 0.8252 | 499 |
| 1,024 | 64 | 66,878 | 1,045 | 66,665 | 66,852 | 0.0028 | 1,016 |
| 1,024 | 128 | 66,878 | 523 | 66,053 | 66,852 | 0.0120 | 1,016 |
| 1,024 | 256 | 66,878 | 262 | 63,413 | 66,852 | 0.0514 | 1,016 |
| 1,024 | 512 | 66,878 | 131 | 53,405 | 66,852 | 0.2011 | 1,016 |
| 1,024 | 1,024 | 66,878 | 66 | 36,085 | 66,852 | 0.4602 | 1,016 |
| 1,024 | 2,048 | 66,878 | 33 | 20,954 | 66,852 | 0.6866 | 1,016 |
| 2,048 | 64 | 268,564 | 4,197 | 268,389 | 268,559 | 0.0006 | 2,043 |
| 2,048 | 128 | 268,564 | 2,099 | 267,758 | 268,559 | 0.0030 | 2,043 |
| 2,048 | 256 | 268,564 | 1,050 | 264,928 | 268,559 | 0.0135 | 2,043 |
| 2,048 | 512 | 268,564 | 525 | 254,223 | 268,559 | 0.0534 | 2,043 |
| 2,048 | 1,024 | 268,564 | 263 | 214,945 | 268,559 | 0.1996 | 2,043 |
| 2,048 | 2,048 | 268,564 | 132 | 144,887 | 268,559 | 0.4605 | 2,043 |

## Interpretation

Small fixed-hit segments are probably not enough. At 2,048 clustered points,
64-hit segments reject only 0.06% of global parent attempts and 256-hit segments
reject only 1.35%. That design would add launch/buffering overhead without
meaningfully reducing global atomic pressure.

Large segments reject many more duplicate proposals, but they also require
larger temporary storage and may reduce scheduling flexibility. At 2,048
points, 2,048-hit segments reject about 46% of attempts. At 512 points, the
same segment target rejects about 82.5%, but that smaller row is not a reliable
proxy for dense benchmark-scale behavior.

The native prototype should therefore avoid a naive "many tiny query chunks"
approach. The first serious implementation should do at least one of:

- use large enough fixed segment buffers to create measurable proposal
  rejection;
- group hits by spatial cell, Morton bucket, or query/source locality so
  duplicate component proposals co-reside inside a segment;
- emit explicit telemetry showing whether reduced global atomic attempts
  justify the extra phases and temporary memory.

## Boundary

- No native ABI was added.
- No benchmark-app route changed.
- No pod timing was collected.
- No performance claim is authorized.
- RT-DBSCAN remains only the stress benchmark; the target remains a generic
  fixed-radius grouped component continuation.

## Next Step

The next implementation step should be a native OptiX prototype only if it can
report the Goal2467 telemetry fields and avoid DBSCAN vocabulary:

- `segment_count`;
- `segment_target_hits`;
- `max_segment_hits`;
- `global_parent_atomic_attempts`;
- `global_parent_atomic_successes`;
- `local_or_segment_union_proposals`;
- `deduplicated_union_proposals`;
- `proposal_rejection_rate`;
- `fallback_to_unblocked_grouped_union`.

That step needs pod validation because the value depends on native launch
overhead, buffer traffic, and global atomic behavior.
