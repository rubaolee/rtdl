# Goal5038 - Device Carrier Concurrent Side Append Result

Date: 2026-07-05

Exit label: `completed_prepared_query_batch_hot_body_62ms__concurrent_side_append_win`

## Purpose

Continue the v2.14.3 RayJoin writer-free binary route attack after Goal5037 stabilized the prepared query-batch route at about 70ms.

The target was the largest remaining downstream phase:

```text
device_resident_carrier_construction_sec ~= 25ms
```

This goal stayed in the RayJoin paper-reproduction app layer. It did not add RTDL core or native RayJoin-specific overlay semantics.

## What Changed

### 1. Concurrent carrier side append

The device-resident binary carrier already used a single-pass atomic append kernel per side. Before this goal, side0 and side1 were launched serially.

This goal adds:

```text
--device-carrier-concurrent-sides
```

When enabled, the two independent side append kernels launch on separate CUDA streams and synchronize before reading the shared atomic counters. The shared `counters` array remains protected by CUDA atomics.

This is valid only for the writer-free binary descriptor route because carrier row order is not a paper-text ordering contract there. The descriptor consumer sorts and aggregates descriptor pairs after carrier construction.

### 2. Direct carrier-prefix descriptor consumer

The native lexsort descriptor consumer now reads the valid prefix of:

```text
carrier["label_a_device"]
carrier["label_b_device"]
carrier["group_length_device"]
```

instead of first copying those columns into new temporary device arrays for the native path.

This is architecture cleanup. It produced only a small consumer-phase effect in the measured route and is not presented as a headline speedup.

## Code And Tests

Modified:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal5034_device_carrier_atomic_append_test.py`

Local verification:

```text
py -3 -m unittest tests.goal5034_device_carrier_atomic_append_test tests.goal5036_prepared_lsi_query_workspace_test

Ran 8 tests in 0.026s
OK
```

POD verification:

```text
python -m unittest tests.goal5034_device_carrier_atomic_append_test tests.goal5036_prepared_lsi_query_workspace_test

Ran 8 tests in 0.003s
OK
```

POD compile check:

```text
python -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

## Measurement Regime

This is not a cold CLI one-shot result and not a paper-text route.

Measured regime:

```text
prepared LSI base session
6 distinct chain-contiguous query batches
prepared query-batch LSI workspaces
device-columnar reprojection/sort
native CUDA/Thrust lexsort
device-resident binary carrier
writer-free descriptor-pair consumer
```

The route excludes paper text writer cost and session preparation cost. It is the prepared query-batch writer-free binary route, not an author-performance parity claim.

## Artifacts

Baseline, same code without concurrent side append:

- `history/internal_docs/rtdl_goal5038_baseline_1_top4.json`
- `history/internal_docs/rtdl_goal5038_baseline_2_top4.json`
- `history/internal_docs/rtdl_goal5038_baseline_3_top4.json`
- `history/internal_docs/rtdl_goal5038_baseline_4_top4.json`
- `history/internal_docs/rtdl_goal5038_baseline_5_top4.json`

Concurrent side append:

- `history/internal_docs/rtdl_goal5038_concurrent_1_top4.json`
- `history/internal_docs/rtdl_goal5038_concurrent_2_top4.json`
- `history/internal_docs/rtdl_goal5038_concurrent_3_top4.json`
- `history/internal_docs/rtdl_goal5038_concurrent_4_top4.json`
- `history/internal_docs/rtdl_goal5038_concurrent_5_top4.json`

Final route, concurrent side append plus direct carrier-prefix descriptor consumer:

- `history/internal_docs/rtdl_goal5038_final_direct_concurrent_1_top4.json`
- `history/internal_docs/rtdl_goal5038_final_direct_concurrent_2_top4.json`
- `history/internal_docs/rtdl_goal5038_final_direct_concurrent_3_top4.json`
- `history/internal_docs/rtdl_goal5038_final_direct_concurrent_4_top4.json`
- `history/internal_docs/rtdl_goal5038_final_direct_concurrent_5_top4.json`

## Structural Anchors

All measured artifact groups preserved the same structural anchors:

```text
lsi_row_counts:
[21424, 56228, 66414, 67840, 88490, 127926]

descriptor_pair_counts:
[2756, 2873, 2987, 3058, 4723, 6316]
```

The final route reports:

```text
downstream_consumer_native_lexsort_direct_carrier_prefix = true
```

## Performance Result

All numbers below are median-of-medians across five independent process runs. Each process measures the six query batches.

| Route | hot body | downstream floor | LSI phase | carrier construction | descriptor consumer |
|---|---:|---:|---:|---:|---:|
| Goal5037 old stable native lexsort | 0.070311s | 0.068286s | 0.001870s | 0.024918s | 0.011388s |
| Goal5038 same-code serial baseline | 0.070743s | 0.068698s | 0.001954s | 0.025343s | 0.011947s |
| Goal5038 concurrent side append | 0.061454s | 0.059483s | 0.001921s | 0.018672s | 0.011552s |
| Goal5038 final direct+concurrent | 0.062045s | 0.060060s | 0.002038s | 0.017564s | 0.011262s |

The final route improves over the Goal5037 stable baseline:

```text
hot body:             0.070311s -> 0.062045s  = 1.13x
downstream floor:     0.068286s -> 0.060060s  = 1.14x
carrier construction: 0.024918s -> 0.017564s  = 1.42x
descriptor consumer:  0.011388s -> 0.011262s  = 1.01x
```

The largest useful change is concurrent side append. Direct carrier-prefix consumption is kept as architecture cleanup, but it is not a meaningful hot-body speedup by itself.

## Interpretation

This goal did move the prepared query-batch hot body:

```text
~70ms -> ~62ms
```

That is a real but bounded improvement. It does not solve cold CLI startup, paper text output, or full author parity.

The remaining prepared query-batch hot-body floor is now roughly:

```text
carrier construction: ~17.6ms
vertex PIP:           ~17.7ms combined
descriptor consumer:  ~11.3ms
sort/reprojection:    ~8.0ms combined
LSI phase:            ~2.0ms
```

## Claim Boundary

Authorized:

- prepared query-batch writer-free binary route improved from about 70ms to about 62ms;
- concurrent side append is a valid app-layer binary-route optimization;
- structural anchors stayed stable;
- no paper text writer, no author parity, no cold CLI claim.

Not authorized:

- no claim that v2.14.3 paper-text Section 5.7 now runs in 62ms;
- no claim that cold one-shot CLI performance is 62ms;
- no claim that the route beats or matches the author program;
- no claim that a RayJoin-specific RTDL core primitive was added.

## Next Target

The next largest honest hot-body targets are:

1. vertex PIP map1/map0 combined, about 17-18ms;
2. remaining carrier construction, about 17-18ms;
3. descriptor consumer, about 11ms.

The carrier win was useful, but the remaining floor is now split. Further progress should attack either PIP query batching/prepared points or the descriptor consumer only if the expected win is at least several milliseconds.
