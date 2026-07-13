# Goal5029 Device-Carrier Skip Host Run Tables Result

Date: 2026-07-05

## Purpose

Goal5028 showed that preparing carrier dataset arrays removed repeated per-batch device copies and made the device-resident carrier route slightly faster in later batches. However, the route still built host `run_start` / `run_end` tables during native sort even though the device-resident carrier consumes device run bounds.

Goal5029 removes that redundant host run-table construction for the device-carrier route only.

## Scope

Changed app-layer code only:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal5021_prepared_lsi_base_session_test.py`

No `src/native/**`, no `src/rtdsl/**`, no core RayJoin primitive.

## Implementation

`sort_xsect_indices_for_map_numba_device(...)` now has:

```python
with_host_run_tables: bool = True
```

Default behavior remains unchanged.

When `--device-resident-carrier` is active, the route calls native sort with:

```python
with_device_run_bounds=True
with_host_run_tables=False
```

The returned sorted view still includes host `order` and `edge_ids`, because other app phases may inspect them. It skips only host `run_start` and `run_end`, which the device-resident carrier does not need.

The summary now records:

- `sort_map0_device_columnar_host_run_tables_skipped = 1.0`
- `sort_map1_device_columnar_host_run_tables_skipped = 1.0`

## POD Evidence

Artifact:

- `history/internal_docs/rtdl_goal5029_query6_device_carrier_skip_host_run_tables_top4.json`

Command regime:

- same-process prepared LSI base session;
- six distinct chain-contiguous top4 County x Zipcode query batches;
- writer-free binary descriptor route;
- device-resident carrier;
- native lexsort;
- prepared carrier arrays from Goal5028;
- no cold CLI claim;
- no paper-text route claim.

## Results

Structural anchors remain stable:

- Total LSI rows across six batches: `428322`
- First batch LSI rows: `127926`
- First batch descriptor pair count: `6316`

### Body Time Matrix

| Route | First batch | Median | Best | Worst | Six-batch sum | Later-batch sum | Later-batch median |
|---|---:|---:|---:|---:|---:|---:|---:|
| Goal5027 CPU carrier, prepared segment sort reuse | 0.201693s | 0.170494s | 0.143194s | 0.201693s | 1.034264s | 0.832571s | 0.168883s |
| Goal5028 device carrier, prepared carrier arrays | 1.741995s | 0.156655s | 0.149566s | 1.741995s | 2.539357s | 0.797362s | 0.152307s |
| Goal5029 device carrier, skip host run tables | 1.628664s | 0.141181s | 0.129552s | 1.628664s | 2.323421s | 0.694757s | 0.140892s |

## Interpretation

This is a real improvement to the device-resident route:

- Later-batch sum improves from `0.797362s` to `0.694757s` versus Goal5028.
- Later-batch median improves from `0.152307s` to `0.140892s`.
- Compared with CPU carrier, later-batch sum improves from `0.832571s` to `0.694757s`, about a `16.6%` steady-state gain.

But the first-batch cost remains too high:

- CPU carrier first batch: `0.201693s`
- Device carrier first batch after Goal5029: `1.628664s`

So device-carrier is now a credible steady-state route, but still not a v2.14.3 default for one-shot or short-run workloads.

## What This Does Not Prove

This does not prove:

- cold CLI one-shot speedup;
- paper-text route speedup;
- author parity;
- 10x;
- a fully zero-copy route;
- that device-carrier should replace CPU carrier as default.

## Next Mountain

The remaining device-carrier blocker is first-call/JIT/setup cost:

- `device_resident_carrier_construction_sec` first batch: `~1.07s`
- `device_resident_descriptor_pair_count_consumer_sec` first batch: `~0.23s`
- first device midpoint-query and device run-bound kernels also show first-call cost.

The next valid goal is a device-carrier warmup / kernel precompile probe that:

1. warms the carrier construction kernels and descriptor consumer without using measured query rows as hidden replay;
2. reports first batch and later batches separately;
3. keeps CPU carrier as default unless the first-batch penalty is actually removed.

## Exit Label

`completed_device_carrier_skip_host_run_tables__steady_state_win_first_batch_still_blocks_default`
