# Goal5027 - Sort Reuses Prepared Segment Arrays

Date: 2026-07-05

## Verdict

`completed_sort_reuses_prepared_segment_arrays__query_batch_body_sum_3_012s_to_1_034s_since_goal5025`

Goal5027 started by checking the apparent first-batch carrier spike from Goal5026. A repeat control showed that spike was not stable. The stable bottleneck was `sort_map1_device_columnar_sec`, about `0.10s` per query batch.

The root cause was not Thrust sort itself. The sort route was re-uploading `dataset.x0/y0` to the GPU for every batch even when `--prepared-query-batch-segment-arrays` had already prepared those same segment arrays in session state.

Goal5027 changed the device-columnar sort route to reuse prepared segment arrays:

```python
sort_xsect_indices_for_map_numba_device(..., segment_device_arrays=device_segment_arrays_right)
```

This moved `sort_map1` from about `0.10s` per batch to about `0.022-0.026s` per batch in the same prepared query-batch regime.

## Implementation

Changed files:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal5019_native_lexsort_bridge_test.py`

Implementation details:

1. `sort_xsect_indices_for_map_numba_device` now accepts:

```python
segment_device_arrays=None
```

2. If present, it reuses:

```python
dataset_x0 = segment_device_arrays["x0"]
dataset_y0 = segment_device_arrays["y0"]
```

3. If absent, it falls back to the old per-call upload and records:

```text
*_segment_xy_to_device_sec
```

4. When reuse is active, it records:

```text
*_segment_xy_reused = 1.0
```

5. Native Thrust lexsort now sorts only `valid_count`, not `padded_count`; the bitonic fallback still uses padded count as required.

6. Sort now records internal breakdown fields:

```text
*_key_kernel_sec
*_native_lexsort_sec
*_copy_order_to_host_sec
*_copy_edges_to_host_sec
*_host_run_start_table_sec
*_host_run_end_table_sec
```

This made the real cause visible: the missing `~0.08s` was per-batch segment-coordinate upload, not native sort.

## Validation

Local:

```text
py -3 -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
py -3 -m unittest tests.goal5019_native_lexsort_bridge_test tests.goal5021_prepared_lsi_base_session_test
git diff --check
```

Result:

```text
12 tests OK
```

POD artifacts:

- `history/internal_docs/rtdl_goal5027_query6_lsi_workspace_warmup_repeat_control_top4.json`
- `history/internal_docs/rtdl_goal5027_query6_native_lexsort_valid_count_top4.json`
- `history/internal_docs/rtdl_goal5027_query6_sort_breakdown_top4.json`
- `history/internal_docs/rtdl_goal5027_query6_sort_reuse_prepared_segments_top4.json`
- `history/internal_docs/rtdl_goal5027_query6_sort_reuse_prepared_segments_repeat_control_top4.json`

All runs use the same top4 County x Zipcode representative input and the same writer-free prepared LSI base-session query-batch route.

## Performance Progression

Same regime:

- top4 County x Zipcode;
- 6 chain-contiguous full-overlay query batches;
- writer-free binary route;
- prepared LSI base session;
- no paper-text writer;
- no cold CLI claim;
- no author ratio claim.

| Route | 6-batch body sum | Later-batch sum | Median body | Best | Worst |
|---|---:|---:|---:|---:|---:|
| Goal5025 native lexsort + prepared right points/segments | 3.012616s | 1.187455s | 0.244431s | 0.215046s | 1.825161s |
| Goal5027 repeat control with LSI workspace warmup | 1.452135s | 1.157482s | 0.236479s | 0.212691s | 0.294652s |
| Goal5027 sort reuses prepared segment arrays | 1.034264s | 0.832571s | 0.170494s | 0.143194s | 0.201693s |

Body sum speedup against Goal5025:

```text
3.012616 / 1.034264 = 2.91x
```

This is not a cold-start speedup and not an author-performance comparison.

## Key Phase Movement

First batch comparison:

| Route | first body | first LSI | first sort_map1 | first carrier |
|---|---:|---:|---:|---:|
| Goal5025 | 1.825161s | 1.595264s | 0.109689s | 0.070978s |
| Goal5027 LSI warmup control | 0.294652s | 0.059936s | 0.110497s | 0.072822s |
| Goal5027 sort segment reuse | 0.201693s | 0.056949s | 0.024595s | 0.068838s |

The carrier spike seen in one Goal5026 artifact did not reproduce reliably. The stable repeated cost was `sort_map1`.

## Sort Decomposition

Before segment-array reuse, `sort_map1_device_columnar_sec` was around `0.10s`, but the measured internal pieces were much smaller:

```text
native_lexsort:       about 0.0005-0.0008s
copy order/edges:     about 0.0004s total
host run tables:      about 0.021-0.023s total
```

The missing time was the uninstrumented per-call upload of `dataset.x0/y0`.

After segment-array reuse:

```text
sort_map1_device_columnar_sec: about 0.022-0.026s
sort_map1_device_columnar_segment_xy_reused: 1.0
```

The remaining `sort_map1` cost is now mostly host run-table construction:

```text
host_run_start_table_sec: about 0.010-0.011s
host_run_end_table_sec:   about 0.010-0.012s
```

## Claim Boundary

Authorized:

- A generic/app-layer reuse of already prepared segment coordinate device arrays in the device-columnar sort route.
- Same-regime body improvement for prepared query batches.
- Sort decomposition showing the remaining floor is mostly host run-table construction.

Not authorized:

- cold CLI speedup;
- paper-text reproduction speedup;
- author parity;
- 10x claim;
- RTDL core RayJoin-specific primitive claim.

## Remaining Mountains

1. Host run-table construction in sort:
   - now about `0.02s` per map1 sort;
   - should be moved to device or avoided by keeping device run bounds through the downstream carrier path.

2. Carrier steady floor:
   - about `0.055-0.065s` per later batch;
   - now larger than sort.

3. LSI per-batch floor:
   - about `0.04-0.05s` per batch after workspace warmup.

4. Session prep:
   - LSI base workspace warmup still costs about `1.6s`;
   - legitimate only as prepared-service setup, not one-shot CLI.

## Recommended Next Goal

```text
Goal5028: remove host run-table construction from device-columnar sort/carrier path
```

Candidate direction:

- Use `with_device_run_bounds=True` as the primary path;
- route downstream carrier through device run bounds where possible;
- keep host run tables only for CPU carrier fallback;
- report same-regime body and session-prep-charged totals.
