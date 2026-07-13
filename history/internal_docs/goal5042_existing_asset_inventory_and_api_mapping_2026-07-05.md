# Goal5042 - Existing Asset Inventory And API Mapping

Date: 2026-07-05

Status: completed inventory; no runtime implementation

Exit label:

```text
completed_asset_inventory_for_v2_14_4_api
```

## Scope

Goal5042 is the first v2.14.4 implementation-planning gate.  It does not add public API and does not change runtime/native behavior.  It inventories the existing assets that should become the v2.14.4 device-columnar prepared pipeline API, and it records RayJoin-named core/native debt with explicit remediate-or-defer decisions.

## Commands Used

Evidence was gathered with focused repository scans:

```powershell
rg -n "DeviceColumn|RowBuffer|HitStream|PartnerResident|Prepared|Session|lexsort|group|reduce|DLPack|dlpack|cuda_array|__cuda_array_interface__|materializes_host_rows|producer_consumer_stream_ordering" src/rtdsl tests -g "*.py"
rg -n "rayjoin|RayJoin|RayjoinCdb|rtdl_optix_.*rayjoin|prepare_rayjoin|Prepared.*Rayjoin|rayjoin_lsi|RTDL_OPTIX_SEGMENT_PAIR_PREDICATE" src/rtdsl src/native tests Paper-reproduction-apps -g "*.py" -g "*.cpp" -g "*.cu" -g "*.h"
rg -o "rtdl_(optix|embree)_[A-Za-z0-9_]*rayjoin[A-Za-z0-9_]*|Prepared[A-Za-z0-9_]*Rayjoin[A-Za-z0-9_]*|RtdlRayjoin[A-Za-z0-9_]*|RayjoinCdb[A-Za-z0-9_]*|rayjoin_lsi|RTDL_[A-Z0-9_]*RAYJOIN[A-Z0-9_]*|RTDL_OPTIX_SEGMENT_PAIR_PREDICATE" src/rtdsl/optix_runtime.py src/rtdsl/embree_runtime.py src/native/optix src/native/embree -g "*.py" -g "*.cpp" -g "*.cu" -g "*.h"
```

Line-based counts from the focused RayJoin-name scan:

| File | Matches |
|---|---:|
| `src/rtdsl/optix_runtime.py` | 108 |
| `src/rtdsl/embree_runtime.py` | 71 |
| `src/native/optix/rtdl_optix_workloads.cpp` | 529 |
| `src/native/optix/rtdl_optix_api.cpp` | 60 |
| `src/native/optix/rtdl_optix_core.cpp` | 51 |
| `src/native/optix/rtdl_optix_prelude.h` | 26 |
| `src/native/embree/rtdl_embree_api.cpp` | 181 |
| `src/native/embree/rtdl_embree_scene.cpp` | 76 |
| `src/native/embree/rtdl_embree_geometry.cpp` | 48 |
| `src/native/embree/rtdl_embree_prelude.h` | 14 |

This confirms Claude's warning: the "RTDL is generic, RayJoin is an app" principle is correct as a target, but existing core/native implementation still carries substantial RayJoin naming debt.

Traceability note: this table records line-based match counts from the focused substring scan.  It is not a unique-symbol count from the `rg -o` extraction command.

## Inventory Summary

v2.14.4 should not invent a new fifth columnar surface.  It should consolidate the following existing surfaces:

