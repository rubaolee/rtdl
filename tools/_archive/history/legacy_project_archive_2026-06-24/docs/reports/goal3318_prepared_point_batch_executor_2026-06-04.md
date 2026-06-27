# Goal3318 - Reusable Prepared Point Batch Count Executor

Date: 2026-06-04

## Purpose

Goal3314 added opt-in multi-stream batching for repeated prepared point / closed-shape scalar-count requests. Goal3315's Claude review accepted it with a boundary and noted that CUDA streams were created and destroyed on every batch call. Goal3316 validated the explicit `auto` stream policy.

Goal3318 adds a reusable generic batch-count executor to reduce per-call setup overhead. The executor owns:

- the selected CUDA stream pool;
- the device count buffer;
- the device launch-parameter buffer;
- pre-uploaded per-request launch parameters.

Each executor `run()` only clears the count slots, launches the prepared requests, synchronizes the owned streams, and downloads the count slots.

## API Shape

Native C ABI:

- `rtdl_optix_prepare_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d`
- `rtdl_optix_run_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d`
- `rtdl_optix_destroy_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d`

Python:

```python
with prepared.prepare_device_filtered_prepared_points_batch_executor(
    prepared_points,
    request_count,
    stream_count="auto",
) as executor:
    counts = executor.run()
```

This is a generic prepared point / closed-shape membership count executor. It contains no RayJoin-specific native logic.

## Pod Validation

Pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- Commit: `c037f510b89a2effd4eff32d025da1a3c053a0b1`
- Build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- Runtime library: `/root/rtdl_goal3293/build/librtdl_optix.so`
- Dataset: `/root/rtdl_goal3293/data/rayjoin_public_cdb/br_county_start0_count512.cdb`
- Slice: 512 points, 481 shapes
- Exact scalar count: 1430

Pod tests passed:

```text
python3 -m unittest \
  tests.goal3318_prepared_point_batch_executor_surface_test \
  tests.goal3316_auto_batch_stream_policy_test \
  tests.goal3314_prepared_point_multistream_batch_count_test \
  tests.goal3310_prepared_point_batch_scalar_count_test
```

The pod probe ran:

```text
python3 scripts/goal3310_rayjoin_pip_batch_scalar_count_probe.py \
  --dataset /root/rtdl_goal3293/data/rayjoin_public_cdb/br_county_start0_count512.cdb \
  --output /root/goal3318_rayjoin_pip_batch_executor_auto_stream_2026-06-04.json \
  --scalar-count-pipeline \
  --batch-stream-count auto \
  --batch-executor \
  --single-warmup 1 \
  --single-repeat 6 \
  --batch-warmup 2 \
  --batch-repeat 12 \
  --request-counts 1 4 8 16 32 64
```

## Results

| Request count | Effective streams | Executor per-request median ms | Native per-request median ms | Total median ms | Count |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 0.274909 | 0.261826 | 0.274909 | 1430 |
| 4 | 1 | 0.250228 | 0.246507 | 1.000910 | 1430 |
| 8 | 4 | 0.070683 | 0.068824 | 0.565461 | 1430 |
| 16 | 8 | 0.038350 | 0.037145 | 0.613599 | 1430 |
| 32 | 8 | 0.034875 | 0.034211 | 1.116015 | 1430 |
| 64 | 16 | 0.033171 | 0.032713 | 2.122968 | 1430 |

Compared with Goal3316's non-executor auto path:

| Request count | Goal3316 auto ms/request | Goal3318 executor ms/request | Ratio |
| ---: | ---: | ---: | ---: |
| 8 | 0.073424 | 0.070683 | 1.039x |
| 16 | 0.039792 | 0.038350 | 1.038x |
| 32 | 0.035896 | 0.034875 | 1.029x |
| 64 | 0.034279 | 0.033171 | 1.033x |

Compared with the Goal3314 single-stream 32-request baseline of 0.236400 ms/request, the executor 32-request row is about 6.78x faster per request. The executor 64-request row is about 7.13x faster per request than that same single-stream baseline.

## Interpretation

Goal3318 is a useful runtime cleanup and a modest throughput improvement. It removes per-repeat stream creation/destruction and per-repeat launch-parameter upload from the measured executor run path.

The improvement is modest because the dominant remaining cost is the RT traversal/count pass itself. This is still good engineering: it turns a benchmark-only env knob into a reusable Python+RTDL API that users can hold across repeated requests.

The next substantial performance leap is unlikely to come from more host-side batching. It likely requires a more compact generic closed-shape predicate-count primitive, prepared boundary/range acceleration, or a same-contract comparison against a true batched RayJoin baseline.

## Claim Boundary

- `release_authorized`: false
- `public_speedup_claim_authorized`: false
- `rt_core_speedup_claim_authorized`: false
- `true_zero_copy_claim_authorized`: false
- `rtdl_beats_rayjoin_claim_authorized`: false
- `rayjoin_paper_reproduction_claim_authorized`: false

