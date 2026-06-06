# Goal3551 RT-DBSCAN Internal Repeat Hook

Date: 2026-06-06

## Purpose

Goal3548 produced a same-contract v2.8/v2.3 A5000 packet with all rows meeting the planned 10-second target, but `rt_dbscan_optix_grouped_stream` remained the weakest observed row at `0.955x`. That row was still being extended by the outer Goal3536 subprocess wrapper instead of by an app-level hot-query repeat loop.

Goal3551 closes that measurement weakness for RT-DBSCAN. The benchmark app now exposes `--repeat` and `--warmup` for the prepared grouped-stream path, so the harness can measure repeated prepared-query execution without re-running process startup or one-time app setup for every repeat.

## Changes

- Added `repeat` and `warmup` parameters to `run_rt_dbscan_benchmark`.
- Added CLI flags:
  - `--repeat`
  - `--warmup`
- Implemented a prepared grouped-stream repeat loop inside the `optix_rt_core_grouped_stream_*` modes.
- Kept scalar repeat metadata only, including:
  - repeat count
  - warmup count
  - measured run count
  - median measured hot-loop elapsed time
  - total measured hot-loop elapsed time
  - signature-stability flag
- Preserved one-shot behavior by default with `repeat=1` and `warmup=0`.
- Updated the Goal2626 benchmark registry so `rt_dbscan_optix_grouped_stream` declares an internal repeat knob with `--warmup 1 --repeat 3`.
- Refreshed the v2.3 measurement-overlay patch so the same repeat flags can be applied to the v2.3 comparison checkout.

## Measurement Semantics

For grouped-stream modes, the benchmark now separates:

- prepare time, stored in the timing breakdown as `prepare_sec`;
- repeated prepared-query execution, summarized by median hot-loop elapsed time;
- optional column-signature generation or row materialization, depending on the selected mode.

The top-level `elapsed_sec` for repeated grouped-stream runs is the median measured prepared-query run after warmup, not total wall time including one-time preparation. This matches the intended Goal3536 steady-state comparison: prepared handles are allowed on both v2.3 and v2.8, and the measured row should compare the steady query contract rather than subprocess relaunch overhead.

## Boundaries

This goal does not authorize any new public performance claim by itself. It only gives the RT-DBSCAN row a fairer repeat mechanism for the next A5000 packet.

Still blocked until fresh pod evidence:

- whether the `rt_dbscan_optix_grouped_stream` row improves relative to the Goal3548 `0.955x` observation;
- whether the full 11-row v2.8/v2.3 packet remains at 10-second-level observed durations;
- any release, public speedup, broad RT-core speedup, whole-app speedup, or zero-copy claim.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3551_rt_dbscan_internal_repeat_hook_test tests.goal3536_v2_8_vs_v2_3_10s_steady_state_test tests.goal3548_v2_9_a5000_same_contract_repeat_evidence_test
```

Result:

```text
Ran 13 tests
OK
```

The v2.3 overlay patch was also checked against a fresh v2.3 worktree with:

```powershell
git apply --check docs/patches/goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch
py -3 -m py_compile examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py scripts/goal2626_benchmark_embree_optix_baseline.py
```

## Next Step

Run a targeted A5000 packet for `rt_dbscan_optix_grouped_stream` first. If it is clean, fold it into a refreshed 11-row v2.8/v2.3 packet using the same Goal3536 same-contract protocol.
