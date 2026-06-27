# Goal3314 - Multi-Stream Prepared Point Batch Scalar Count Evidence

Date: 2026-06-04

## Purpose

Goal3310 added a generic prepared-point batch scalar-count surface for repeated closed-shape membership/count requests. Goal3311's Claude review accepted the surface with a boundary, but correctly flagged that the initial implementation queued all batch requests on the null stream, limiting overlap.

Goal3314 tests the next narrow engineering step: an opt-in stream pool for the existing generic batch count path. This is a repeated-query throughput probe, not a one-shot RayJoin latency comparison.

## Implementation

The native OptiX batch-count path now honors:

```text
RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT
```

When the value is greater than one, the generic prepared-point / closed-shape scalar-count batch path creates a small CUDA stream pool and assigns each independent request to `request_index % stream_count`. The default remains one stream, preserving the Goal3310 behavior unless the user or benchmark explicitly opts in.

No app-specific native API was added. The path remains generic:

- prepared point columns
- prepared closed-shape membership
- scalar count output
- repeated independent request batch

The RayJoin PIP probe script now exposes `--batch-stream-count` and records the selected count in the artifact.

## Validation

Pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- Commit: `0cfc510d19c3026eef8cf409d29ecaa4eabe8d6b`
- Build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- Runtime library: `/root/rtdl_goal3293/build/librtdl_optix.so`
- Dataset: `/root/rtdl_goal3293/data/rayjoin_public_cdb/br_county_start0_count512.cdb`
- Slice: 512 points, 481 shapes
- Exact scalar count: 1430

Pod validation passed:

```text
python3 -m unittest \
  tests.goal3314_prepared_point_multistream_batch_count_test \
  tests.goal3312_prepared_point_batch_graph_count_test \
  tests.goal3310_prepared_point_batch_scalar_count_test
```

The stream sweep artifacts all report exact first and last counts of 1430, and all claim-boundary flags remain false.

## Results

| Stream count | Request count | Per-request median ms | Native per-request median ms | Total median ms | Count |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 8 | 0.247338 | 0.243547 | 1.978705 | 1430 |
| 1 | 16 | 0.243664 | 0.241759 | 3.898622 | 1430 |
| 1 | 32 | 0.236400 | 0.235201 | 7.564785 | 1430 |
| 2 | 8 | 0.131361 | 0.127213 | 1.050889 | 1430 |
| 2 | 16 | 0.125156 | 0.122594 | 2.002498 | 1430 |
| 2 | 32 | 0.123923 | 0.122697 | 3.965526 | 1430 |
| 4 | 8 | 0.077603 | 0.073554 | 0.620825 | 1430 |
| 4 | 16 | 0.069881 | 0.068398 | 1.118093 | 1430 |
| 4 | 32 | 0.065747 | 0.064778 | 2.103899 | 1430 |
| 8 | 8 | 0.057266 | 0.053226 | 0.458131 | 1430 |
| 8 | 16 | 0.040770 | 0.038677 | 0.652325 | 1430 |
| 8 | 32 | 0.036487 | 0.034991 | 1.167582 | 1430 |
| 16 | 16 | 0.043571 | 0.041619 | 0.697141 | 1430 |
| 16 | 32 | 0.037426 | 0.035884 | 1.197620 | 1430 |
| 16 | 64 | 0.034520 | 0.033654 | 2.209300 | 1430 |
| 32 | 16 | 0.044333 | 0.042727 | 0.709325 | 1430 |
| 32 | 32 | 0.039772 | 0.038683 | 1.272696 | 1430 |
| 32 | 64 | 0.036074 | 0.035132 | 2.308736 | 1430 |

Compared with the single-stream 32-request row, the 8-stream 32-request row improves per-request median time from 0.236400 ms to 0.036487 ms, or about 6.48x.

The best measured row in this sweep is 16 streams with 64 requests, at 0.034520 ms per request, about 6.85x faster than the single-stream 32-request row.

## Interpretation

This is a real throughput improvement for repeated independent prepared-point scalar-count requests. It directly addresses the Goal3311 null-stream serialization concern.

It does not prove a one-shot RayJoin speedup, a RayJoin paper reproduction, a broad RT-core speedup, or a release claim. The benchmark shape is still a repeated-query throughput contract: prepare the shape and point inputs once, then issue many independent scalar-count requests.

The next useful engineering targets are:

- choose an adaptive default stream count for sufficiently large repeated-request batches;
- compare this repeated-query throughput contract against any equivalent batched RayJoin baseline if one is exposed;
- continue investigating the Goal3312 CUDA graph replay mismatch separately, because the graph path remains fail-closed negative evidence.

## Claim Boundary

- `release_authorized`: false
- `public_speedup_claim_authorized`: false
- `rt_core_speedup_claim_authorized`: false
- `true_zero_copy_claim_authorized`: false
- `rtdl_beats_rayjoin_claim_authorized`: false
- `rayjoin_paper_reproduction_claim_authorized`: false
