# Goal4014 Compressed Partition Enumeration Accounting

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal4014 makes the Goal3999/4011 partition feasibility probe expose the
compressed enumeration accounting that it already uses internally. This closes a
traceability gap after Goal4012: the next native primitive must avoid a dense
cell-pair matrix, so the feasibility artifact must prove whether the tool is
also avoiding that shape.

Goal4014 therefore records the no dense cell-pair matrix boundary in both the
script artifact schema and this report.

This is still CPU feasibility evidence. It does not add a native ABI, does not
change the accepted grouped-stream runtime route, and does not authorize public
speedup wording.

## Pod Evidence

Hardware: NVIDIA RTX 4000 Ada Generation pod.

Source commit: `eb4795d8`.

Artifact:

- `docs/reports/goal4014_compressed_partition_enumeration_accounting.json`

Command shape:

```bash
python3 scripts/goal3999_grouped_union_partition_feasibility_probe.py \
  --goal Goal4014 \
  --profiles clustered3d,road3d,ngsim_dense \
  --point-count 65536 \
  --seed 20260608 \
  --cell-factors 0.125 \
  --output docs/reports/goal4014_compressed_partition_enumeration_accounting.json
```

## What Changed

`scripts/goal3999_grouped_union_partition_feasibility_probe.py` now records:

- `enumeration_strategy = compressed_occupied_key_bounded_offsets`;
- `dense_cell_pair_matrix_materialized = false`;
- `bounded_offset_count`;
- `enumerated_cell_pairs`;
- `enumerated_pair_upper`;
- `far_safe_skip_cell_pairs`;
- `far_safe_skip_pair_upper`;
- corresponding ratios for enumerated and far-skip work.

## Results

All rows use `radius_x_0.125`, the best tested partition factor from Goal4011.

| Profile | Occupied partitions | Dense equivalent cell pairs | Enumerated cell pairs | Enumerated / dense | Far-safe-skip pair ratio | Safe-full / near | Ambiguous / near |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 16,675 | 139,036,150 | 19,462,589 | 0.139982 | 0.795659 | 0.632970 | 0.367030 |
| `road3d` | 18,031 | 162,567,496 | 10,253,945 | 0.063075 | 0.936004 | 0.668465 | 0.331535 |
| `ngsim_dense` | 60,070 | 1,804,232,485 | 30,469,176 | 0.016888 | 0.983079 | 0.940124 | 0.059876 |

The strongest signal is `ngsim_dense`: a dense matrix would contain about
1.804 billion occupied-cell pairs, while bounded-offset enumeration visits about
30.47 million. That is still substantial work for Python, but it is the right
native/device-resident shape: compressed occupied partition keys plus bounded
near offsets, not a dense cell-pair matrix.

## Design Consequence

Goal4014 strengthens the Goal4012 contract:

1. The next implementation should start with a generic device-resident
   partition summary producer.
2. The producer should expose partition ids, occupied partition keys, offsets,
   counts, AABBs, and bounded near-partition pairs.
3. Safe-full, safe-skip, ambiguous, root-read, and convergence/staleness
   counters should remain visible.
4. Same-contract parity against the current grouped-stream route is mandatory
   before any route promotion.

This stays app-agnostic. The native vocabulary should remain fixed-radius
pairs, partitions, groups, component roots, convergence, and status counters.
Do not add DBSCAN, clustering, epsilon, min-points, or app labels to the native
ABI.

## Boundary

Goal4014 does not authorize public speedup wording.

It also does not authorize release, broad RT-core speedup wording, whole-app
acceleration wording, paper-reproduction wording, true-zero-copy wording,
automatic partner/backend selection, or app-specific native-engine logic.
