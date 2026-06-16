# Goal4445 / V3.0 M49 DBSCAN Compact Component Signature

Status: `accept-with-boundary`

M49 closes the DBSCAN app's most visible V3 output debt from Goal4420. The RTDL/OptiX grouped-stream component-label path was already fast, but the app still paid Python cost to materialize one row per point. M49 adds `output_mode="component_signature"` for the same generic fixed-radius graph component front door, so an app that only needs a cluster-size/noise/core summary can consume compact partner aggregates instead of full Python cluster rows.

This remains an app plus partner continuation path. It is not a DBSCAN-specific native engine ABI, not automatic partner selection, and not a broad public DBSCAN speedup claim.

## What Changed

| Piece | Result |
|---|---|
| App backend | `optix_grouped_stream_components` now supports `output_mode="full"` and `output_mode="component_signature"`. |
| RTDL primitive | Unchanged: `prepare_v2_8_fixed_radius_graph_component_continuation_3d` plus `fixed_radius_graph_component_labels_3d_v2_8`. |
| Partners | CuPy uses device `unique` aggregation. Numba uses the Numba device columns through CuPy's CUDA array interface when available, with a compact host NumPy fallback only if that bridge is unavailable. |
| Output | Full mode still emits per-point Python cluster rows. Component-signature mode emits `point_count`, `cluster_count`, `clustered_point_count`, `noise_count`, `core_count`, size histogram, and min/max cluster size. |
| Claim boundary | App-specific DBSCAN fixture/oracle logic stays in the app layer; the engine primitive stays app-agnostic. |

## Evidence

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20 GB.

Artifacts:

```text
docs/reports/goal4445_v3_0_m49_dbscan_full_rows_65536_warm_2026-06-16.json
docs/reports/goal4445_v3_0_m49_dbscan_component_signature_65536_warm_2026-06-16.json
docs/reports/goal4445_v3_0_m49_dbscan_full_rows_524288_warm_2026-06-16.json
docs/reports/goal4445_v3_0_m49_dbscan_component_signature_524288_warm_2026-06-16.json
docs/reports/goal4445_v3_0_m49_dbscan_full_rows_2097152_2026-06-16.json
docs/reports/goal4445_v3_0_m49_dbscan_component_signature_2097152_warm_2026-06-16.json
```

All measured rows passed:

```text
all_match_oracle: true
cluster_size_signatures_match: true
core_counts_match: true
noise_counts_match: true
native_continuation_active: true
rt_core_accelerated: true
public_claim_authorized: false
```

## Timings

The table separates the prepared hot component-label kernel from the post-window consumer. `row` is full Python row materialization. `sig` is compact component-signature aggregation.

| Points | Partner | Mode | Prepare | Hot component-label median | Post-window consumer | Consumer backend | Python cluster rows |
|---:|---|---|---:|---:|---:|---|---:|
| 65,536 | CuPy | full rows | 0.146704s | 0.000355s | row 0.095707s | Python rows | 65,536 |
| 65,536 | CuPy | component signature | 0.156403s | 0.000355s | sig 0.001534s | `cupy_device_unique` | 0 |
| 65,536 | Numba | full rows | 0.185532s | 0.000459s | row 0.097527s | Python rows | 65,536 |
| 65,536 | Numba | component signature | 0.183995s | 0.000467s | sig 0.001681s | `numba_device_columns_via_cupy_cuda_array_interface` | 0 |
| 524,288 | CuPy | full rows | 1.341038s | 0.000564s | row 0.768489s | Python rows | 524,288 |
| 524,288 | CuPy | component signature | 1.351923s | 0.000652s | sig 0.002044s | `cupy_device_unique` | 0 |
| 524,288 | Numba | full rows | 1.423546s | 0.000665s | row 0.771055s | Python rows | 524,288 |
| 524,288 | Numba | component signature | 1.376463s | 0.000657s | sig 0.001772s | `numba_device_columns_via_cupy_cuda_array_interface` | 0 |
| 2,097,152 | CuPy | full rows | 5.713194s | 0.001408s | row 3.041865s | Python rows | 2,097,152 |
| 2,097,152 | CuPy | component signature | 4.818098s | 0.001390s | sig 0.001838s | `cupy_device_unique` | 0 |
| 2,097,152 | Numba | full rows | 5.367940s | 0.001497s | row 3.067937s | Python rows | 2,097,152 |
| 2,097,152 | Numba | component signature | 4.733575s | 0.001485s | sig 0.001973s | `numba_device_columns_via_cupy_cuda_array_interface` | 0 |

The 2,097,152-point full-row file used `app_call_warmups=0` to avoid repeating multi-million-row Python materialization. The corresponding component-signature file used `app_call_warmups=1` to remove one-time CuPy aggregation compilation from the steady consumer timing. The 65,536 and 524,288 warm files used the same `app_call_warmups=1` setting on both modes.

## Ratios

| Points | Partner | Row consumer / signature consumer | Full hot+consumer / signature hot+consumer | Prepare-included ratio |
|---:|---|---:|---:|---:|
| 65,536 | CuPy | 62.4x | 50.8x | 1.53x |
| 65,536 | Numba | 58.0x | 45.6x | 1.52x |
| 524,288 | CuPy | 375.9x | 285.2x | 1.56x |
| 524,288 | Numba | 435.2x | 317.8x | 1.59x |
| 2,097,152 | CuPy | 1654.7x | 942.6x | 1.82x* |
| 2,097,152 | Numba | 1554.8x | 887.7x | 1.78x* |

`*` The 2,097,152-point prepare-included ratios mix full-row no app-call warmup with signature one-call warmup, so use them as scale intuition only. The consumer and hot+consumer ratios are the cleaner M49 evidence.

## Interpretation

M49 changes the DBSCAN lesson materially. Before this milestone, the RT component-label hot path was already sub-millisecond at 65K and 524K, but the user-visible full output path paid roughly 0.1s to 0.8s to materialize Python rows. At 2.1M points, that full-row consumer cost reached roughly 3.05s while the hot RT component-label work stayed around 1.4-1.5ms.

The compact signature path removes that Python row requirement when the app only needs the cluster-size/noise/core summary. On the same fixture and the same grouped-stream primitive, the post-window consumer drops to roughly 1.5-2.0ms across the measured scales. That is the right V3 design shape: generic RTDL primitive first, explicit partner continuation for app-specific summary consumption, no C++/CUDA user kernel requirement, and no hidden DBSCAN-native engine.

CuPy and Numba are both viable here. CuPy is the direct CUDA array partner; Numba is the Python-source/no-C++ reference, and its device columns are consumed through CuPy's CUDA array interface for the compact aggregation in these pod runs. Neither partner should be auto-selected by RTDL from this evidence.

## Allowed Wording

The current DBSCAN app can use a generic RTDL/OptiX fixed-radius graph component primitive plus explicit CuPy or Numba partner continuation to return a compact component signature without materializing one Python row per point. On the RTX 4000 Ada pod, this removes the dominant post-window row-materialization cost on the tiled DBSCAN fixture while preserving oracle parity.

## Forbidden Wording

Do not claim broad DBSCAN acceleration, automatic partner optimization, true zero-copy, a DBSCAN-specific native engine ABI, or arbitrary RT-core superiority from M49. If a user needs every per-point cluster row in Python, the full-row output mode remains the correct but slower contract.
