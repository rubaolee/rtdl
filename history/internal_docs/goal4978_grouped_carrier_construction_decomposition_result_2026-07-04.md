# Goal4978 Result: Grouped Carrier Construction Decomposition

Date: 2026-07-04

## Verdict Requested

`completed_carrier_construction_side_builder_dominated`

## Summary

Goal4978 decomposed the largest remaining downstream component after Goal4977:

```text
grouped_compiled_columnar_carrier_construction_sec
```

The result is decisive: carrier construction is dominated by the per-side Numba builder loop, especially side0. It is not dominated by Python array concatenation, offset cumsum, stats packaging, or slice copies.

## Code Changes

Changed only the app-owned reproduction script and tests:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal4978_grouped_carrier_decomposition_test.py`

No RTDL core/native code was changed for Goal4978.

The compiled carrier builder now records subphase timings:

- `grouped_compiled_carrier_side0_prepare_inputs_sec`
- `grouped_compiled_carrier_side0_numba_builder_sec`
- `grouped_compiled_carrier_side0_slice_copy_sec`
- `grouped_compiled_carrier_side0_total_sec`
- `grouped_compiled_carrier_side1_prepare_inputs_sec`
- `grouped_compiled_carrier_side1_numba_builder_sec`
- `grouped_compiled_carrier_side1_slice_copy_sec`
- `grouped_compiled_carrier_side1_total_sec`
- `grouped_compiled_carrier_concatenate_sec`
- `grouped_compiled_carrier_group_offset_cumsum_sec`
- `grouped_compiled_carrier_stats_packaging_sec`

## Local Validation

Commands:

```text
py -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
$env:PYTHONPATH='src'; py -m unittest tests.goal4978_grouped_carrier_decomposition_test tests.goal4977_fast_scaled_point_pack_test
```

Result:

```text
Ran 5 tests in 0.003s
OK
```

## POD Evidence

POD:

- `root@213.173.108.6 -p 10626`

Input:

- left: `Paper-reproduction-apps/rayjoin-paper/_data/goal4971_top4_arcgis/top4_county.cdb`
- right: `Paper-reproduction-apps/rayjoin-paper/_data/goal4971_top4_arcgis/top4_zipcode.cdb`

Route:

```text
--device-columnar
--compiled-group
--bounded-exact-lsi-device-columns --bounded-exact-lsi-capacity 600000
--point-location-device-face-columns
--fast-scaled-point-pack
```

Artifact:

- `history/internal_docs/goal4978_grouped_carrier_decomposition_artifacts_2026-07-04/carrier_decomposition_summary.json`

## Top-Level Timing

| Metric | Seconds |
|---|---:|
| writer-free hot | 4.124075 |
| downstream floor | 1.449488 |
| grouped carrier total | 0.654825 |

## Carrier Subphase Decomposition

| Carrier subphase | Seconds |
|---|---:|
| side0 prepare inputs | 0.001276 |
| side0 Numba builder | 0.576031 |
| side0 slice copy | 0.000567 |
| side0 total | 0.577883 |
| side1 prepare inputs | 0.006103 |
| side1 Numba builder | 0.067711 |
| side1 slice copy | 0.000560 |
| side1 total | 0.074382 |
| concatenate | 0.001059 |
| group offset cumsum | 0.001452 |
| stats packaging | 0.000010 |

The Numba builder loops account for almost the entire carrier construction cost:

```text
side0_numba_builder + side1_numba_builder = 0.643742s
carrier_total = 0.654825s
builder_share ~= 98.3%
```

Side0 alone accounts for:

```text
side0_numba_builder = 0.576031s
side0_builder / carrier_total ~= 88.0%
```

## Structural Consistency

Compared with Goal4977, these structural anchors match exactly:

- `lsi_row_count`
- `xsect_sorted_counts`
- `vertex_positive_counts`
- `grouped_carrier`
- `downstream_consumer`
- `scale_bounds`

The instrumentation did not change the numeric/binary route result.

## Interpretation

This closes the immediate carrier-decomposition question:

- It is not an array concatenation problem.
- It is not a cumsum problem.
- It is not a stats packaging problem.
- It is not primarily a Python slice/copy problem.

The remaining carrier cost is the actual side-builder loop:

```text
for each chain/edge/run:
    scan original map points
    inject sorted intersections
    dedupe consecutive display points
    apply face-label keep rule
    emit group length and labels
```

The next optimization must therefore target the algorithm/dataflow of the side-builder loop itself. Optimizing `np.concatenate`, `np.cumsum`, or metadata packaging would be noise.

## Generic-System Boundary

This result is still inside the paper-reproduction app, but the carrier representation remains generic:

- group-level columns: `group_offset`, `group_length`, `label_a`, `label_b`
- no paper text writer
- no output-chain byte format in RTDL core
- no CDB/RayJoin native primitive added
- no RTDL core/native edit in Goal4978

The side-builder logic is still app-owned because it encodes how a planar overlay route builds descriptor groups from chain points, intersection runs, and point-location labels.

## Next Direction

The next goal should not optimize carrier concatenation/cumsum. It should choose between two sharper options:

1. **Side-builder algorithm/dataflow optimization**
   - reduce the side0 loop work
   - precompute per-edge/run descriptors
   - avoid scanning chain points that cannot emit kept groups
   - keep the carrier generic and app-owned unless a non-RayJoin proof exists

2. **Defer carrier optimization and attack another phase**
   - if side-builder logic is judged inherently app-layer overlay assembly, stop treating it as RTDL core progress
   - focus instead on LSI setup reuse or point-location prepared-points residency

Given the evidence, the sharper next goal is a side0 builder work audit:

```text
count chain points scanned, intersection-run transitions, emitted groups, skipped groups, and dedupe operations;
identify whether 0.576s is proportional to original chain scan, intersection-run count, or kept/skipped group emission.
```

## Claim Boundary

Authorized:

- The current grouped carrier cost is side-builder-loop dominated.
- The next carrier work must target the side-builder algorithm/dataflow, not concat/cumsum.

Not authorized:

- No author-performance claim.
- No claim that true device-resident overlay is complete.
- No claim that grouped carrier should be promoted to RTDL core.
- No claim that this is a RayJoin-specific core primitive.

## Exit Label

`completed_carrier_construction_side_builder_dominated`
