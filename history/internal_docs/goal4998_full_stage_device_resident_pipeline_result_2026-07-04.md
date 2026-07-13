# Goal4998 - RayJoin 5.7 Writer-Free Device-Resident Pipeline Result

Date: 2026-07-04

## Objective

Implement and measure the next RayJoin 5.7 writer-free route requested by the owner:

> connect the existing RTDL/Numba device-column assets into the real RayJoin reprojection/sort/midpoint/PIP/carrier/consumer path, instead of stopping at demo-level row-buffer handoff.

The goal was not to add a RayJoin-specific RTDL core primitive.  The implementation stayed in the paper-reproduction app layer and used existing public/generic RTDL outputs where available.

## What Changed

The app now has an experimental `--device-resident-carrier` route in:

`Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

It adds:

1. Device-side midpoint face scatter, so midpoint PIP face-id results do not have to be copied back to host merely to fill the face-id array.
2. Prepared-session carrier dataset arrays, so chain offsets, chain face labels, and point coordinate arrays are copied to device once per prepared operator session rather than once per measured run.
3. Device carrier construction kernels for side count, prefix, fill, side combine, and descriptor pair aggregation.
4. Device descriptor-pair consumer that returns only scalar summary results to host.
5. Phase accounting for the new device-resident stages.

The first prototype regressed badly because it built dense device run-bound tables inside sort and recopied large dataset arrays per run.  The current implementation fixes those two concrete mistakes:

- It does not force dense device run-bound generation in the sort path.
- It reuses prepared carrier dataset arrays in the prepared/query-many protocol.

## POD Evidence

POD:

`root@157.157.221.29 -p 25248`

Dataset:

`top4_county_zipcode`

Inputs:

- `Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_county.cdb`
- `Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_zipcode.cdb`

Both routes used:

- `--device-columnar`
- `--bounded-exact-lsi-device-columns`
- `--point-location-device-face-columns`
- `--fast-scaled-point-pack`
- `--prepared-operator-session`
- `--warmup-runs 1`
- `--repeat 5`

Artifacts:

- `history/internal_docs/goal4998_full_stage_device_resident_pipeline_artifacts_2026-07-04/baseline_compiled_group_top4_repeat5_serial.json`
- `history/internal_docs/goal4998_full_stage_device_resident_pipeline_artifacts_2026-07-04/device_resident_carrier_top4_repeat5_serial.json`

## Correctness / Structural Gate

Both routes produced:

- `lsi_row_count`: `428322`
- `descriptor_pair_count`: `15014`
- `structural_consistency.single_lsi_row_count`: `true`
- `structural_consistency.single_descriptor_pair_count`: `true`

This is not a paper-text byte-equality route.  It is the writer-free binary descriptor route.

## Performance Result

Baseline prepared/query-many route using the existing compiled CPU/Numba carrier:

- best writer-free hot time: `0.3583594933152199s`
- median writer-free hot time: `0.36405662819743156s`

New `--device-resident-carrier` route:

- best writer-free hot time: `0.3312861304730177s`
- median writer-free hot time: `0.338140819221735s`

Observed improvement:

- best: about `7.55%`
- median: about `7.12%`

This is a real but modest improvement.  It is not an author-performance-parity result and not a fresh one-shot headline.

## Key Phase Comparison

New device-resident carrier measured run, representative median-like row:

- LSI pair-id device columns: about `0.003s`
- reprojection: about `0.004s`
- sort map0: about `0.030s`
- sort map1: about `0.114-0.131s`
- vertex PIP total: about `0.029s`
- midpoint generation/PIP/scatter total: about `0.024-0.030s`
- device carrier construction: about `0.081-0.087s`
- device descriptor consumer: about `0.039-0.046s`

The route removed the previous per-run dataset-to-device carrier copy:

- side0 dataset copy in measured runs: `0.0s`
- side1 dataset copy in measured runs: `0.0s`
- session carrier array prepare: about `0.0096s` left, `0.0558s` right

## Honest Boundary

This is progress toward the requested full-stage device-resident pipeline, but it is not yet a strict zero-copy, all-stage GPU pipeline.

Still not fully device-resident:

1. Midpoint query points still pass through the current point-location query-point ABI.  The PIP output can remain as device face-id columns, but query point preparation is not yet a pure device-column input API.
2. Sort still returns host order/run-bound metadata for compatibility and diagnostics.  The device carrier route copies run-bound tables to device rather than deriving compact run bounds entirely on device.
3. The app still copies scalar summary results to host, which is acceptable for a binary summary consumer but not a fully chained downstream SQL operator.
4. This is app-layer code.  It does not yet prove a generic non-RayJoin downstream consumer with the same device-carrier route.

## What This Proves

It proves that the existing RTDL/Numba device-column assets can be connected into the real RayJoin writer-free route beyond a toy handoff:

- LSI pair-id device output feeds Numba reprojection.
- Device sort feeds downstream stages.
- Point-location face-id columns are retained for device scatter/carrier use.
- Carrier construction and descriptor-pair counting can execute on device arrays.
- The resulting route preserves structural output and slightly improves prepared/query-many hot performance.

## What This Does Not Prove

It does not prove:

- full fresh one-shot performance improvement;
- paper text byte-equality;
- author performance parity;
- a fully zero-copy end-to-end GPU pipeline;
- a generic RTDL core primitive for overlay;
- that RayJoin-specific output-chain semantics belong in RTDL core.

## Current Bottleneck

After this change, the dominant steady hot costs are still:

1. sort map1, around `0.11-0.13s`;
2. device carrier plus descriptor consumer, around `0.12-0.13s`;
3. smaller PIP/midpoint/reprojection phases.

The device carrier route improves the route modestly, but the remaining floor is now mostly ordering plus small-kernel carrier/consumer work.  Several kernels show low-occupancy warnings, which is consistent with small reduce/prefix kernels not being a natural GPU win at this scale.

## Exit Label

`completed_goal4998_app_layer_device_resident_carrier_route__modest_prepared_hot_win__not_strict_zero_copy`
