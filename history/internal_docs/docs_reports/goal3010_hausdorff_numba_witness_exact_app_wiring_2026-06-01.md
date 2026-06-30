# Goal3010: Hausdorff Numba Witness Exact App Wiring

## Purpose

Goal3010 uses the Goal3008 Numba witness front door in the Hausdorff benchmark
app. The new mode is:

`partner_numba_witness_exact`

It computes exact directed Hausdorff summaries by:

1. building caller-owned dense grouped score rows from point pairs;
2. passing `group_ids:int64`, `item_ids:int64`, and `scores:float64` to
   `group_argmin_then_global_argmax_partner_columns(..., partner="numba")`;
3. comparing the two directed distances in Python to produce the undirected
   Hausdorff distance.

## Boundary

This is an exact dense partner-continuation path, not an RT-core path. It is
useful because it proves the benchmark app can call the same generic Numba
witness reducer that RTNN/Hausdorff-style RT hit streams will need later.

It deliberately records:

- `host_score_row_materialization_used: True`;
- `rt_core_accelerated: False`;
- no native continuation;
- no app-specific native engine logic.

## Claim Boundary

Goal3010 does not authorize:

- v2.6 release;
- public speedup wording;
- Numba speedup wording;
- RT-core speedup wording;
- whole-app speedup wording;
- true-zero-copy wording;
- automatic partner selection;
- app-specific native-engine logic.

## Next Step

Run the mode on the pod for app-level correctness evidence, then decide whether
the next performance step should be a Numba dense score-row kernel or an
RT-hit-stream producer that feeds the same generic witness reducer.
