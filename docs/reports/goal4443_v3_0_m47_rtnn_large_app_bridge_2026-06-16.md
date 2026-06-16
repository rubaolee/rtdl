# Goal4443 / V3.0 M47 RTNN Large App-Front-Door Bridge

Status: `accept-with-boundary`

M47 extends the current RTNN benchmark app evidence from the M25 bridge to a
large resident search scene. The measured route is still app-agnostic: RTDL
prepares a generic 3-D fixed-radius ranked-summary graph, replays it, and then
runs explicit same-stream CuPy and Numba partner reductions before
materializing compact results.

This is internal V3 evidence, not full RTNN paper reproduction and not a public
ANN-index speedup claim.

## Pod Run

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20 GB.

Artifact:

```text
docs/reports/goal4443_v3_0_m47_rtnn_app_bridge_uniform_1048576q65536_r1000_2026-06-16.json
```

Command:

```bash
PYTHONPATH=src:. python3 scripts/v3_0_m25_rtnn_app_bridge_measure.py \
  --point-count 1048576 \
  --query-count 65536 \
  --distribution uniform \
  --warmups 2 \
  --repeats 1000 \
  --numba-cuda-home /usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc \
  --output docs/reports/goal4443_v3_0_m47_rtnn_app_bridge_uniform_1048576q65536_r1000_2026-06-16.json
```

## Result

| Resident search points | Query batch | Partner | Hot median per batch | 1000-repeat hot total | Estimated 1M-query total by 16 batches | Signature | Hot copy gate |
| ---: | ---: | --- | ---: | ---: | ---: | --- | --- |
| 1,048,576 | 65,536 | CuPy | `0.004988s` | `4.988s` | `0.079810s` | matched | passed |
| 1,048,576 | 65,536 | Numba | `0.005020s` | `5.020s` | `0.080313s` | matched | passed |

Both partner rows record:

- `signature_match: true`
- `hot_no_hidden_column_copy_ready: true`
- `device_result_materialization_after_hot_window: true`
- `cuda_graph_replay_used: true`
- `same_stream_partner_device_reduction_used: true`
- `public_claim_authorized: false`

## Comparison Reading

Use the same query granularity when reading the speedups. M47 measures a
65,536-query batch against a 1,048,576-point resident search scene. A full
1,048,576-query pass is therefore estimated as 16 batches.

Compared with the Goal4381 exact float64 Embree aggregate row for the same
1,048,576-point uniform fixture:

- Embree exact aggregate full 1M-query median: `1.512707s`
- M47 CuPy graph bridge estimated 1M-query total: `0.079810s`, or `18.95x`
  faster than Embree
- M47 Numba graph bridge estimated 1M-query total: `0.080313s`, or `18.84x`
  faster than Embree

Compared with the Goal4381 exact float64 OptiX aggregate row:

- OptiX exact aggregate full 1M-query median: `0.149152s`
- M47 CuPy graph bridge estimated 1M-query total: `1.87x` faster
- M47 Numba graph bridge estimated 1M-query total: `1.86x` faster

This comparison is useful but not an exactness-equivalent speedup claim: the
Goal4381 exact aggregate rows are float64, while the graph-bridge row is the
resident float32 app bridge. Keep those contracts separate in public wording.

Goal4381's older best graph-runner row remains the fastest measured specialized
uniform 1M route in this evidence family. M47's contribution is different: it
proves the current RTNN app front door itself can run the large resident
graph-bridge contract with both CuPy and Numba visible and second-level hot
evidence.

## Route Decision

RTNN is now a mixed explicit route:

- choose exact native aggregate rows for same-contract float64
  OptiX-vs-Embree comparison;
- choose `prepared_ranked_summary_graph_partner_bridge` for resident graph
  replay plus same-stream CuPy/Numba app-bridge evidence;
- keep official RTNN authors-code rows diagnostic until output-contract
  equivalence is proven.

## Forbidden Wording

Do not claim full RTNN paper reproduction, RTDL beats the RTNN authors' code,
arbitrary ANN-index speedup, automatic exact-vs-float32 route selection,
public zero-copy, or broad RT-core superiority from this milestone.
