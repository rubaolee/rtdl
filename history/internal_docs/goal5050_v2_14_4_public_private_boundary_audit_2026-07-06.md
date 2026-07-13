# Goal5050 - v2.14.4 Public/Private Boundary Audit

Date: 2026-07-06

Status:

```text
completed_v2_14_4_boundary_audit__public_surfaces_clean__legacy_naming_debts_deferred
```

## Purpose

Goal5050 audits the v2.14.4 public/private boundary after Goals5043-5049.

The core principle remains:

```text
RTDL is the generic system. RayJoin is an app on top of RTDL.
```

This audit distinguishes what v2.14.4 can honestly publish as public generic API
from what remains legacy/internal implementation debt.

## Amendment - Goal5059 Legacy Public Export Boundary

External review found that the original wording below was too strong for
RayJoin-named Python exports.  The following names remain present in
`rtdsl.__all__` and are therefore **legacy public exports** retained for
compatibility or RayJoin paper-app support:

```text
PreparedEmbreeRayjoinCdbPointLocation2D
PreparedOptixRayjoinCdbPointLocation2D
PreparedOptixRayjoinCdbPointLocationPoints2D
RAYJOIN_PAPER_TARGETS
RayJoinBoundedPlan
RayJoinFeatureServiceLayer
RayJoinPlan
RayJoinPublicAsset
chains_to_rayjoin_cdb_segments
download_rayjoin_sample
lower_to_rayjoin
pack_rayjoin_cdb_segments
prepare_rayjoin_cdb_point_location_2d_embree
prepare_rayjoin_cdb_point_location_2d_optix
rayjoin_bounded_plans
rayjoin_feature_service_layers
rayjoin_public_assets
```

Correct classification:

```text
legacy public exports / compatibility debt; not new v2.14.4 public generic API
```

This amends any wording that said these names are "not public API names" or
"not user-facing public contracts."  The new v2.14.4 public generic API surface
remains `DeviceColumnBuffer`, `PreparedGeometrySession`, `device_order_by`, and
`NumbaPartnerContinuation`; the RayJoin-named exports are compatibility debt or
paper-app support exports to deprecate, alias, move, or document in a later
export-hygiene goal.

Classification:

```text
CDB/point-location compatibility bridge:
  PreparedEmbreeRayjoinCdbPointLocation2D
  PreparedOptixRayjoinCdbPointLocation2D
  PreparedOptixRayjoinCdbPointLocationPoints2D
  chains_to_rayjoin_cdb_segments
  pack_rayjoin_cdb_segments
  prepare_rayjoin_cdb_point_location_2d_embree
  prepare_rayjoin_cdb_point_location_2d_optix

RayJoin paper-app/data support exports:
  RAYJOIN_PAPER_TARGETS
  RayJoinBoundedPlan
  RayJoinFeatureServiceLayer
  RayJoinPlan
  RayJoinPublicAsset
  download_rayjoin_sample
  lower_to_rayjoin
  rayjoin_bounded_plans
  rayjoin_feature_service_layers
  rayjoin_public_assets
```

## Public v2.14.4 Surfaces

The v2.14.4 public device-columnar prepared-pipeline surface now consists of:

```text
DeviceColumnBuffer
PreparedGeometrySession
device_order_by
NumbaPartnerContinuation
```

Boundary:

- these are generic API surfaces;
- they do not encode RayJoin output-chain semantics;
- they do not make `device_group_by` public;
- they do not authorize speedup, author-parity, true-zero-copy, or RT traversal
  replacement claims.

## Verification Summary

Local command already run across the adjacent gate:

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal5049_rayjoin_public_v2144_surface_migration_test tests.goal5019_native_lexsort_bridge_test tests.goal5048_non_rayjoin_numba_partner_public_api_genericity_test tests.goal5047_numba_partner_continuation_public_api_test tests.goal5046_device_group_by_public_readiness_decision_test tests.goal5045_public_device_order_by_contract_test tests.goal5044_public_prepared_geometry_session_contract_test tests.goal5043_public_device_column_buffer_contract_test
```

Result:

```text
Could not find platform independent libraries <prefix>
........s...........................
----------------------------------------------------------------------
Ran 36 tests in 0.117s

