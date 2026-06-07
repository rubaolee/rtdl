# Goal3684 Native Relation-Status Corrected Scalar Count

Date: 2026-06-07

## Purpose

Goal3677 and Goal3681 proved that a generic relation-status candidate stream plus a Numba boundary-contact continuation could compute an exact closed-shape membership scalar count. The negative lesson was that boundary-status rows were dense on the full public county dataset (`47241 / 47264`), so even the resident Numba path still had to preserve and consume a large boundary candidate stream.

Goal3684 implements the next generic primitive step: a native OptiX relation-status corrected scalar-count route that validates boundary-contact candidates inside the traversal path and downloads only scalar counters.

This is not a RayJoin-specific ABI. The new symbol is:

`rtdl_optix_count_prepared_point_closed_shape_membership_relation_status_corrected_prepared_points_2d`

## Implementation

Changed files:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal3677_rayjoin_pip_relation_status_exact_count_timing.py`
- `tests/goal3684_native_relation_status_corrected_scalar_count_test.py`

The implementation adds:

- `RtdlNativeClosedShapeScalarCountSummary`, a compact scalar summary with exact row count, candidate count, boundary-candidate count, dropped-candidate count, timing, device ordinal, and claim-neutral correction flags.
- double-precision lookup buffers on prepared closed-shape geometry and prepared point columns, while preserving the existing float traversal columns for the fast RT path.
- a source-specialized OptiX pipeline named `point_closed_shape_relation_status_corrected_scalar_count_kernel.cu`.
- `PreparedOptixPointClosedShapeMembership2D.count_relation_status_corrected_prepared_points_native(...)`, an explicit Python front door that returns a non-authorizing dictionary rather than device row columns.

The native route counts:

`exact_count = interior_relation_candidate_count + exact_boundary_contact_candidate_count`

It records:

- all accepted relation candidates,
- boundary-contact candidates,
- boundary candidates dropped by the double-precision exact boundary predicate,
- final exact scalar count.

No boundary candidate row stream is materialized in this route.

## A5000 Evidence

Artifact:

`docs/reports/goal3684_native_relation_status_corrected_scalar_count_a5000/summary.json`

Pod:

`NVIDIA RTX A5000, driver 580.126.09`

Dataset:

`data/rayjoin_public_cdb/br_county_start0_count16545.cdb`

Rows:

- points: `16545`
- shapes: `15700`
- exact oracle count: `47262`

Hot medians:

| Route | Median seconds | Stable count |
| --- | ---: | ---: |
| all relation candidates, count-only | `0.000462798` | `47264` |
| boundary-status candidate columns | `0.000723106` | `47241` |
| relation-status corrected exact Numba count | `0.003212072` | `47262` |
| resident relation-status corrected exact Numba count | `0.001824513` | `47262` |
| native relation-status corrected exact scalar count | `0.000516817` | `47262` |

Correctness:

- native corrected count: `47262`
- exact oracle count: `47262`
- native all-match exact count: `true`
- dropped boundary-contact candidates: `2`

The artifact was generated from clean scoped source at commit `eaeafde2` (`goal3677_scoped_source_dirty=false`).

Relative to the prior resident Numba path in the same packet, the native scalar route is about `3.53x` faster (`0.001824513 / 0.000516817`) and does not materialize boundary candidate rows. Relative to the one-shot Numba corrected path, it is about `6.21x` faster.

## Interpretation

This is the first strong fix for the dense-boundary weakness found in Goal3677:

- relation-status filtering alone was not sparse enough,
- resident Numba reduced repeated overhead but still required dense boundary columns,
- the new native scalar correction keeps the app-agnostic relation-status contract and removes the dense boundary row stream for scalar count-only workloads.

This is a generic closed-shape membership scalar-count primitive. It does not put RayJoin, CDB, county, GIS overlay, or any benchmark-app vocabulary into the native ABI.

## Boundary

This report does not authorize:

- release,
- default-route promotion,
- public speedup claims,
- RTDL-beats-RayJoin claims,
- RayJoin paper reproduction claims,
- broad RT-core speedup claims,
- true zero-copy claims.

The evidence authorizes only this internal engineering conclusion: the generic native relation-status corrected scalar-count route is exact on the measured full public county dataset and removes the dense boundary-row materialization bottleneck for scalar count-only closed-shape membership.

## Next Work

The next useful work is:

1. add a fresh external review of Goal3684,
2. decide whether this native scalar count becomes the recommended RayJoin count reference route,
3. investigate whether the same scalar-correction pattern can serve other dense-boundary benchmark rows without creating app-shaped engine code.