| Existing asset | Current role | v2.14.4 decision |
|---|---|---|
| `src/rtdsl/device_column_row_buffer.py` | v2.14.2 generic row-buffer adapter over primitive output columns; has source modes, four-state stream ordering, host-materialization metadata, and partner handoff planning | `promote_via_public_wrapper` as the backbone of `DeviceColumnBuffer` |
| `src/rtdsl/columnar_partner.py` | `DeviceColumnDescriptor` and `PartnerResidentColumnarRecordSet`; descriptor-only partner-resident columnar shape; explicitly lists native-execution blockers | `wrap_and_merge_metadata`; do not expose as a separate competing public API |
| `src/rtdsl/hit_stream_handoff.py` | mature hit-stream/device-column handoff substrate, four-state stream-ordering vocabulary, raw CUDA column wrappers, native output owners | `keep_internal_substrate`; reuse vocabulary and owner model in `DeviceColumnBuffer` |
| `src/rtdsl/neutral_buffer_seam.py` | v2.5 neutral buffer descriptor, ownership/lifetime, CUDA array interface/DLPack classification | `keep_internal_substrate`; source for residency/lifetime derivation rules |
| `src/rtdsl/v2_6_neutral_partner_handoff.py` | neutral handoff planning for CuPy/Numba partners | `wrap` into `PartnerContinuation` planning |
| `src/rtdsl/numba_partner_continuation.py` | Numba operations: segmented count/sum/min/max, grouped vector sum, compact mask, arg reducers, score rows, etc. | `promote_subset` under `PartnerContinuation`; do not overclaim whole operator performance |
| `src/rtdsl/current_prepared_session_residency_profiles.py` | internal registry of prepared-session reuse profiles and claim boundaries | `keep_internal_policy_evidence`; use as precedent for regime metadata |
| `src/rtdsl/optix_runtime.py::run_cuda_lexsort_i64_f64_i64_i64_device` | generic native CUDA/Thrust lexsort used by the RayJoin descriptor consumer path | `promote` as initial `device_order_by` implementation with narrow dtype/key support |
| `src/rtdsl/grouped_reduction.py` | generic grouped-reduction contract metadata | `wrap_internal`; public `device_group_by` depends on POD device-resident proof |
| `src/rtdsl/columnar_aggregate_reference.py` | CPU reference/oracle for columnar grouped aggregates | `keep_reference_oracle` for `device_group_by` verification |
| `src/rtdsl/output_assembly.py` | generic grouped output assembly and materializer | `keep_internal`; useful for app materialization, not `DeviceColumnBuffer` core |
| `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py` | RayJoin app consumer and performance regression route | `consumer_only`; no API evidence except as regression consumer |

## Proposed API Mapping

### `DeviceColumnBuffer`

Decision: `promote_via_public_wrapper`.

Primary substrate:

- `RtdlDeviceColumnRowBuffer`
- `DeviceColumnDescriptor`
- `PartnerResidentColumnarRecordSet`
- `RtdlHitStreamColumnHandoff`
- `RtdlRawCudaColumn`
- neutral buffer descriptors from v2.5/v2.6

Required public contract:

- four-state `producer_consumer_stream_ordering`:

```text
not_proven
same_stream
producer_event_waited_by_consumer
host_synchronized_before_consumer
```

- device-residency derived from actual column interfaces and `materializes_host_rows_for_bridge`;
- no self-declared app flags;
- context-manager/owner retention;
- explicit copy methods for host materialization.

Implementation note:

Do not expose all existing classes.  Create one public wrapper/alias layer, preserve the rich internal metadata, and make the old surfaces internal implementation details.

### `PreparedGeometrySession`

Decision: `wrap`.

Primary substrate:

- `prepared_session_residency.py`
- `current_prepared_session_residency_profiles.py`
- existing OptiX prepared session classes in `optix_runtime.py`
- RayJoin prepared LSI/query-batch app evidence from Goals 5020, 5021, 5036, and 5039

Required public contract:

- explicit regime labels:

```text
cold_cli_one_shot
warm_process_fresh
prepared_base_distinct_query_batch
prepared_replay_same_input_diagnostic
```

- compile/setup vs per-input workspace timing fields;
- no silent promotion of same-input replay to query-many.

Implementation note:

Prepared-session API should be generic and backed by adapters.  Existing RayJoin prepared classes are consumer evidence and legacy implementation substrate, not public names.

### `device_order_by`

Decision: `promote`.

Primary substrate:

- `run_cuda_lexsort_i64_f64_i64_i64_device` in `optix_runtime.py`
- tests `goal5019_native_lexsort_bridge_test.py` and `goal5033_descriptor_consumer_native_lexsort_test.py`

Initial v2.14.4 public scope:

```text
keys: i64, f64, i64, i64
directions: ascending only unless explicitly extended
backend: CUDA/Thrust native helper
output: device-resident order/index column
```

The API may be generic in shape, but the supported dtype/key matrix must be narrow and fail-closed in v2.14.4.  Do not imply arbitrary dtype/count support.

### `device_group_by`

Decision: `keep_internal_until_pod_device_resident_reduce`.

Primary substrate:

- `grouped_reduction.py`
- `columnar_aggregate_reference.py`
- `columnar_partner.py`
- `optix_runtime.py` partner-resident grouped count/sum/min/max/stats symbols
- older grouped/count/reduction tests from v1.5-v2.8, including partner and hit-stream grouped reductions

