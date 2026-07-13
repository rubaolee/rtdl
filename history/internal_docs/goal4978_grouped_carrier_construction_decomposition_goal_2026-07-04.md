# Goal4978: Grouped Carrier Construction Decomposition

Date: 2026-07-04

## Purpose

Goal4977 removed the midpoint scaled-point host pack boundary. The largest remaining downstream component on the top4 representative route is now:

```text
grouped_compiled_columnar_carrier_construction_sec ~= 0.664s
```

Goal4978 does not optimize this phase yet. It first decomposes the phase so the next implementation does not chase the wrong target.

## Work

Instrument `build_projected_descriptor_carrier_columnar_compiled` into subphases:

- per-side input coercion/allocation
- per-side Numba side-builder execution
- per-side slice/copy into exact-length arrays
- post-side concatenation
- group-offset cumsum
- stats packaging

Run the same top4 route as Goal4977:

```text
--device-columnar
--compiled-group
--bounded-exact-lsi-device-columns --bounded-exact-lsi-capacity 600000
--point-location-device-face-columns
--fast-scaled-point-pack
```

## Verification

The result must answer:

1. Does the 0.664s carrier construction time come from Numba side-builder execution, Python/NumPy array copying, concatenation/cumsum, or compile/cache effects?
2. Does the instrumentation preserve the same structural outputs as Goal4977?
3. Is the next target a generic carrier builder optimization, or is carrier construction already below the best remaining ROI threshold?

## Boundary

Allowed:

- app-owned timing instrumentation
- local tests for presence of subphase keys
- POD top4 measurement

Forbidden:

- no RTDL core/native edit
- no RayJoin-specific core primitive
- no author-performance headline
- no new performance claim before subphase evidence

## Exit Labels

- `completed_carrier_construction_side_builder_dominated`
- `completed_carrier_construction_copy_concat_dominated`
- `completed_carrier_construction_already_below_roi_threshold`
- `fail_redo_due_to_missing_subphase_evidence`
