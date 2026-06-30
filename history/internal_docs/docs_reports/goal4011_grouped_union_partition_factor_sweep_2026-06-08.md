# Goal4011 Grouped-Union Partition Factor Sweep

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal4011 reruns the Goal3999 CPU partition feasibility probe with a denser
factor sweep at the actual RT-DBSCAN benchmark radii. The purpose is to sharpen
the next generic partition-convergence primitive before adding native ABI.

This is not a performance optimization and not a release claim. It is design
evidence for the next native/device-resident grouped-union primitive.

## Pod Evidence

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05.

Source commit: `743567c2`.

Artifact:

- `docs/reports/goal4011_grouped_union_partition_factor_sweep.json`

Command shape:

```bash
python3 scripts/goal3999_grouped_union_partition_feasibility_probe.py \
  --goal Goal4011 \
  --profiles clustered3d,road3d,ngsim_dense \
  --point-count 65536 \
  --seed 20260608 \
  --cell-factors 1.0,0.75,0.5,0.333333,0.25,0.2,0.166667,0.125 \
  --output docs/reports/goal4011_grouped_union_partition_factor_sweep.json
```

## Summary

The earlier Goal3999 `radius_x_0.25` result was useful but not the best tested
partition. Finer partitions reduce ambiguous boundary pair upper bounds
substantially:

| Profile | Radius | Best factor | Ambiguous / all pairs | Ambiguous / near pairs | Safe-full / near pairs | Occupied cells |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `clustered3d` | 0.055 | `radius_x_0.125` | 0.056185 | 0.367030 | 0.632970 | 16,675 |
| `road3d` | 0.030 | `radius_x_0.125` | 0.015654 | 0.331535 | 0.668465 | 18,031 |
| `ngsim_dense` | 0.012 | `radius_x_0.125` | 0.000354 | 0.059876 | 0.940124 | 60,070 |

Compared with `radius_x_0.25`, `radius_x_0.125` cuts ambiguous pair upper
bounds by:

| Profile | `radius_x_0.25` ambiguous pairs | `radius_x_0.125` ambiguous pairs | Reduction |
| --- | ---: | ---: | ---: |
| `clustered3d` | 303,725,488 | 120,653,932 | 60.27% |
| `road3d` | 85,957,890 | 33,615,373 | 60.90% |
| `ngsim_dense` | 9,417,550 | 759,876 | 91.93% |

## Interpretation

The good news: the partition-convergence direction is stronger than Goal3999
initially showed. A smaller partition factor can turn much of the near-pair work
into safe-full or safe-skip summaries, especially on `ngsim_dense`.

The boundary: a naive dense cell-pair matrix is not viable. At `radius_x_0.125`,
occupied cells are high and theoretical total occupied-cell pairs are large:

| Profile | Occupied cells | Total occupied-cell pairs |
| --- | ---: | ---: |
| `clustered3d` | 16,675 | 139,036,150 |
| `road3d` | 18,031 | 162,567,496 |
| `ngsim_dense` | 60,070 | 1,804,232,485 |

So the native primitive should not materialize a dense cell-pair matrix. It
needs a compressed occupied-cell structure plus bounded near-offset enumeration.

## Design Consequence

The next real native slice should expose generic device-resident partition
columns and bounded near-partition traversal:

1. partition id per point;
2. occupied partition keys;
3. partition offsets/counts;
4. partition AABBs;
5. near-partition pair enumeration bounded by radius and cell factor;
6. safe-full, safe-skip, and ambiguous status counters;
7. same-contract parity against the existing grouped stream.

This is still not a DBSCAN native ABI. The vocabulary stays generic:
fixed-radius pairs, partitions, groups, component roots, convergence, and
status counters.

## Boundary

Goal4011 does not authorize release, public speedup wording, broad RT-core
speedup wording, whole-app acceleration wording, paper-reproduction wording,
true-zero-copy wording, automatic partner/backend selection, or app-specific
native-engine logic.