Blocking evidence:

`columnar_partner.py` currently states:

```text
Current OptiX compatibility payload stores host scalar row_values.
Current OptiX exact filtering and grouped count/sum reductions read host row_values.
Goal2505 descriptors explicitly set native_execution_authorized=False.
```

Therefore, public `device_group_by` is not authorized unless Goal5046 proves:

- CPU reference parity;
- POD execution;
- metadata showing no host row materialization;
- compact device-resident group key/value output.

Allowed v2.14.4 outcomes:

```text
completed_public_device_group_by_segmented_reduce
completed_internal_only_device_group_by_until_device_resident_reduce
blocked_device_group_by_public_due_to_host_row_values
```

### `PartnerContinuation`

Decision: `promote_numba_first`.

Primary substrate:

- `numba_partner_continuation.py`
- `v2_6_neutral_partner_handoff.py`
- `neutral_buffer_seam.py`
- row-buffer partner planning in `device_column_row_buffer.py`

Initial v2.14.4 scope:

- Numba first;
- CuPy allowed as helper/backend validation when already present;
- explicit host fallback only;
- metadata records stream ordering and materialization;
- outputs become `DeviceColumnBuffer` or clearly internal partner buffers.

Do not make v2.14.4 a broad "all partners" release.

## Duplicate Surfaces To Reconcile

| Surface | Problem | Goal5043/5047 direction |
|---|---|---|
| `RtdlDeviceColumnRowBuffer` vs `DeviceColumnDescriptor` | overlapping column metadata with different vocabulary | public `DeviceColumnBuffer` wrapper uses one schema, adapters translate old surfaces |
| `RtdlHitStreamColumnHandoff` vs row-buffer | hit-stream has richer owner/stream metadata | preserve hit-stream vocabulary; do not down-convert to weaker states |
| `PartnerResidentColumnarRecordSet` vs Numba continuation descriptors | two partner-facing descriptor families | `PartnerContinuation` consumes `DeviceColumnBuffer`, not a third descriptor object |
| grouped reduction contracts vs columnar aggregate reference | contract and CPU oracle separated | keep both; public group-by only after device-resident execution exists |
| RayJoin app flags vs prepared-session concepts | app owns performance route flags | public session/query-batch API replaces flags only after regression gate passes |

## RayJoin Naming Debt Remediate-Or-Defer Table

Goal5042 found no new implementation need, but it did find existing debt that must be tracked before v2.14.4 can honestly claim a generic public API.  The decision here is conservative: do not rename native ABI in Goal5042; wrap public generic aliases now, defer native rename until a dedicated compatibility goal.

