# Goal5033 Native Descriptor Pair Ordering Result

Date: 2026-07-05

## Purpose

Goal5032 proved that the device-resident carrier route was close, but still not the v2.14.3 default for the prepared LSI base-session query-batch regime:

- CPU carrier median six-batch sum: `0.971880s`
- Device carrier median six-batch sum: `1.063056s`
- Device carrier won later batches, but lost the first batch.

The largest remaining generic ordering/reduction cost in the device route was the descriptor-pair consumer. It used an app-layer Numba bitonic sort over `(label_a, label_b, length)` rows. This goal replaces that ordering step with the existing generic RTDL native CUDA/Thrust lexsort helper, then reduces on device using the sorted order.

## Implementation

Changed:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal5033_descriptor_consumer_native_lexsort_test.py`

The device descriptor consumer now:

1. copies generic descriptor columns into device arrays:
   - `label_a: int64`
   - `label_b: int64`
   - `length: int64`
2. initializes an order vector and a zero `float64` secondary key;
3. calls the existing generic native helper:
   - `optix_runtime.run_cuda_lexsort_i64_f64_i64_i64_device(...)`
4. reduces sorted `(label_a, label_b)` pairs with a Numba CUDA reducer that gathers lengths through the sorted `order`.

Fallback:

- If native lexsort is unavailable, the legacy Numba bitonic path remains as `numba_cuda_device_pair_sort_scan_fallback`.

Evidence fields added to repeat artifacts:

- `downstream_consumer_partner`
- `downstream_consumer_native_lexsort_descriptor_pair_scan`

## Generic-System Boundary

This does not add a RayJoin core primitive.

The reused RTDL primitive is the existing generic native lexsort:

```text
rtdl_cuda_sort_i64_f64_i64_i64_lex
```

The app-level descriptor consumer supplies generic integer labels and lengths. RTDL core does not learn output chains, overlay text format, CDB topology semantics, or RayJoin-specific descriptor meanings.

## Local Verification

Commands:

```text
py -3 -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
py -3 -m unittest tests.goal5019_native_lexsort_bridge_test tests.goal5021_prepared_lsi_base_session_test tests.goal5033_descriptor_consumer_native_lexsort_test
```

Result:

```text
Ran 17 tests in 0.015s
OK
```

## POD Regime

POD:

```text
root@157.157.221.29:25248
repo: /root/rtdl_goal4988
```

Input:

```text
top4 County x Zipcode
```

Regime:

- same-process prepared LSI base-session;
- six distinct chain-contiguous top4 query batches;
- writer-free binary descriptor route;
- device-columnar;
- device-resident carrier;
- native lexsort enabled;
- bounded exact LSI device columns;
- point-location device face columns.

Not this regime:

- not cold CLI one-shot;
- not paper-text output;
- not author-performance comparison;
- not same-input prepared replay.

## POD Artifacts

```text
history/internal_docs/rtdl_goal5033_nrun_device_native_descriptor_1_top4.json
history/internal_docs/rtdl_goal5033_nrun_device_native_descriptor_2_top4.json
history/internal_docs/rtdl_goal5033_nrun_device_native_descriptor_3_top4.json
```

Each measured row reports:

```text
downstream_consumer_partner = native_thrust_lexsort_i64_f64_i64_i64_descriptor_pair_scan
downstream_consumer_native_lexsort_descriptor_pair_scan = true
```

Structural anchors stayed stable:

```text
LSI row counts: [21424, 56228, 66414, 67840, 88490, 127926]
Descriptor pair counts: [2756, 2873, 2987, 3058, 4723, 6316]
```

## N-Run Matrix

| Route | Source | Median six-batch sum | Median first batch | Median later-batch sum |
|---|---:|---:|---:|---:|
| CPU carrier | Goal5032 | `0.971880s` | `0.199882s` | `0.771825s` |
| Device carrier before this goal | Goal5032 | `1.063056s` | `0.386033s` | `0.663246s` |
| Device carrier after native descriptor lexsort | Goal5033 | `0.911350s` | `0.256250s` | `0.654501s` |

Goal5033 per-run details:

| Run | Six-batch sum | First batch | Later-batch sum | First descriptor consumer | Later descriptor consumer |
|---:|---:|---:|---:|---:|---:|
| 1 | `0.930709s` | `0.276208s` | `0.654501s` | `0.015410s` | `0.042262s` |
| 2 | `0.911350s` | `0.252260s` | `0.659090s` | `0.015413s` | `0.040571s` |
| 3 | `0.898139s` | `0.256250s` | `0.641889s` | `0.015381s` | `0.040642s` |

## Interpretation

This goal turns the device carrier route from a steady-state-only win into a full six-batch win in the prepared LSI base-session query-batch regime.

Compared with Goal5032:

- device route six-batch median improved from `1.063056s` to `0.911350s`;
- device route now beats CPU carrier median `0.971880s`;
- first batch improved from `0.386033s` to `0.256250s`;
- descriptor consumer first-batch cost dropped from roughly `~0.136s` to `~0.015s`;
- later-batch descriptor consumer sum is now roughly `~0.041s`.

This is exactly the generic ordering issue exposed after Goal5032. The bottleneck was not RayJoin semantics; it was using a weak app-layer bitonic ordering implementation where RTDL already had a stronger generic native ordering primitive.

## Default Decision

Recommended scoped decision:

```text
device carrier can become the default for the prepared LSI base-session query-batch writer-free binary route, after review.
```

This is not a global default switch. The winning regime requires the prepared/query-batch/device-columnar setup listed above. Cold CLI and paper-text routes are not covered by this decision.

## Not Authorized

This goal does not authorize:

- cold CLI one-shot performance claims;
- paper text output performance claims;
- author parity claims;
- broad RayJoin Section 5.7 claims outside this top4 prepared query-batch binary route;
- a claim that all device-resident work is now solved;
- a new RTDL core RayJoin primitive.

## Exit Label

```text
completed_native_descriptor_pair_ordering__device_carrier_beats_cpu_in_prepared_query_batch_regime
```