OK (skipped=1)
```

## Boundary Findings

### Finding 1 - Public API surfaces are generic and claim-bounded

`DeviceColumnBuffer`, `PreparedGeometrySession`, `device_order_by`, and
`NumbaPartnerContinuation` all expose claim-boundary metadata.  The important
claim flags remain false:

```text
public_speedup_claim_authorized
true_zero_copy_claim_authorized
app_specific_semantics_allowed
device_group_by_public_claim_authorized
replaces_rt_traversal
raw_kernel_required
```

Classification:

```text
public_surface_clean_for_v2_14_4
```

### Finding 2 - Legacy grouped/segmented Numba exports still exist

`rt.__all__` still contains historical lower-level Numba grouped/segmented
symbols such as:

```text
NUMBA_SEGMENTED_COUNT_I64_OPERATION
NUMBA_SEGMENTED_SUM_F64_OPERATION
NUMBA_GROUPED_VECTOR_SUM_F64X2_OPERATION
NUMBA_GROUPED_ARGMIN_F64_OPERATION
NUMBA_GROUPED_ARGMAX_F64_OPERATION
NUMBA_GROUPED_TOPK_F64_OPERATION
run_numba_segmented_count_i64
run_numba_grouped_vector_sum_f64x2
run_numba_grouped_topk_f64
```

This is a legacy export-hygiene debt, not a new Goal5047/5048 leak.

Important boundary:

- none of those operation values appears in
  `NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS`;
- routing them through `numba_partner_continuation(...)` fails closed;
- `device_group_by` remains absent from `rt` and `rt.__all__`;
- Goal5046 remains the controlling decision: grouped reduce is not public-ready
  in v2.14.4.

Decision:

```text
defer_removal_for_compatibility__document_as_legacy_low_level_exports
```

Follow-up:

```text
v2_14_5_export_hygiene_or_deprecation_plan
```

### Finding 3 - RayJoin-named lower-level implementation symbols remain

A local scan over `src/rtdsl` and `src/native/optix` found many RayJoin-named
implementation symbols.  Key examples include:

```text
rtdl_optix_prepare_rayjoin_cdb_point_location_2d
rtdl_optix_run_prepared_rayjoin_cdb_point_location_2d
rtdl_optix_prepared_rayjoin_cdb_point_location_2d_device_face_id_columns
rtdl_optix_rayjoin_cdb_point_location_get_last_phase_timings
PreparedRayjoinCdbPointLocation2D
RTDL_RAYJOIN_CDB_QUERY_MAP_ID
RTDL_RAYJOIN_CDB_SCALE_MIN_X
_PLANAR_MAP_LSI_LEGACY_NATIVE_ALIAS = "rayjoin_lsi"
```

These names are the known historical CDB/point-location bridge and legacy LSI
predicate naming debt.  v2.14.4 adds generic public wrappers around this
functionality, but it does not rename the native ABI.

Decision:

```text
defer_native_symbol_rename__risk_too_high_for_v2_14_4
```

Allowed v2.14.4 wording:

```text
Public API names are generic. Some lower-level native symbols retain RayJoin-era
names for compatibility and are not user-facing public contracts.
```

Amended wording for Python exports:

```text
Some RayJoin-named Python helpers remain legacy public exports for compatibility.
They are compatibility debt or paper-app support exports and are not part of
the new v2.14.4 public generic API surface.
```

Forbidden wording:

```text
All core/internal symbols are RayJoin-free.
```

Follow-up:

```text
v2_14_5_native_symbol_rename_or_alias_cleanup_design
```

### Finding 4 - RayJoin app now uses one public v2.14.4 path

Goal5049 migrated the RayJoin Section 5.7 writer-free app's optional native
lexsort path from a direct `optix_runtime` call to:

```text
DeviceColumnBuffer -> device_order_by(..., backend="native_cuda")
```

This is the correct direction: RayJoin uses RTDL public API as an app.

Classification:

```text
app_migration_partial_success__no_new_performance_claim
```

## Not Authorized

This audit does not authorize:

```text
device_group_by_public_ready
all_internal_symbols_rayjoin_free
public_speedup_claim
author_parity_claim
true_zero_copy_claim
RayJoin_core_primitive
RT_traversal_replacement_claim
POD_runtime_success_for_skipped_smokes
```

## Closeout

v2.14.4 is in a coherent state for the device-columnar prepared-pipeline API
surface:

- the public API layer is generic and claim-bounded;
- one RayJoin app route has been migrated to use the public ordering surface;
- non-RayJoin genericity has been checked structurally and with an optional
  CUDA smoke;
- grouped reduce remains intentionally non-public;
- RayJoin-named lower-level symbols are documented as compatibility debt rather
  than hidden or denied.