| Symbol family | Examples | Current status | Decision | Rationale |
|---|---|---|---|---|
| OptiX point-location native symbols | `rtdl_optix_prepare_rayjoin_cdb_point_location_2d`, `rtdl_optix_run_prepared_rayjoin_cdb_point_location_2d`, `rtdl_optix_prepared_rayjoin_cdb_point_location_2d_device_face_id_columns`, destroy/count/timing variants | core/native ABI is RayJoin-named | `wrap_with_public_alias_defer_native_rename` | Semantics are now directed segment point-location.  Immediate native rename risks ABI break; public API must use generic names. |
| OptiX point-location Python classes | `PreparedOptixRayjoinCdbPointLocation2D`, `PreparedOptixRayjoinCdbPointLocationPoints2D` | generic aliases already exist (`PreparedOptixDirectedSegmentPointLocation2D`, points alias) | `wrap_with_public_alias_defer_native_rename` | Keep generic aliases as public path; old class names become internal/deprecated debt. |
| OptiX RayJoin CDB packed structs imported from Embree runtime | `_RtdlRayjoinCdbSegment`, `_RtdlRayjoinCdbScaledPoint`, `_RtdlRayjoinCdbPointLocationRow`, `PackedRayjoinCdbSegments`, `PackedRayjoinCdbScaledPoints` | ctypes ABI and helper packing are RayJoin-named | `wrap_with_public_alias_defer_native_rename` | Public API should expose directed segment faces / scaled query points; struct rename needs coordinated native/Python ABI work. |
| OptiX LSI predicate alias | `_PLANAR_MAP_LSI_LEGACY_NATIVE_ALIAS = "rayjoin_lsi"`, `RTDL_OPTIX_SEGMENT_PAIR_PREDICATE` | public front door exists but internal predicate name remains RayJoin-shaped | `wrap_with_public_alias_defer_native_rename` | v2.14.4 can expose planar-map LSI public API; native predicate should eventually become `planar_map_lsi`. |
| OptiX RayJoin env vars | `RTDL_RAYJOIN_CDB_QUERY_MAP_ID`, `RTDL_RAYJOIN_CDB_SCALE_*`, `RTDL_RAYJOIN_CDB_GROUP_*`, `RTDL_RAYJOIN_CDB_ALLOW_EQUAL_TIES` | process-global bridge variables | `keep_internal_with_debt` | Must not be public API.  Future dedicated goal should replace with explicit native parameter structs. |
| OptiX internal native structs/functions | `RayjoinCdbPointLocationParams`, `RayjoinCdbSegment`, `RayjoinCdbPointLocationKernelSrc`, `RayjoinCdbDuplicateHalfEdgeKey`, `rayjoin_cdb_*` helpers | internal implementation names in native code | `keep_internal_with_debt` | Acceptable only as private implementation debt in v2.14.4 docs; native-symbol scan must record them. |
| Embree point-location native symbols | `rtdl_embree_prepare_rayjoin_cdb_point_location_2d`, run/count/destroy/timing variants | Embree ABI is RayJoin-named | `keep_internal_with_debt` | Embree is not the v2.14.4 performance gate.  Do not rename in this release; no public promotion under RayJoin names. |
| Embree LSI symbols | `rtdl_embree_run_rayjoin_lsi_aabb_refined_segment_pair_intersections`, count variant, `RTDL_EMBREE_RAYJOIN_LSI_AABB_PAD` | legacy CPU/Embree path names | `keep_internal_with_debt` | Not in v2.14.4 public CUDA device-column API; track in Goal5050 native scan. |
| Embree packed/row Python classes | `PreparedEmbreeRayjoinCdbPointLocation2D`, `PackedRayjoinCdbSegments`, `PackedRayjoinCdbScaledPoints` | legacy compatibility layer | `keep_internal_with_debt` | Existing aliases may stay; public v2.14.4 docs should not expose these as current API. |
| RayJoin app code | `src/rtdsl/rayjoin_overlay.py`, `Paper-reproduction-apps/rayjoin-paper/*` | app / paper reproduction implementation | `move_to_app_boundary_already` | App may remain RayJoin-named.  It must not be used as public RTDL API evidence except as consumer/regression evidence. |
| Legacy DSL aliases | `backend="rayjoin"`, `lower_to_rayjoin` tests | backwards-compatible legacy front door | `keep_internal_or_legacy_with_debt` | Not part of v2.14.4 device-columnar API.  Do not feature in new docs. |

## Public API Promotion Decisions

| API concept | v2.14.4 exposure | Reason |
|---|---|---|
| `DeviceColumnBuffer` | public wrapper | Existing row-buffer/hit-stream/descriptor assets are real and generic, but need one stable surface. |
| `PreparedGeometrySession` | public wrapper | Prepared-session/regime accounting is central to avoiding replay/query-many confusion. |
| `device_order_by` | public | Native CUDA/Thrust lexsort is generic, hardware-proven, and load-bearing in Goal5039. |
| `device_group_by` | internal unless Goal5046 proves device-resident reduce | Existing grouped assets are broad, but current blocker list says host `row_values` still participate. |
| `PartnerContinuation("numba")` | public first partner | Numba handoff is mature enough as a first partner route; keep fallback explicit and measured. |

## Verification Status

This goal performed no runtime changes and therefore no runtime test run is required.  Verification for this inventory is document-level:

- existing assets identified;
- duplicate surfaces identified;
- RayJoin-named core/native debt classified with remediate-or-defer decisions;
- `device_group_by` public exposure blocked unless Goal5046 produces POD device-resident reduce proof;
- `device_order_by` remains public target;
- RayJoin app remains consumer/regression evidence, not API evidence.

## Next Goal

Proceed to Goal5043 only after external review of this inventory:

```text
Goal5043 - Public DeviceColumnBuffer Contract
```

Goal5043 must implement the public buffer contract without weakening the existing four-state stream-ordering vocabulary or self-declaring device residency.
