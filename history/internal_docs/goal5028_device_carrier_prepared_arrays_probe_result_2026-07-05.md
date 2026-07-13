# Goal5028 Device-Carrier Prepared Arrays Probe Result

Date: 2026-07-05

## Purpose

After Goal5027 made the CPU-carrier route faster by reusing prepared segment arrays for native sort, re-test the device-resident carrier route under the same prepared LSI base-session query-batch regime.

The specific question was narrow:

> Was the device-resident carrier route losing because it re-copied carrier dataset arrays every batch, and if so, does preparing those arrays once make the device route a credible default?

## Regime

This is not a cold CLI run, not paper-text output, and not author-performance parity evidence.

Measured regime:

- Same-process prepared LSI base session.
- Six distinct chain-contiguous full-overlay query batches from top4 County x Zipcode.
- Writer-free binary descriptor consumer.
- Generic LSI prewarm time excluded from measured body.
- Prepared base-session setup excluded from measured body.
- First batch and later batches are reported separately.

## Implementation

Changed app-layer code only:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

No `src/native/**`, no `src/rtdsl/**`, no public RTDL core semantic change.

Changes:

1. Native device-columnar sort now requests device run bounds when `--device-resident-carrier` is active.
2. Prepared LSI base-session query-batch mode now prepares carrier dataset arrays once:
   - right/base carrier arrays once per session;
   - left/query-batch carrier arrays once per batch;
   - per-batch route reuses those prepared arrays via `_device_carrier_arrays_left/right`.
3. Added a source guard test to ensure the prepared-carrier-array path remains present:
   - `tests/goal5021_prepared_lsi_base_session_test.py`

## Commands

Representative POD command:

```bash
python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_county.cdb \
  --right Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_zipcode.cdb \
  --summary history/internal_docs/rtdl_goal5028_query6_device_carrier_prepared_arrays_top4.json \
  --device-columnar \
  --native-lexsort \
  --bounded-exact-lsi-device-columns \
  --bounded-exact-lsi-capacity 1000000 \
  --point-location-device-face-columns \
  --prepared-lsi-base-workspace-warmup \
  --prepared-query-batch-right-vertex-points \
  --prepared-query-batch-segment-arrays \
  --fast-scaled-point-pack \
  --compiled-group \
  --device-resident-carrier \
  --generic-lsi-prewarm \
  --prepared-lsi-base-session \
  --query-chain-batches 6 \
  --repeat 1
```

Artifacts:

- `history/internal_docs/rtdl_goal5027_query6_sort_reuse_prepared_segments_repeat_control_top4.json`
- `history/internal_docs/rtdl_goal5028_query6_device_resident_carrier_probe_top4.json`
- `history/internal_docs/rtdl_goal5028_query6_device_carrier_prepared_arrays_top4.json`

## Result

All routes kept the same structural anchor:

- Total query-batch LSI rows: `428322`
- First batch `lsi_row_count`: `127926`
- First batch descriptor pair count: `6316`

### Body Times

| Route | First batch | Median | Best | Worst | Later-batch sum | Later-batch median |
|---|---:|---:|---:|---:|---:|---:|
| Goal5027 CPU carrier, prepared segment sort reuse | 0.201693s | 0.170494s | 0.143194s | 0.201693s | 0.832571s | 0.168883s |
| Goal5028 device carrier probe, before prepared carrier arrays | 1.685051s | 0.231273s | 0.209729s | 1.685051s | 1.149308s | 0.230491s |
| Goal5028 device carrier, prepared carrier arrays | 1.741995s | 0.156655s | 0.149566s | 1.741995s | 0.797362s | 0.152307s |

### What Improved

Before prepared carrier arrays, device-carrier route paid per-batch dataset transfers:

- `device_resident_carrier_side1_dataset_to_device_sec`: later median `0.058409s`
- `device_resident_carrier_side0_dataset_to_device_sec`: later median `0.002525s`

After prepared carrier arrays:

- `device_resident_carrier_side1_dataset_to_device_sec`: `0.0s`
- `device_resident_carrier_side0_dataset_to_device_sec`: `0.0s`

Session preparation cost:

- right/base carrier arrays: `0.056274s`
- left/query batch carrier arrays: `0.001289s` to `0.003500s` per batch

That is the intended shift: remove repeated per-batch carrier dataset copies and pay them in session preparation.

### Steady-State Interpretation

For later batches only, prepared device-carrier is now slightly ahead of the CPU-carrier route:

- CPU carrier later-batch sum: `0.832571s`
- Device carrier later-batch sum after prepared arrays: `0.797362s`
- Difference: about `0.035209s`, a `~4.2%` later-batch sum improvement.

This is a real but small steady-state win.

### First-Batch Problem

The first measured device-carrier batch is still bad:

- Device-carrier first batch: `1.741995s`
- CPU-carrier first batch: `0.201693s`

The bad first batch is dominated by device-side first-call/JIT/setup costs:

- `device_resident_carrier_construction_sec`: `1.078586s`
- `device_resident_descriptor_pair_count_consumer_sec`: `0.268812s`
- `midpoint_points_map0_device_query_points_sec`: visible first-call cost in the same artifact
- `sort_map0_device_columnar_device_run_bounds_sec`: visible first-call cost in the same artifact

So the prepared carrier arrays fixed repeated transfers, but did not solve device-carrier first-call cost.

## Decision

Device carrier is no longer an obvious steady-state loser after prepared arrays. It now has a small later-batch advantage.

But it is still not a v2.14.3 default:

- first batch is much worse than CPU-carrier;
- six-batch total is worse because the first batch dominates;
- the gain is only valid in this prepared same-process query-batch regime;
- no cold CLI speedup, paper-text speedup, author parity, or 10x claim is authorized.

Recommended next step:

1. Keep CPU carrier as the v2.14.3 default writer-free route.
2. Keep device carrier behind its explicit flag.
3. If continuing, attack the first-call device-carrier floor with a narrow warmup or skip unused host run-table construction, and require the same first/later-batch matrix before any default switch.

## Exit Label

`completed_device_carrier_prepared_arrays_steady_state_small_win__blocked_by_first_batch_jit`
