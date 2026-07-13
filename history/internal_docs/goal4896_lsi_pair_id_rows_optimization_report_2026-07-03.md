# Goal4896: Planar-map LSI pair-id row optimization

Date: 2026-07-03

## Verdict requested

`completed_generic_lsi_pair_id_rows__representative_overlay_byte_equal__bounded_speedup`

## Goal

Optimize the remaining LSI bottleneck in the v2.14 RayJoin paper-reproduction engineering line without adding a RayJoin-specific hidden shortcut.

The target was the current public planar-map LSI row stage in the representative Section 5.7 overlay harness:

```python
with prepare_planar_map_lsi_2d_optix(right.lsi_segments) as lsi:
    row_view = lsi.run_raw(left.lsi_segments)
```

The harness only consumes `left_id` and `right_id`, then computes app-specific intersection reprojection in Python. The old public row route materialized full rows including `intersection_point_x/y`, which forced a native host exact-refine pass that the app did not use.

## Root cause measured before implementation

Focused POD probe on the Australia lakes x parks representative pair:

| Item | Old full-row route |
|---|---:|
| `PreparedOptixPlanarMapLsi2D.run_raw` wall | 4.797617s |
| `rowview.to_numpy_columns(copy=True)` | 0.001289s |
| rows | 13,452 |
| native `candidate_count_pass` | ~0.0029s |
| native `candidate_write_pass` | ~0.0028s |
| native `exact_refine` | 2.393130s |

Interpretation:

- RT traversal/write was not the bottleneck on this representative LSI route.
- The removable cost was the full-row native exact-refine/materialization that produced intersection coordinates not consumed by this app path.
- The other large hidden cost was prepared-left construction, which remains for future work.

Evidence artifact:

- `history/internal_docs/goal4896_lsi_probe_summary_2026-07-03.json`

## Implementation

Added a generic, lightweight exact pair-id row route for prepared-left grouped-range direct intersection:

- Native ABI:
  - `RtdlSegmentPairIdRow { uint32_t left_id, right_id; }`
  - `rtdl_optix_run_prepared_segment_pair_id_rows_prepared_left_grouped_range_direct_intersection_with_predicate_mode`
- Python runtime:
  - `_RtdlSegmentPairIdRow`
  - `PreparedOptixSegmentPairIntersection.run_prepared_left_grouped_range_direct_pair_id_rows(...)`
  - `PreparedOptixPlanarMapLsi2D.run_pair_id_rows(...)`
  - timing mode `pair_id_rows_prepared_left_grouped_range_direct_intersection`
- Harness:
  - `goal4880_section57_public_primitives_overlay_harness.py` now calls `lsi.run_pair_id_rows(...)` because it only needs `left_id/right_id`.
- Measurement wrapper:
  - records both old and new LSI routes and reads `candidate_count_pass` / `candidate_write_pass` correctly.

This is a generic LSI result-shape improvement. It does not add overlay logic, midpoint logic, output-chain logic, or RayJoin-specific app semantics to RTDL core.

## Correctness result

Representative Section 5.7 overlay remains byte-for-byte equal to the AuthorOfficial comparator:

| Metric | Value |
|---|---|
| generated SHA256 | `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e` |
| author SHA256 | `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e` |
| byte-equal | `true` |
| output lines | 276,320 |
| LSI rows | 13,452 |

Evidence artifact:

- `history/internal_docs/goal4896_pair_id_rows_overlay_summary_2026-07-03.json`

## Performance result

### LSI-only focused probe

| Route | LSI wall | Native exact refine | Rows |
|---|---:|---:|---:|
| old full-row route | 4.797617s | 2.393130s | 13,452 |
| new pair-id row route | 2.521691s | 0.000008s | 13,452 |

LSI-only speedup: about `1.90x`.

### Same-wrapper hot-cache overlay comparison

The fair end-to-end comparison uses the same Goal4886 wrapper and the same hot packed-cache state. The old control forced the LSI route back through full rows; the new run used pair-id rows.

| Route | Wrapper total | LSI stage | Writer | Byte equal |
|---|---:|---:|---:|---|
| old full-row LSI control | 16.398231s | 5.546302s | 3.380360s | true |
| new pair-id LSI route | 14.055081s | 2.855508s | 3.355789s | true |

Bounded representative overlay speedup: about `1.17x` end-to-end under this hot-cache condition.

LSI-stage speedup: about `1.94x`.

Evidence artifacts:

- `history/internal_docs/goal4896_old_lsi_control_overlay_summary_2026-07-03.json`
- `history/internal_docs/goal4896_pair_id_rows_overlay_summary_2026-07-03.json`

## Verification

Local:

```text
PYTHONPATH=src py -m unittest \
  tests.goal4851_planar_map_lsi_public_front_door_test \
  tests.goal4857_planar_map_point_location_public_front_door_test \
  tests.goal4894_directed_point_location_fine_grained_default_test \
  tests.goal4895_planar_map_cdb_packed_loader_test \
  tests.goal4895_public_cdb_loader_harness_integration_test

Ran 15 tests in 0.087s
OK
```

POD:

```text
cd /workspace/goal4894_productize_20260703b
PYTHONPATH=/workspace/goal4894_productize_20260703b/src python -m unittest \
  tests.goal4851_planar_map_lsi_public_front_door_test \
  tests.goal4857_planar_map_point_location_public_front_door_test \
  tests.goal4894_directed_point_location_fine_grained_default_test \
  tests.goal4895_planar_map_cdb_packed_loader_test \
  tests.goal4895_public_cdb_loader_harness_integration_test

Ran 15 tests in 0.058s
OK
```

POD native build:

```text
make build-optix OPTIX_PREFIX=/tmp/optix-sdk-probe
```

Build succeeded.

## Boundaries

Authorized claim:

- RTDL now has a generic lightweight planar-map LSI pair-id row route.
- On the representative Australia lakes x parks Section 5.7 workload, this removes unused full-row exact-refine work and improves the LSI stage by about 1.9x while preserving byte equality.
- Under a same-wrapper hot-cache representative run, this improves end-to-end time from 16.40s to 14.06s.

Not authorized:

- No full Section 5.7 eight-pair claim.
- No broad RayJoin performance claim.
- No claim that RTDL beats AuthorOfficial overall.
- No claim that this closes the deeper in-traversal fusion/callback gap.
- No claim that this is a RayJoin-specific hidden kernel.

## Remaining bottleneck after Goal4896

In the hot-cache representative run, dominant remaining phases are now:

- output writer: about 3.36s
- LSI pair-id row stage: about 2.86s
- vertex PIP map0 in map1: about 1.10s outer Python/native call wall, but native traversal itself remains tiny
- prepared-left construction is still part of the LSI wall and is the likely next generic target

The next optimization should not invent app-specific overlay shortcuts. The next evidence-driven target is either:

1. prepared-left reuse/device-resident query side for repeated LSI workloads, or
2. writer/app-continuation cleanup if the product line wants to keep pushing representative full-overlay wall time.
