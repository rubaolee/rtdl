# Goal3012: Numba Pairwise Score Rows for Hausdorff Witness Mode

## Purpose

Goal3012 removes the worst user-facing weakness in the initial Goal3010
Hausdorff Numba witness mode: CPU materialization of the dense score-row table.

The new generic partner primitive is:

`pairwise_l2_sq_score_rows_2d`

It produces device-resident generic score rows:

- `group_ids:int64`: dense source row index;
- `item_ids:int64`: caller-supplied target id;
- `scores:float64`: squared 2D L2 distance.

The Hausdorff app then composes those score rows with the existing generic
`group_argmin_then_global_argmax_partner_columns(..., partner="numba")` witness
front door.

## What Changed

- Added a Numba CUDA score-row producer:
  `run_numba_pairwise_l2_sq_score_rows_2d`.
- Added a public RTDL partner adapter:
  `pairwise_l2_sq_score_rows_2d_partner_columns(..., partner="numba")`.
- Updated `partner_numba_witness_exact` in the Hausdorff benchmark app so score
  rows are generated on the Numba device instead of being materialized by NumPy
  on the host.

## Boundary

This is still an exact dense partner-continuation path, not an RT-core path.

It deliberately records:

- `host_score_row_materialization_used: False`;
- `score_rows_generated_on_partner_device: True`;
- `rt_core_accelerated: False`;
- no native continuation;
- no app-specific native-engine logic.

The remaining known boundary is the grouped arg reducer's preview compaction:
present-group compaction and NaN validation still use host synchronization.

## Claim Boundary

Goal3012 does not authorize:

- v2.6 release;
- public speedup wording;
- Numba speedup wording;
- RT-core speedup wording;
- whole-app speedup wording;
- true-zero-copy wording;
- automatic partner selection;
- app-specific native-engine logic.

## Next Step

Collect clean L4 pod app-level evidence at a larger scale and compare phase
timing against the Goal3010 host-materialized version. The next RT-core-facing
step remains a real native hit-stream producer feeding this same generic witness
reducer.
