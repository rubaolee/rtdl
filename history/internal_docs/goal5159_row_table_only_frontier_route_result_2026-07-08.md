# Goal5159 - Row-Table-Only Native Frontier Route Result

## Verdict

`completed_row_table_only_native_frontier_route_hygiene`

## What Changed

Goal5159 adds an opt-in row-table-only mode to the generic native 3-D
cell-MBR frontier helper:

```text
cell_mbr_nearest_frontier_native_3d_optix_columns(..., return_split_frontiers=False)
```

The default remains backward compatible:

```text
return_split_frontiers=True
```

When a streaming consumer only needs the ABI row table, the helper no longer
materializes the derived `inline_frontier`, `offload_frontier`, and
`pruned_frontier` dictionaries from the native row table. The X-HD route uses
this row-table-only mode because it immediately passes:

```text
frontier["row_table"]
```

to the generic nearest-witness continuation.

This is a generic RTDL helper hygiene change, not an X-HD primitive.

## Files Changed

```text
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
tests/goal5148_native_3d_cell_mbr_frontier_test.py
tests/goal5159_row_table_only_frontier_route_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_row_table_only_frontier_profile_pod.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## Compatibility

Existing callers are preserved:

- default helper behavior still returns split frontiers;
- the route can explicitly choose row-table-only mode;
- metadata records `split_frontiers_returned`;
- row-table contract stays `generic_cell_mbr_nearest_frontier_row_table`;
- app semantics remain `none`.

## POD Command

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample256,sample1024 \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_row_table_only_frontier_profile_pod.json
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation, 550.127.05
```

## Evidence File

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_row_table_only_frontier_profile_pod.json
```

## Results

### sample256

```text
matched = true
author Running.AvgTime = 4.096 ms
RTDL route median = 0.017566122114658356 s
RTDL total median = 0.019529104232788086 s
validation_mode = author-only
ratios_authorized = false
```

Median frontier profile:

```text
A->B frontier rows = 27099
A->B frontier phase = 0.004112958908081055 s

B->A frontier rows = 12022
B->A frontier phase = 0.0024756938219070435 s
```

### sample1024

```text
matched = true
author Running.AvgTime = 4.081 ms
RTDL route median = 0.10764291137456894 s
RTDL total median = 0.11500988900661469 s
validation_mode = author-only
ratios_authorized = false
```

Median route profile:

```text
A->B frontier rows = 189472
A->B frontier phase = 0.03566768020391464 s
A->B seed phase = 0.01990629732608795 s
A->B continuation phase = 0.005608171224594116 s

B->A frontier rows = 82544
B->A frontier phase = 0.010616570711135864 s
B->A seed phase = 0.019933991134166718 s
B->A continuation phase = 0.0038464367389678955 s
```

## Before / After Against Goal5158

The comparable Goal5158 production matrix reported:

```text
sample256 RTDL route median = 0.018150337040424347 s
sample1024 RTDL route median = 0.11371012777090073 s
```

Goal5159 reports:

```text
sample256 RTDL route median = 0.017566122114658356 s
sample1024 RTDL route median = 0.10764291137456894 s
```

So, for the RTDL route itself:

```text
sample256 route improvement ~= 1.03x vs Goal5158
sample1024 route improvement ~= 1.06x vs Goal5158
```

The targeted frontier phase moves only modestly:

```text
sample1024 frontier median total before ~= 0.0507 s
sample1024 frontier median total after  ~= 0.0463 s
frontier phase improvement ~= 1.09x
```

## Interpretation

This is a small but clean route improvement. More importantly, it is a useful
diagnostic result:

- split frontier materialization was not the main remaining cost;
- the route still emits large row volumes, especially 189472 A->B frontier rows
  on sample1024;
- the next hard target is native frontier row volume/production itself, not
  Python-side split-frontier derivation.

This goal does **not** claim author-performance parity. The author and RTDL
timings still have different phase boundaries and no ratio is authorized.

## Validation

Local:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/data/manifest.json
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_row_table_only_frontier_profile_pod.json
py -m unittest tests.goal5159_row_table_only_frontier_route_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test \
  tests.goal5158_vectorized_nearest_cell_mbr_seed_test \
  tests.goal5157_vectorized_frontier_nearest_continuation_test
Ran 13 tests OK
```

POD:

```text
python3 -m unittest tests.goal5159_row_table_only_frontier_route_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test \
  tests.goal5158_vectorized_nearest_cell_mbr_seed_test
Ran 10 tests OK
```

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author `Running.AvgTime` parity;
- denominator-aligned author-vs-RTDL speedup;
- native fused X-HD RT-core equivalence;
- whole-program performance reproduction.

It claims only a generic RTDL helper compatibility-preserving route hygiene
improvement and measured RTDL-route phase reduction on representative
same-source fixtures.
