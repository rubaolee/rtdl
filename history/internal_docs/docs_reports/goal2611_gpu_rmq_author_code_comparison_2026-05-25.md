# Goal2611 GPU-RMQ Author-Code Comparison

Date: 2026-05-25

## Purpose

This report records the first direct comparison between the RTDL GPU-RMQ
benchmark app and the authors' public implementation from:

- `https://github.com/lakreis/GPU-RMQ.git`
- commit `86fed1c170b7e41e8ec44e461f7220f87f492893`

The comparison is internal evidence only. It does not authorize public speedup
claims.

## Pod And Build

RunPod endpoint used through Jupyter HTTP:

```text
https://b908xd2jqzcq9o-8888.proxy.runpod.net/lab
```

Environment:

- GPU: NVIDIA RTX PRO 4000 Blackwell.
- Driver: 580.159.04.
- CUDA: 12.8.93.
- OptiX SDK: 8.1.0 installed at `/workspace/optix8`.
- RTDL OptiX library: `/workspace/rtdl_goal2610/build/librtdl_optix.so`.

Author build fixes required:

- Cloned and built documented HRMQ dependency from
  `https://github.com/hferrada/rmq.git`.
- Built `hrmq/rmqrmmBP.a`.
- Reconfigured author CMake with explicit CUDA static library path and
  `-fopenmp` linker flags, because the pod image did not propagate those paths
  into the final C++ link.

These are build-environment fixes, not algorithm changes.

## Workloads

Two author-generated `lr=-3` workloads were used. Both use the authors' saved
input binaries for the array and query set.

| Workload | Values | Queries | Seed | Author check mode |
|---|---:|---:|---:|---|
| small | 65,536 | 8,192 | 27722 | `--randTrivialCheck --save-input-data` |
| medium | 1,048,576 | 65,536 | 27722 | `--randTrivialCheck --save-input-data` |

For the small workload, RTDL was compared directly against the authors' saved
expected result binaries. For the medium workload, the authors saved only the
32K sampled expected rows used by `--randTrivialCheck`, so RTDL correctness was
checked against RTDL's exact CPU oracle over the full 65,536 queries.

Raw evidence:

- `docs/reports/goal2611_gpu_rmq_author_code_comparison_2026-05-25.json`

## Query-Only Timing

Small workload, `n=65,536`, `q=8,192`, `lr=-3`, `log_bs=6`:

| Implementation | Query time | ns/query | Correctness |
|---|---:|---:|---|
| Author full GPU scan, alg 2 | 3.292 ms | 57.416 | pass |
| Author RTXRMQ, alg 5 | 0.079 ms | 1.383 | pass |
| Author GPU-RMQ CL, alg 16 | 0.138 ms | 2.406 | pass |
| Author Interleaved CUDA, alg 19 | 0.144 ms | 2.507 | pass |
| Author vector load, alg 20 | 0.083 ms | 1.448 | pass |
| Author multi-load, alg 24 | 0.077 ms | 1.343 | pass |
| RTDL one-level prepared | 0.588 ms | 71.792 | exact match to author expected |
| RTDL paper-hybrid partner | 2.320 ms | 283.144 | exact match to author expected |

Medium workload, `n=1,048,576`, `q=65,536`, `lr=-3`, `log_bs=6`:

| Implementation | Query time | ns/query | Correctness |
|---|---:|---:|---|
| Author full GPU scan, alg 2 | 3.480 ms | 10.621 | pass |
| Author RTXRMQ, alg 5 | 0.223 ms | 0.681 | pass |
| Author GPU-RMQ CL, alg 16 | 0.126 ms | 0.385 | pass |
| Author Interleaved CUDA, alg 19 | 0.135 ms | 0.413 | pass |
| Author vector load, alg 20 | 0.082 ms | 0.251 | pass |
| Author multi-load, alg 24 | 0.134 ms | 0.410 | pass |
| RTDL one-level prepared | 17.686 ms | 269.870 | exact CPU oracle match |
| RTDL paper-hybrid partner | 36.091 ms | 550.703 | exact CPU oracle match |

## OptiX Author-Code Status

The author OptiX modes did not produce valid timings on this Blackwell pod:

- Alg 18, `Interleaved2`, segfaulted during `RTX Config` after repeated OptiX
  `Invalid value` errors.
- Alg 21, `Interleaved_in_OptiX`, failed the same way.

The logs are preserved on the pod:

- `/tmp/goal2611_alg18_probe.log`
- `/tmp/goal2611_alg21_probe.log`

This means the current direct author-code comparison is against the authors'
CUDA and RTXRMQ modes, not their OptiX RT-core GPU-RMQ modes.

## Conclusion

RTDL correctness is solid on author-generated inputs: both RTDL one-level and
paper-hybrid paths returned the same minima as the author expected files or the
full CPU oracle.

Performance is not close to the author implementation yet. On the medium
workload, the best author CUDA row is about 216x faster than RTDL one-level
prepared and about 440x faster than the RTDL paper-hybrid partner path.

The immediate bottleneck is not RMQ semantics or correctness. It is the current
RTDL runtime boundary: result download, host-side candidate merge/finalization,
and Python/NumPy partner staging dominate the prepared query path. The next
engineering target should be a device-resident partner/finalization path before
claiming GPU-RMQ competitiveness.
