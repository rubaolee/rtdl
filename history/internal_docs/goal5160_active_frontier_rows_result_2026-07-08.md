# Goal5160 - Active Frontier Rows Result

## Verdict

`completed_native_active_frontier_rows`

## What Changed

Goal5160 adds a generic native ABI option to avoid emitting pruned diagnostic
rows from the 3-D cell-MBR nearest-frontier OptiX backend:

```text
emit_pruned_rows: bool = True
```

Default behavior remains backward compatible: `emit_pruned_rows=True` still
returns inline, offload, and pruned rows. Streaming consumers that ignore pruned
rows can set:

```text
emit_pruned_rows=False
```

The X-HD representative route now uses:

```text
emit_pruned_rows=False
return_split_frontiers=False
```

because it immediately passes the ABI row table into:

```text
nearest_witness_from_cell_mbr_frontier_numpy_columns
```

and that continuation ignores pruned rows.

This is a generic frontier-row emission option, not an X-HD-specific primitive.

## Files Changed

```text
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_api.cpp
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
tests/goal5148_native_3d_cell_mbr_frontier_test.py
tests/goal5159_row_table_only_frontier_route_test.py
tests/goal5160_active_frontier_rows_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_active_frontier_profile_pod.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## Native Semantics

Before Goal5160, the native any-hit path appended a row for every cell within
the route radius, including rows whose MBR lower bound could not beat the
current best distance:

```text
kind = pruned
```

Those rows were useful as diagnostics and for full frontier partition consumers,
but the X-HD streaming route did not consume them. It only needed inline/offload
rows that could still improve the nearest witness.

Goal5160 moves the pruned-row check before the native append:

```text
if kind == pruned and emit_pruned_rows == false:
    ignore intersection without atomic row append
```

So the backend avoids:

- atomic append for pruned rows;
- device row storage for pruned rows;
- device-to-host copy of pruned rows;
- host sort/unique of pruned rows;
- Python row-table transfer of pruned rows.

The exact distance semantics are unchanged because pruned rows were already
ignored by the continuation.

## POD Build And Command

The POD backend was rebuilt after the native ABI change:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev
```

Production-style route command:

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample256,sample1024 \
  --backend optix \
  --grid-shape 8,8,8 \
  --rtdl-repeat-count 5 \
  --validation-mode author-only \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_active_frontier_profile_pod.json
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation, 550.127.05
```

## Evidence File

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_active_frontier_profile_pod.json
```

## Results

### sample256

```text
matched = true
author Running.AvgTime = 3.967 ms
RTDL route median = 0.013508938252925873 s
RTDL total median = 0.016190804541110992 s
validation_mode = author-only
ratios_authorized = false
```

Frontier row count:

```text
A->B rows: 27099 -> 269
B->A rows: 12022 -> 245
```

### sample1024

```text
matched = true
author Running.AvgTime = 3.991 ms
RTDL route median = 0.07889240980148315 s
RTDL total median = 0.08573675900697708 s
validation_mode = author-only
ratios_authorized = false
```

Frontier row count:

```text
A->B rows: 189472 -> 2272
B->A rows: 82544  -> 2185
```

Median route profile after Goal5160:

```text
A->B frontier phase = 0.0025987327098846436 s
A->B seed phase = 0.030864723026752472 s
A->B continuation phase = 0.003309391438961029 s

B->A frontier phase = 0.0024597197771072388 s
B->A seed phase = 0.02762702852487564 s
B->A continuation phase = 0.0031762272119522095 s
```

## Before / After Against Goal5159

The comparable Goal5159 production matrix reported:

```text
sample256 RTDL route median = 0.017566122114658356 s
sample1024 RTDL route median = 0.10764291137456894 s
```

Goal5160 reports:

```text
sample256 RTDL route median = 0.013508938252925873 s
sample1024 RTDL route median = 0.07889240980148315 s
```

So, for the RTDL route itself:

```text
sample256 route improvement ~= 1.30x vs Goal5159
sample1024 route improvement ~= 1.36x vs Goal5159
```

Across the recent production-route optimization line:

```text
Goal5155 sample1024 production route ~= 0.301 s
Goal5157 after continuation vectorization ~= 0.170 s
Goal5158 after seed vectorization ~= 0.114 s
Goal5159 after row-table-only split avoidance ~= 0.108 s
Goal5160 after active-row native emission ~= 0.079 s
```

This is about a 3.8x RTDL-route improvement from Goal5155 to Goal5160 on the
same representative sample1024 route family.

## Interpretation

Goal5160 is the first post-5158 frontier change that substantially reduces the
frontier row volume. It shows that the previous frontier cost was dominated by
emitting and moving pruned rows that the streaming nearest-witness continuation
does not consume.

After Goal5160, frontier row production is no longer the dominant measured
phase. The next measured route target is again the nearest-cell-MBR seed:

```text
sample1024 seed combined ~= 0.0585 s
sample1024 frontier combined ~= 0.0051 s
sample1024 continuation combined ~= 0.0065 s
```

This result is still not author-performance parity. The author and RTDL numbers
have different phase boundaries, exact paper datasets are still unavailable,
and no ratio is authorized.

## Validation

Local:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/data/manifest.json
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_active_frontier_profile_pod.json
py -m unittest tests.goal5160_active_frontier_rows_test \
  tests.goal5159_row_table_only_frontier_route_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test \
  tests.goal5158_vectorized_nearest_cell_mbr_seed_test \
  tests.goal5157_vectorized_frontier_nearest_continuation_test
Ran 16 tests OK
```

POD:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev

python3 -m unittest tests.goal5148_native_3d_cell_mbr_frontier_test \
  tests.goal5159_row_table_only_frontier_route_test \
  tests.goal5158_vectorized_nearest_cell_mbr_seed_test \
  tests.goal5157_vectorized_frontier_nearest_continuation_test
Ran 13 tests OK

python3 -m unittest tests.goal5160_active_frontier_rows_test \
  tests.goal5159_row_table_only_frontier_route_test \
  tests.goal5148_native_3d_cell_mbr_frontier_test \
  tests.goal5158_vectorized_nearest_cell_mbr_seed_test
Ran 13 tests OK
```

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author `Running.AvgTime` parity;
- denominator-aligned author-vs-RTDL speedup;
- native fused X-HD RT-core equivalence;
- whole-program performance reproduction.

It claims only a generic native frontier-row emission improvement and measured
RTDL-route phase reduction on representative same-source fixtures.
