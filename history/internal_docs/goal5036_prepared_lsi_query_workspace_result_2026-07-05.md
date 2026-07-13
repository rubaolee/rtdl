# Goal5036 Result: Prepared LSI Query-Batch Workspace Warmup

Date: 2026-07-05

## Verdict

`completed_prepared_query_batch_lsi_workspace_warmup__query_many_hot_body_improved`

Goal5036 adds an app-level prepared-query-batch workspace route for the RayJoin writer-free binary operator. It does not add a RayJoin-specific RTDL core primitive. It prepares and warms each distinct query batch's LSI query workspace during session preparation, then the measured hot body still recomputes bounded exact LSI pair-id device columns.

## What Changed

File changed:
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal5036_prepared_lsi_query_workspace_test.py`

New CLI flag:

```text
--prepared-query-batch-lsi-query-workspaces
```

Required context:
- `--prepared-lsi-base-session`
- `--query-chain-batches > 0`
- `--bounded-exact-lsi-device-columns`

Implementation summary:
- During session preparation, create one prepared LSI query handle per chain-contiguous query batch.
- Warm each prepared query's scaled-cache workspace by running bounded exact pair-id device-column production once in the session phase.
- During measured rows, pass the already prepared query handle to `run_pipeline`.
- Measured rows still execute `produce_lsi_bounded_exact_device_columns_from_prepared_query(...)` and emit LSI pair-id device columns.
- All prepared query handles are closed in `finally`.

Claim-boundary metadata now records:

```json
"prepared_query_batch_lsi_query_workspaces": true,
"prepared_query_batch_lsi_query_workspaces_scope": "session_prepares_and_warms_each_distinct_batch_lsi_query_workspace_without_reusing_results"
```

## POD Environment

POD:

```text
ssh root@157.157.221.29 -p 22051
```

GPU:

```text
NVIDIA RTX 4000 Ada Generation
```

Notes:
- System driver/toolchain could not run the native CUDA lexsort path because CUDA 12.8 generated PTX unsupported by the installed driver.
- I installed CUDA 12.4 NVVM/NVRTC pip packages in the POD venv for Numba compatibility.
- Native lexsort remained blocked by the POD's RTDL native CUDA JIT/PTX mismatch, so the final A/B uses the Numba CUDA sort fallback for both baseline and warmed routes.
- This is still a fair Goal5036 A/B because the only tested variable is the new `--prepared-query-batch-lsi-query-workspaces` flag.

## Input

Top4 County x Zipcode representative input staged on the POD:

```text
Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_county.cdb
Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_zipcode.cdb
```

Structural anchors were identical for all runs:

```text
lsi_row_counts:        [21424, 56228, 66414, 67840, 88490, 127926]
descriptor_pair_counts:[2756, 2873, 2987, 3058, 4723, 6316]
```

## Performance Evidence

Same POD, same input, same route, same Numba sort fallback. Three runs per route.

Baseline route:

```text
--prepared-lsi-base-session
--query-chain-batches 6
--prepared-query-batch-right-vertex-points
--prepared-query-batch-segment-arrays
--prepared-lsi-base-workspace-warmup
--device-resident-carrier
```

Warmed route adds:

```text
--prepared-query-batch-lsi-query-workspaces
```

### Median-of-Medians

| Route | median writer-free hot | median LSI phase | median downstream floor |
|---|---:|---:|---:|
| Baseline | 0.131156s | 0.044176s | 0.085430s |
| Prepared query-batch workspace | 0.089189s | 0.002034s | 0.086616s |
| Delta | -0.041967s | -0.042143s | +0.001186s |
| Ratio | 1.47x faster | 21.72x faster | neutral |

Interpretation:
- The new route removes roughly 42ms from the query-batch hot body.
- The improvement is almost exactly the LSI phase reduction.
- Downstream is unchanged, which is expected.

### Per-Run Summary

| Artifact | Route | median hot | median LSI | median downstream |
|---|---|---:|---:|---:|
| `rtdl_goal5036_baseline_numba_sort_1_top4.json` | baseline | 0.129915s | 0.044176s | 0.083718s |
| `rtdl_goal5036_baseline_numba_sort_2_top4.json` | baseline | 0.134173s | 0.044532s | 0.085430s |
| `rtdl_goal5036_baseline_numba_sort_3_top4.json` | baseline | 0.131156s | 0.044018s | 0.085949s |
| `rtdl_goal5036_warmed_numba_sort_1_top4.json` | warmed | 0.091457s | 0.003252s | 0.088014s |
| `rtdl_goal5036_warmed_numba_sort_2_top4.json` | warmed | 0.087888s | 0.002034s | 0.085749s |
| `rtdl_goal5036_warmed_numba_sort_3_top4.json` | warmed | 0.089189s | 0.001963s | 0.086616s |

### Session Prepare Cost

The warmed route moves work out of the hot body into session preparation:

```text
median additional per-batch LSI query/workspace session prep: ~0.323s
```

This is why the result is valid for a prepared-base/query-batch route, not for cold CLI one-shot.

## Correctness / Integrity

Local checks:

```text
py -3 -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
py -3 -m unittest tests.goal5036_prepared_lsi_query_workspace_test tests.goal5035_public_perf_boundary_guard_test tests.goal5034_device_carrier_atomic_append_test
git diff --check
```

Result:

```text
Ran 7 tests in 0.004s
OK
```

POD checks:

```text
python -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
python -m unittest tests.goal5036_prepared_lsi_query_workspace_test
```

Result:

```text
Ran 3 tests in 0.002s
OK
```

Runtime structural anchors:
- LSI row counts identical across baseline and warmed routes.
- Descriptor pair counts identical across baseline and warmed routes.
- `lsi_pair_input_device_resident == true`.
- `lsi_pair_host_to_device_copy_used == false`.

## Not Authorized

This result does not authorize:
- cold CLI one-shot performance claims;
- paper-text output performance claims;
- author parity claims;
- same-input replay claims;
- saying results are cached or replayed;
- claiming native lexsort success on this POD;
- claiming full device-resident pipeline completion.

## Actual Meaning

Goal5036 proves a narrow but real product point:

> In the prepared-base + distinct query-batch regime, the per-batch LSI scaled-cache workspace can be prepared once per batch and removed from the measured hot body, while still recomputing LSI pair-id device columns. On top4 County x Zipcode, this improves the writer-free hot body from about 0.131s to about 0.089s, a 1.47x improvement for this regime.

## Remaining Bottleneck

After this change, the median hot body is approximately:

```text
LSI phase:        ~0.002s
downstream floor: ~0.087s
total hot body:   ~0.089s
```

The next performance target is no longer LSI scaled-cache setup in this prepared query-batch regime. The remaining work is downstream:
- descriptor consumer / pair scan,
- carrier construction,
- first-batch outliers and PIP/session setup,
- native lexsort toolchain compatibility if native sort is required on this POD class.
