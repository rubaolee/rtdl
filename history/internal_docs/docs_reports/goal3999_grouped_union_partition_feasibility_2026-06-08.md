# Goal3999 Grouped-Union Partition Feasibility Probe

Date: 2026-06-08

## Verdict

`needs-more-evidence`

Goal3999 tested whether the next dense fixed-radius grouped-union improvement
should be a simple partition-assisted primitive. The result is constructive but
bounded: partition summaries are useful, especially for skipping far cell pairs
and summarizing some definitely-within-radius cell pairs, but they do not by
themselves close the RT-DBSCAN grouped-union bottleneck.

The next promising primitive is therefore a hybrid, not a plain grid rewrite:
use a generic device-resident partition to summarize safe interior cell pairs,
keep RT traversal for ambiguous boundary pairs, and preserve convergence/root
metadata for the grouped-union continuation.

Artifact:
`docs/reports/goal3999_grouped_union_partition_feasibility.json`

## Why This Probe Was Needed

Goal3996 and Goal3998 used `clustered3d` with radius `0.5` as a stress lens.
That profile exposed the huge candidate/root-read pressure and rejected the
stale source-root payload idea.

However, the active RT-DBSCAN benchmark defaults use smaller radii:

| Profile | Current benchmark radius |
| --- | ---: |
| `clustered3d` | `0.055` |
| `road3d` | `0.030` |
| `ngsim_dense` | `0.012` |

So Goal3999 reran the design question at the benchmark radii first, and kept
the `clustered3d` / `0.5` row explicitly labeled as stress-only.

## Method

For each profile at `65,536` points, the probe builds deterministic RT-DBSCAN
points and partitions them into uniform cells at three sizes:

| Label | Cell size |
| --- | --- |
| `radius_x_1` | `radius` |
| `radius_x_0.5` | `radius / 2` |
| `radius_x_0.25` | `radius / 4` |

For each occupied cell pair, the probe uses cell AABBs to classify the pair:

- `safe_full`: every point pair in the two cells is guaranteed within radius;
- `safe_skip`: every point pair is guaranteed outside radius;
- `ambiguous`: the cell AABBs overlap the radius boundary and need finer work.

This is a CPU feasibility probe over the generated fixture. It does not add a
native ABI, does not measure a new runtime path, and does not authorize a
performance claim.

## Results

Best row per profile, choosing the tested cell size with the lowest ambiguous
pair ratio:

| Profile | Purpose | Radius | Best cell | Occupied cells | Ambiguous / all pairs | Safe-full / near pairs | Ambiguous / near pairs |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `clustered3d` | current benchmark default | `0.055` | `radius_x_0.25` | `4,071` | `0.1414` | `0.2333` | `0.7667` |
| `road3d` | current benchmark default | `0.030` | `radius_x_0.25` | `4,118` | `0.0400` | `0.2995` | `0.7005` |
| `ngsim_dense` | current benchmark default | `0.012` | `radius_x_0.25` | `34,552` | `0.0044` | `0.4650` | `0.5350` |
| `clustered3d` | stress row, not default | `0.500` | `radius_x_0.25` | `47` | `0.4184` | `0.3747` | `0.6253` |

## Interpretation

Partitioning is not useless. At the actual benchmark radii it can classify most
global point pairs as far outside the radius and can summarize some interior
near pairs. The strongest default-radius signal is `ngsim_dense`, where
`radius/4` cells make almost half of near pair work safe-full by the AABB test.

But the remaining ambiguous near-boundary work is still substantial:

- `clustered3d`: `76.67%` of near pair upper bound remains ambiguous;
- `road3d`: `70.05%` of near pair upper bound remains ambiguous;
- `ngsim_dense`: `53.50%` of near pair upper bound remains ambiguous.

That means a simple "build cells, union cells" route is not enough. It would
either lose exactness at boundaries or still need a significant fine-grained
candidate path.

The stress row also remains important, but it must not be confused with the
current benchmark default. At radius `0.5`, only `47` cells are occupied, yet
the ambiguous pair upper bound remains `41.84%` of all pairs. This matches the
Goal3996/3998 lesson: for very dense, high-radius grouped union, coarse
partitioning alone cannot replace convergence-aware traversal.

## Next Generic Primitive Direction

Promote neither a stale source-root payload nor a plain CPU-planned grid route.
The next design should be a generic device-resident hybrid primitive:

1. Produce or reuse prepared spatial partitions with cell AABBs and counts.
2. Summarize `safe_full` cell pairs as coarse grouped-union work without
   materializing every pair.
3. Route `ambiguous` cell pairs through the existing RT fixed-radius traversal
   or a bounded candidate stream.
4. Keep convergence/root metadata explicit, including staleness and pass count.
5. Preserve the engine boundary: fixed-radius pairs, partitions, components,
   roots, and union events are allowed; DBSCAN, clusters, epsilon/min-points,
   and app labels stay out of native ABI names.

## Boundary

This is design evidence only. It does not authorize release, public speedup
wording, broad RT-core speedup wording, whole-app acceleration wording,
paper-reproduction wording, true-zero-copy wording, automatic partner/backend
selection, or app-specific native-engine logic.
