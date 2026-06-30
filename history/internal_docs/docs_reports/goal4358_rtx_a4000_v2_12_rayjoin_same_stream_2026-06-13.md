# Goal4358 RTX A4000 v2.12 RayJoin Same-Stream Packet

Date: 2026-06-13

Status: v2.12 RayJoin same-stream evidence packet is complete for LSI and PIP scalar-count contracts. This is a serious RTDL RT-core-vs-Embree CPU comparison for these RayJoin-exported streams, plus a comparison against the original RayJoin `query_exec` RT logs. It is not a broad all-benchmark-app public speedup claim.

## Artifacts

| Item | Value |
| --- | --- |
| RTDL commit | `7dc94cf7c5e42b6c8f8d6a4850a94ec9ee559327` |
| Pod | `157.157.221.29:20049` |
| GPU | `NVIDIA RTX A4000, driver 580.126.20, compute capability 8.6` |
| CPU | `AMD EPYC 7702`, 128 hardware threads visible |
| OptiX headers | `/root/vendor/optix-sdk-v8` |
| Embree | `4.3.0` |
| Summary JSON | `docs/reports/goal4358_rtx_a4000_v2_12_rayjoin_same_stream_2026-06-13/summary.json` |
| Summary Markdown | `docs/reports/goal4358_rtx_a4000_v2_12_rayjoin_same_stream_2026-06-13/summary.md` |

## Direct RTDL Hardware Comparison

Both RTDL backends consumed the same RayJoin-exported query stream and returned scalar counts without materializing rows. Higher OptiX-over-Embree speedup means NVIDIA RT-core hardware won over the Embree CPU path for the same RTDL contract.

| Workload | Contract | Count | OptiX RT hot median ms | Embree CPU hot median ms | OptiX faster than Embree | Reasonable? |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| LSI | exact prepared segment-pair scalar count | 8,921 | 0.336 | 14.539 | 43.28x | Yes. This is the clean RT-core acceleration row: the OptiX route performs prepared-left direct segment-pair counting on RTX hardware, while Embree uses CPU traversal plus endpoint supplementation. The counts match exactly. |
| PIP | exact closed-shape membership count with prepared points | 8,686 | 12.034 | 14.168 | 1.18x | Yes, but small. RT cores accelerate candidate generation, but RTDL still spends material time in exact membership/refinement and generic front-door orchestration. The counts match exactly. |

The old Embree LSI result was not a fair CPU baseline. Before commit `7dc94cf7`, sparse zero-hit LSI queries fell back to scanning every static segment, making the 100k x 326k stream effectively O(N*M). The fixed Embree LSI hot median improved from 141,939.613 ms to 14.539 ms, a 9,762.83x repair, with the same 8,921 count.

## Original RayJoin RT Comparison

The next table uses RayJoin's original RT `Query` time as the denominator. Values above 1 in the speedup column mean RTDL is faster than RayJoin RT on the same stream; values below 1 mean RayJoin RT is faster.

| Workload | Backend | RayJoin RT query ms | RTDL hot query ms | RayJoin RT / RTDL | Readout |
| --- | --- | ---: | ---: | ---: | --- |
| LSI | RTDL OptiX | 0.819 | 0.336 | 2.44x | RTDL OptiX is faster than RayJoin RT for this scalar-count contract. |
| LSI | RTDL Embree | 0.819 | 14.539 | 0.056x | RayJoin RT is 17.76x faster than Embree CPU. |
| PIP | RTDL OptiX | 0.830 | 12.034 | 0.069x | RayJoin RT is 14.49x faster than RTDL OptiX. |
| PIP | RTDL Embree | 0.830 | 14.168 | 0.059x | RayJoin RT is 17.07x faster than Embree CPU. |

## Interpretation

LSI is the strong RTDL RT-core result. The observed 43.28x OptiX-over-Embree CPU speedup is consistent with the hardware and algorithm: the query is a large sparse segment-pair intersection count, the output is a scalar, and the RT-core path avoids CPU traversal and row materialization.

PIP is not a strong RTDL RT-core speedup row yet. The measured 1.18x OptiX-over-Embree CPU speedup is still reasonable because exact membership dominates the current RTDL contract. In the measured OptiX PIP repeats, candidate write was about 1.83 ms median, candidate download about 0.024 ms, exact host refinement about 4.93 ms, and the whole hot front door was about 12.03 ms. RayJoin's specialized RT PIP implementation remains much faster at 0.830 ms query time.

The public wording should say: RTDL v2.12 has a ready-to-use high-performance NVIDIA RT-core path and a ready-to-use optimized Embree CPU path for these RayJoin LSI/PIP scalar-count contracts, and LSI shows a clear RT-core advantage. It should not say that RTDL beats RayJoin overall, or that RT cores broadly accelerate every benchmark app, from this packet alone.

## Validation

Focused pod tests passed after the Embree LSI fix:

```text
python3 -m unittest \
  tests.goal4356_rayjoin_pip_exact_prepared_points_count_surface_test \
  tests.goal4357_rayjoin_goal4354_exact_prepared_points_runner_test \
  tests.goal4352_embree_spatial_rayjoin_count_surface_test \
  tests.goal709_embree_threading_contract_test \
  tests.goal710_embree_parallel_point_query_test

Ran 21 tests in 0.083s
OK
```

The packet preserves conservative claim boundaries in `summary.json`: same RayJoin-exported query stream, scalar-count hot query phase, no Python row materialization in the RTDL measured path, and no paper-wide reproduction or whole-application speedup claim.
