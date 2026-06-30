# Goal2292: Current Prepared RayJoin-Style Comparison

Status: accepted with Goal2294 2-AI consensus.

## Purpose

Goal2252 preserved an honest current comparison after the first prepared
closed-shape membership path, but its LSI row still used the older compiled RTDL
kernel route. After Goal2287 and Goal2291, the current v2 learner route for
repeated LSI calls is prepared segment-pair intersection with a prepacked
left/query batch.

Goal2292 refreshes the comparison so the project is no longer reading stale LSI
numbers while deciding the next RayJoin-style optimization.

## Environment

- Pod SSH: `root@69.30.85.202 -p 22064`
- Commit: `38399f3b847b6af7c3ccbbf9b1c290d1d8b7b090`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- OptiX SDK: `/root/vendor/optix-sdk`
- CUDA prefix: `/usr/local/cuda-12.8`
- LSI stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_lsi_gen100000_stream.json`
- PIP stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_pip_gen100000_stream.json`
- Warmups/repeats: 2 warmups, 11 timed repeats per row

## Current Results

Artifact:
`docs/reports/goal2292_rayjoin_current_prepared_comparison_pod_2026-05-17.json`

| Workload | Current v2 Route | Queries | Expected Rows | Row/Count Parity | Median Rows (s) | Median Count (s) |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| LSI | prepared segment-pair + prepacked left/query batch | 100,000 | 8,921 | true | 0.010591023 | 0.010393109 |
| PIP | prepared closed-shape membership + prepacked points | 100,000 | 8,686 | true | 0.052356653 | 0.039025227 |

One-time preparation costs are outside the repeated-call medians but recorded
for honesty:

| Workload | One-Time Query Pack (s) | Static Scene Pack/Prepare (s) |
| --- | ---: | ---: |
| LSI | 0.282903 | 1.659662 prepared right scene |
| PIP | 0.246674 point pack | 0.236784 shape pack + 0.405520 prepared shape scene |

## Comparison With Goal2252

Goal2252's LSI route was the older `compiled_rtdl_kernel` path and measured
`0.083592888s`. Goal2292's current packed-left LSI raw row median is
`0.010591023s`, about `7.89x` faster than that stale route. The current scalar
count path is about `8.04x` faster than the stale Goal2252 LSI route.

Goal2252's PIP prepared row-return median was `0.063292889s`. Goal2292's current
PIP row-return median is `0.052356653s`, about `1.21x` faster. The current PIP
scalar count median is `0.039025227s`, about `1.62x` faster than Goal2252's
row-return median.

## Interpretation

The current v2 learner story is stronger than the older comparison suggested:

- LSI is no longer the slow RayJoin-style row in the RTDL learner harness once
  the user follows the packed-input contract.
- PIP still costs more than LSI because it traverses closed-shape boundary
  segments and performs exact membership counting, but scalar count avoids final
  row materialization and is the better route when a count is enough.
- The next RayJoin-style performance fight should focus on device-resident
  continuation/output streams or a stronger generic closed-shape membership
  primitive, not on the old LSI compiled-kernel route.

## Boundary

This report does not authorize:

- full RayJoin reproduction,
- a claim that RTDL beats RayJoin,
- paper-scale RayJoin speedup claims,
- broad LSI or PIP speedup claims,
- whole-application speedup,
- true zero-copy,
- or v2.0 release readiness.

The accepted claim is only that, on this RTX A5000 pod and these two
RayJoin-exported 100k streams, the current prepared v2 learner routes are much
faster than the stale Goal2252 LSI route and preserve the prior CPU-verified row
counts.
