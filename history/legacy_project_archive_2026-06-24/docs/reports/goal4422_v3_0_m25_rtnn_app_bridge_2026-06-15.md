# Goal4422 / V3.0 M25 RTNN app-level ranked-summary bridge

Status: `accept-with-boundary`

M25 promotes the M19 RTNN ranked-summary graph bridge into the current RTNN benchmark app. The new app mode is `prepared_ranked_summary_graph_partner_bridge`: users can now enter through `examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py` and run the same app-agnostic prepared OptiX ranked-summary graph with explicit CuPy and Numba same-stream partner reductions.

This is an internal V3 integration step, not a public speedup claim.

## What Changed

| Piece | Result |
|---|---|
| App mode | `prepared_ranked_summary_graph_partner_bridge` in the current RTNN benchmark app. |
| RTDL primitive | Reuses `run_v3_m19_ranked_summary_bridge_case`, which prepares the generic 3D fixed-radius ranked-summary graph. |
| Partners | CuPy and Numba, both run from the same prepared graph and validated through the same signature. |
| Hot window | Native graph replay plus same-stream partner device reduction; aggregate materialization happens after the hot measured window. |
| Batch shape | Search-set size and prepared query-batch size are now explicit, so larger resident search scenes can be measured with the current `query_count <= 65536` graph capacity. |
| Boundary | This is not an RTNN-specific native engine ABI, full RTNN paper reproduction, public speedup claim, automatic partner selection, or true-zero-copy public claim. |

## Pod Evidence

Artifacts:

```text
docs/reports/goal4422_v3_0_m25_rtnn_app_bridge_uniform_65536_2026-06-15.json
docs/reports/goal4422_v3_0_m25_rtnn_app_bridge_uniform_262144q65536_2026-06-15.json
```

Hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20 GB.

Commands:

```bash
python scripts/v3_0_m25_rtnn_app_bridge_measure.py \
  --point-count 65536 \
  --query-count 65536 \
  --distribution uniform \
  --warmups 2 \
  --repeats 5 \
  --numba-cuda-home /tmp/rtdl_cuda124_home \
  --output docs/reports/goal4422_v3_0_m25_rtnn_app_bridge_uniform_65536_2026-06-15.json

python scripts/v3_0_m25_rtnn_app_bridge_measure.py \
  --point-count 262144 \
  --query-count 65536 \
  --distribution uniform \
  --warmups 1 \
  --repeats 3 \
  --numba-cuda-home /tmp/rtdl_cuda124_home \
  --output docs/reports/goal4422_v3_0_m25_rtnn_app_bridge_uniform_262144q65536_2026-06-15.json
```

| Search points | Query batch | Partner | Hot device median | Materialize median | Signature | Hot copy gate |
|---:|---:|---|---:|---:|---|---|
| 65,536 | 65,536 | CuPy | 0.000605s | 0.0000468s | matched | passed |
| 65,536 | 65,536 | Numba | 0.000632s | 0.0000838s | matched | passed |
| 262,144 | 65,536 | CuPy | 0.001164s | 0.0000510s | matched | passed |
| 262,144 | 65,536 | Numba | 0.001161s | 0.0000880s | matched | passed |

Both artifacts passed:

```text
signature_match: true
hot_no_hidden_column_copy_ready: true
device_result_materialization_after_hot_window: true
cuda_graph_replay_used: true
same_stream_partner_device_reduction_used: true
public_claim_authorized: false
```

## Interpretation

M19 already proved the runtime bridge. M25 closes the app-surface gap: the current RTNN benchmark app now exposes that bridge directly, so RTNN users do not have to know which historical goal script contains the optimized route.

The key architectural claim remains narrow: RTDL can keep the prepared ranked-summary graph output on device, run bounded same-stream partner reductions in CuPy and Numba, and defer materialization until after the hot window. It does not prove whole-app RTNN paper parity or public RT-core speedup.

The attempted 262,144-point self-query exposed the current prepared graph capacity limit: `query_count <= 65536`. M25 resolves that at the app contract level by making query batching explicit. The second artifact therefore uses 262,144 resident search points with a 65,536-query batch, which is the correct RTNN-style prepared-scene usage pattern for the current graph implementation.

## Allowed Wording

The current RTNN benchmark app exposes an internal V3 route that uses the generic prepared OptiX ranked-summary graph and explicit CuPy/Numba same-stream partner reductions.

## Forbidden Wording

Do not claim public speedup, full RTNN paper reproduction, RTDL-beats-RTNN, broad RT-core superiority, end-to-end zero-copy, automatic partner selection, or an RTNN-specific native engine implementation from this milestone.
