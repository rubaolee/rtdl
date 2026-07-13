# Goal5034 Device Carrier Atomic Append Result

Date: 2026-07-05

## Purpose

Goal5033 removed the weak app-layer bitonic descriptor ordering and reused RTDL's generic native CUDA/Thrust lexsort. After that, the remaining device-carrier cost was the carrier construction path itself.

The old device carrier was conservative and order-preserving:

```text
count groups -> prefix sum -> fill rows -> combine side0/side1
```

For the writer-free binary descriptor route, that order is not semantically required. The downstream consumer immediately sorts generic descriptor pairs `(label_a, label_b)` with the native lexsort route introduced in Goal5033. Therefore this goal replaces the carrier construction path with an app-layer atomic append builder:

```text
emit valid descriptor groups directly into preallocated device columns
```

## Implementation

Changed:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal5034_device_carrier_atomic_append_test.py`

The new device carrier route adds:

- `_carrier_emit_group_atomic(...)`
- `_carrier_side_atomic_append_kernel(...)`
- `_build_projected_descriptor_carrier_device_atomic_append_side(...)`

The active `build_projected_descriptor_carrier_columnar_device(...)` route now:

1. allocates over-capacity device columns for `group_length`, `label_a`, and `label_b`;
2. allocates device counters for `group_count`, `point_rows`, and `skipped`;
3. runs one atomic-append kernel per side;
4. copies only the small counters and overflow flag back to host;
5. fails closed on overflow;
6. returns a compact metadata shape to the native descriptor consumer.

The old count/prefix/fill kernels remain in the file for compatibility and diagnostics, but the active device carrier builder no longer uses them.

The atomic append kernel was also added to the existing CUDA warmup path. A diagnostic no-warm run exposed a first-batch Numba JIT spike in the new kernel. The final matrix below uses the warmed route, consistent with the existing prepared LSI base-session regime.

## Generic-System Boundary

This is not a RayJoin core primitive.

The optimization is app-layer carrier construction over generic descriptor columns:

```text
label_a: int64
label_b: int64
group_length: int64
```

RTDL core does not learn output-chain semantics, paper-text format, CDB topology rules, or RayJoin overlay semantics. The downstream ordering/reduction remains the generic native lexsort path:

```text
native_thrust_lexsort_i64_f64_i64_i64_descriptor_pair_scan
```

The route is valid only because this writer-free binary consumer is set-based and sorts descriptor pairs later. It is not authorized for the paper text byte-equality writer route, where generation order may matter.

## Local Verification

Commands:

```text
py -3 -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
py -3 -m unittest tests.goal5033_descriptor_consumer_native_lexsort_test tests.goal5034_device_carrier_atomic_append_test
git diff --check
```

Result:

```text
Ran 6 tests
OK
```

The tests check that:

- the active device carrier builder uses the atomic append path;
- the active builder no longer calls the count/prefix/fill kernels;
- the carrier remains app-layer and does not import `rtdsl.rayjoin_overlay`;
- the implementation carries `rtdl_core_change: False`.

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
- native descriptor lexsort enabled;
- bounded exact LSI device columns;
- point-location device face columns.

Not this regime:

- not cold CLI one-shot;
- not paper-text output;
- not author-performance comparison;
- not same-input prepared replay.

## POD Artifacts

```text
history/internal_docs/rtdl_goal5034_atomic_append_warmed_device_carrier_1_top4.json
history/internal_docs/rtdl_goal5034_atomic_append_warmed_device_carrier_2_top4.json
history/internal_docs/rtdl_goal5034_atomic_append_warmed_device_carrier_3_top4.json
```

Each measured row reports:

```text
device_resident_carrier_side0_atomic_append_used = 1.0
device_resident_carrier_side1_atomic_append_used = 1.0
device_resident_carrier_side*_count_kernel_sec = 0.0
device_resident_carrier_side*_prefix_sum_sec = 0.0
device_resident_carrier_side*_fill_kernel_sec = 0.0
downstream_consumer_partner = native_thrust_lexsort_i64_f64_i64_i64_descriptor_pair_scan
downstream_consumer_native_lexsort_descriptor_pair_scan = true
```

Structural anchors stayed stable in all three runs:

```text
LSI row counts: [21424, 56228, 66414, 67840, 88490, 127926]
Descriptor pair counts: [2756, 2873, 2987, 3058, 4723, 6316]
```

## N-Run Matrix

| Route | Source | Median six-batch sum | Median first batch | Median later-batch sum |
|---|---:|---:|---:|---:|
| CPU carrier | Goal5032 | `0.971880s` | `0.199882s` | `0.771825s` |
| Device carrier after native descriptor lexsort | Goal5033 | `0.911350s` | `0.256250s` | `0.654501s` |
| Device carrier with atomic append | Goal5034 | `0.755416s` | `0.194246s` | `0.568413s` |

Goal5034 per-run details:

| Run | Six-batch sum | First batch | Later-batch sum | LSI sum | Downstream sum | Carrier construction sum | Descriptor consumer sum |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `0.728717s` | `0.194246s` | `0.534471s` | `0.257345s` | `0.471371s` | `0.162283s` | `0.066857s` |
| 2 | `0.755416s` | `0.182958s` | `0.572458s` | `0.277508s` | `0.477908s` | `0.160964s` | `0.067528s` |
| 3 | `0.779284s` | `0.210871s` | `0.568413s` | `0.289657s` | `0.489627s` | `0.159711s` | `0.066608s` |

Median detailed sums:

```text
six-batch total:        0.755416s
first batch:            0.194246s
later-batch sum:        0.568413s
LSI sum:                0.277508s
downstream sum:         0.477908s
carrier construction:   0.160964s
descriptor consumer:    0.066857s
side0 atomic kernels:   0.084124s
side1 atomic kernels:   0.063720s
```

## Interpretation

Goal5034 removes the last known order-preserving carrier-construction tax from the device route in this regime.

Compared with Goal5033:

- six-batch median improved from `0.911350s` to `0.755416s`;
- absolute improvement is `0.155934s`;
- relative improvement is `17.1%`;
- first batch improved from `0.256250s` to `0.194246s`;
- later-batch sum improved from `0.654501s` to `0.568413s`.

Compared with the CPU carrier baseline from Goal5032:

- six-batch median improved from `0.971880s` to `0.755416s`;
- absolute improvement is `0.216464s`;
- relative improvement is `22.3%`.

The result is a real improvement in the selected prepared LSI base-session, six-batch, writer-free binary route. It is not a cold-start result and not a paper-text reproduction speed claim.

## Remaining Floor

After this goal, carrier construction is no longer the blocking issue it was before Goal5034. The remaining measured per-six-batch floor is split mainly between:

- LSI pair-id production for each distinct batch: median `0.277508s`;
- downstream binary continuation: median `0.477908s`, of which carrier construction is now about `0.160964s` and descriptor consumer about `0.066857s`.

The next optimization, if authorized, should be chosen from measured hot-path components in this same regime. It must not switch back to cold CLI, paper text, or prepared replay.

## Exit Label

```text
completed_goal5034_atomic_append_device_carrier__prepared_query_batch_route_faster
```
