# Goal3316 - Auto Batch Stream Policy For Prepared Point Scalar Counts

Date: 2026-06-04

## Purpose

Goal3314 proved that the generic prepared-point / closed-shape scalar-count batch path benefits from opt-in multi-stream execution on repeated independent requests. Goal3315's Claude review accepted that work with a boundary and flagged one medium issue: the native code already recognized an `auto` stream-count value, but the probe, tests, and report did not validate or document it.

Goal3316 closes that specific review debt by making `auto` reachable from the probe, recording the effective stream count per request row, and measuring the policy on the same RTX A5000 RayJoin PIP slice.

## Auto Policy

`RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT=auto` is still explicit opt-in. The default remains one stream.

The policy is intentionally conservative and based on the Goal3314 sweep:

| Request count | Effective stream count |
| ---: | ---: |
| `< 8` | 1 |
| `8..15` | 4 |
| `16..63` | 8 |
| `>= 64` | 16 |

The policy does not select 32 streams because Goal3314 found no improvement over 16 streams at the tested 64-request size.

## Implementation

- The native helper accepts either a positive integer or `auto` through `RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT`.
- The probe script's `--batch-stream-count` argument now accepts either a positive integer or `auto`.
- The probe records `batch_stream_count_effective` in each batch row so reviewers can verify the selected stream count without reading the C++ policy.

No new native ABI was added, and the native path remains generic.

## Pod Validation

Pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- Commit: `8e28f485ed93da0d467b980e483d382f23000271`
- Build: fresh `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- Runtime library: `/root/rtdl_goal3293/build/librtdl_optix.so`
- Dataset: `/root/rtdl_goal3293/data/rayjoin_public_cdb/br_county_start0_count512.cdb`
- Slice: 512 points, 481 shapes
- Exact scalar count: 1430

The pod ran:

```text
python3 scripts/goal3310_rayjoin_pip_batch_scalar_count_probe.py \
  --dataset /root/rtdl_goal3293/data/rayjoin_public_cdb/br_county_start0_count512.cdb \
  --output /root/goal3316_rayjoin_pip_batch_auto_stream_2026-06-04.json \
  --scalar-count-pipeline \
  --batch-stream-count auto \
  --single-warmup 1 \
  --single-repeat 6 \
  --batch-warmup 2 \
  --batch-repeat 8 \
  --request-counts 1 4 8 16 32 64
```

## Results

| Request count | Effective streams | Per-request median ms | Native per-request median ms | Total median ms | Count |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 0.285530 | 0.261688 | 0.285530 | 1430 |
| 4 | 1 | 0.251194 | 0.245290 | 1.004775 | 1430 |
| 8 | 4 | 0.073424 | 0.070290 | 0.587396 | 1430 |
| 16 | 8 | 0.039792 | 0.038007 | 0.636676 | 1430 |
| 32 | 8 | 0.035896 | 0.034562 | 1.148688 | 1430 |
| 64 | 16 | 0.034279 | 0.033522 | 2.193842 | 1430 |

Against the Goal3314 single-stream 32-request baseline of 0.236400 ms/request, the auto 32-request row is about 6.59x faster.

Against the Goal3314 single-stream 32-request baseline, the auto 64-request row is about 6.90x faster per request.

## Interpretation

`auto` now has code, test, documentation, and pod evidence. It should be treated as the current recommended opt-in policy for repeated independent prepared-point scalar-count batches on this A5000 slice.

The result is still a repeated-query throughput result. It does not replace one-shot RayJoin latency comparisons and does not authorize RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true-zero-copy, or release claims.

The remaining engineering risk from Goal3315 still applies: the stream pool is created and destroyed per batch call. For very small request counts, that overhead can dominate. Goal3316's policy avoids multi-stream execution below 8 requests, but a future persistent stream-pool or prepared batch executor may be needed if applications call this path many times at small-to-medium request counts.

## Claim Boundary

- `release_authorized`: false
- `public_speedup_claim_authorized`: false
- `rt_core_speedup_claim_authorized`: false
- `true_zero_copy_claim_authorized`: false
- `rtdl_beats_rayjoin_claim_authorized`: false
- `rayjoin_paper_reproduction_claim_authorized`: false

