# Goal4301: Numba Grouped Top-K Device Rank

Date: 2026-06-11

## Verdict

`accept-with-boundary` for an internal v2.11 runtime debt-reduction slice.

Goal4301 adds a generic Numba `grouped_topk_f64` CUDA continuation and wires
`top_k_nearest_points_2d_partner_columns(..., partner="numba")` through it. The
old Goal4299 path generated pairwise score rows on the device, then copied those
rows to the host for deterministic top-k ranking. This goal removes that host
rank materialization from the current adapter path.

## What Changed

- Added `NUMBA_GROUPED_TOPK_F64_OPERATION = "grouped_topk_f64"`.
- Added `describe_numba_grouped_topk_f64()`.
- Added `run_numba_grouped_topk_f64(...)`.
- Added a CUDA kernel for equal contiguous grouped score segments:
  `_numba_grouped_topk_f64_equal_segments_kernel`.
- Added `grouped_topk_f64` to `V2_5_NUMBA_PREVIEW_OPERATIONS`.
- Exported the Numba top-k operation, descriptor, max-k, and runner from
  `rtdsl.__init__`.
- Extended `grouped_topk_f64_partner_columns(..., partner="numba")`.
- Rewired `top_k_nearest_points_2d_partner_columns(..., partner="numba")`:
  `pairwise_l2_sq_score_rows_2d -> grouped_topk_f64 -> dense group-id query-id
  gather and sqrt`.

The primitive is intentionally generic. It ranks `(group_id, item_id, score)`
rows and does not know about RTNN, ANN, points, neighbors, or any benchmark app.

## Contract

The first Numba device top-k path has a precise layout precondition:

`equal_contiguous_group_segments`

That is the layout emitted by the existing Numba
`pairwise_l2_sq_score_rows_2d` producer: dense group ids, one contiguous segment
per source/query group, and equal segment length. The generic grouped top-k
runner rejects malformed layouts through a device error flag plus host-side
exception rather than silently returning partial ranks.

Ranking policy:

- sort by lowest score,
- break score ties by lowest item id,
- emit one-based ranks,
- skip duplicate item ids after the first selected item,
- require `k <= 16` in this preview implementation.

## Validation

Windows focused checks:

```text
$env:PYTHONPATH='src;.'; py -3 -m py_compile src\rtdsl\numba_partner_continuation.py src\rtdsl\partner_adapters.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4301_numba_grouped_topk_device_rank_test tests.goal4299_numba_topk_partner_reference_test tests.goal4298_v2_11_embree_cpu_partner_reference_packet_test

Ran 14 tests in 2.471s
OK (skipped=3)
```

Local Linux executable validation used fresh checkout:

`/home/lestat/work/rtdl_goal4301_check` at base commit `bf12a82b`, with only the
Goal4301 touched files copied in.

```text
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/numba_partner_continuation.py src/rtdsl/partner_adapters.py src/rtdsl/__init__.py
PYTHONPATH=src:. python3 -m unittest tests.goal4301_numba_grouped_topk_device_rank_test tests.goal4299_numba_topk_partner_reference_test

Ran 8 tests in 0.954s
OK
```

Fresh local Linux artifacts:

- `docs/reports/goal4301_ann_candidate_numba_device_topk_local_linux.json`
- `docs/reports/goal4301_ann_candidate_numba_device_topk_copies128_local_linux.json`
- `docs/reports/goal4301_v2_11_rtnn_numba_device_topk_runner_local_linux.json`

The scaled direct artifact records:

```json
{
  "query_count": 384,
  "candidate_count": 384,
  "numba_score_row_count": 147456,
  "v2_11_numba_preview_kernel_status": "device_grouped_topk_after_device_score_rows",
  "host_rank_materialization_used": false
}
```

The v2.11 runner row passed:

```json
{
  "row_id": "rtnn_numba_cpu_partner_quality_reference",
  "status": "pass",
  "elapsed_sec": 1.4090955709980335,
  "uses_numba": true,
  "uses_embree": false
}
```

## Claim Boundary

Goal4301 does not authorize:

- release action,
- package-install wording,
- public speedup wording,
- whole-app acceleration wording,
- broad RT-core wording,
- true-zero-copy wording,
- automatic partner selection,
- paper reproduction claims,
- app-specific native-engine logic.

This is a current internal runtime improvement: the Numba reference path now
keeps score-row generation and top-k ranking on the Numba CUDA side for the
equal-contiguous grouped score-row layout.

## Remaining Work

- This preview top-k path is not yet a broad arbitrary grouped-top-k engine. It
  supports the equal contiguous layout first because that is the layout emitted
  by the current point score-row producer.
- Larger-scale timing should be collected on a stronger NVIDIA pod before any
  performance claim.
- Future work can add a row-offset based variable-length grouped top-k contract
  if another benchmark app needs nonuniform group segments.
