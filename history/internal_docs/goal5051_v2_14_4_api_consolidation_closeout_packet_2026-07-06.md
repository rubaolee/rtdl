# Goal5051 - v2.14.4 API Consolidation Closeout Packet

Date: 2026-07-06

Status:

```text
completed_v2_14_4_api_consolidation_closeout_packet__review_debt_pending
```

## Purpose

Goal5051 closes the v2.14.4 implementation arc as an internal API
consolidation packet.

v2.14.4 is not another RayJoin optimization cycle.  Its purpose is to turn the
reusable system pieces proven during the RayJoin v2.14.3 work into a coherent
RTDL public API surface:

```text
RTDL primitive output -> typed device columns -> prepared/session metadata
-> generic ordering -> partner continuation
```

RayJoin remains an app and a regression/proof workload, not the system identity.

## Amendment - Goal5059 Legacy Public Export Boundary

External review found that the original closeout wording blurred two categories:

- new v2.14.4 public generic API names; and
- historical RayJoin-named Python exports that still remain in `rtdsl.__all__`
  for compatibility.

The following names are **legacy public exports**:

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

This packet should not be read as claiming that every RayJoin-named Python
export is private or absent from the public module namespace.  v2.14.4 only
claims that the **new** public API surface is generic and claim-bounded.

## Implemented Public Surface

The v2.14.4 public device-columnar prepared-pipeline surface is:

```text
DeviceColumnBuffer
PreparedGeometrySession
device_order_by
NumbaPartnerContinuation
```

These surfaces are intentionally narrow:

- `DeviceColumnBuffer` carries typed primitive-output columns plus ownership,
  lifetime, stream-ordering, and host-materialization metadata.
- `PreparedGeometrySession` records prepared base/query-batch regime metadata
  and keeps cold, warm, replay, and query-batch labels separate.
- `device_order_by` exposes a generic, fail-closed ordering contract over typed
  columns.  v2.14.4 supports the narrow proven `i64,f64,i64,i64` lexicographic
  signature.
- `NumbaPartnerContinuation` exposes approved Numba partner continuations over
  `DeviceColumnBuffer` inputs.

## Goal Chain

| Goal | Result |
|---|---|
| Goal5041 | v2.14.4 device-columnar prepared pipeline plan accepted with conditions |
| Goal5042 | existing asset inventory: consolidate v2.x assets rather than invent a fifth surface |
| Goal5043 | public `DeviceColumnBuffer` contract |
| Goal5044 | public `PreparedGeometrySession` contract |
| Goal5045 | public `device_order_by` contract |
| Goal5046 | `device_group_by` kept internal for v2.14.4 |
| Goal5047 | public `NumbaPartnerContinuation` contract |
| Goal5048 | non-RayJoin genericity proof for public Numba partner API |
| Goal5049 | RayJoin app sort path migrated to public `device_order_by` |
| Goal5050 | public/private boundary audit |

Recent implementation commits:

```text
0537b7bd0 Add public DeviceColumnBuffer contract
df8c28b11 Add public prepared geometry session contract
6e2feef1f Add public device_order_by contract
3d6f3055f Keep device_group_by internal for v2.14.4
49c1e5f67 Add public Numba partner continuation API
7c126edaa Prove public Numba partner API genericity
d8d3897bc Route RayJoin sort through public device_order_by
848390f4f Audit v2.14.4 public private boundaries
```

## Verification

Local adjacent-gate command:

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal5050_v2144_public_private_boundary_audit_test tests.goal5049_rayjoin_public_v2144_surface_migration_test tests.goal5048_non_rayjoin_numba_partner_public_api_genericity_test tests.goal5047_numba_partner_continuation_public_api_test tests.goal5046_device_group_by_public_readiness_decision_test tests.goal5045_public_device_order_by_contract_test tests.goal5044_public_prepared_geometry_session_contract_test tests.goal5043_public_device_column_buffer_contract_test
```

Result:

```text
Could not find platform independent libraries <prefix>
.........s...........................
----------------------------------------------------------------------
Ran 37 tests in 0.101s

OK (skipped=1)
```

The skipped test is the optional live OptiX + Numba CUDA smoke for the public
Numba partner wrapper.  It remains a POD debt before any end-to-end runtime or
performance claim can cite that wrapper.

## What Changed For A User

Before v2.14.4, a user had to reason about scattered lower-level pieces:

```python
row_view = primitive.run_pair_id_rows()
columns = row_view.to_numpy_columns()
raw_native_sort(...)
run_numba_some_helper(...)
```

v2.14.4 turns that into a clearer system shape:

```python
buffer = rtdl.device_column_buffer(
    {"edge_key": edge, "dist_key": dist, "tie_key": tie, "order_key": order},
    producer="my_spatial_primitive",
    producer_consumer_stream_ordering="same_stream",
)

ordered = rtdl.device_order_by(
    buffer,
    keys=("edge_key", "dist_key", "tie_key", "order_key"),
    backend="native_cuda",
)

plan = rtdl.numba_partner_continuation(
    operation=rtdl.NUMBA_UINT32_EQUAL_MASK_OPERATION,
    input_buffer=buffer,
    input_bindings={"values": "edge_key"},
    scalar_inputs={"target": 7},
)

result = rtdl.run_numba_partner_continuation(plan)
```

The important programming change is not a new RayJoin helper.  The important
change is that RTDL now has named public contracts for device-column ownership,
ordering, prepared-session regime accounting, and Numba partner continuation.

## Performance Boundary

v2.14.4 does not change the v2.14.3 performance headline.

The locked v2.14.3 / Goal5040 boundary remains:

```text
RTDL prepared binary route, top4 six-batch sum: 0.328842s
AuthorOfficial core phases, top4:                0.187042s
Ratio:                                           1.76x slower
```

The v2.14.4 API work is allowed to preserve this baseline, but not to claim a
new speedup without a new same-regime, same-data benchmark.

Forbidden performance wording:

```text
v2.14.4 makes RayJoin faster
v2.14.4 reaches author parity
v2.14.4 proves true zero-copy
v2.14.4 replaces RT traversal with Numba
```

## Boundary Decisions

### device_group_by

`device_group_by` is not public in v2.14.4.

Reason:

```text
existing grouped/segmented Numba assets still have host row/value blockers and
do not yet provide a public device-resident grouped-reduce contract.
```

### Legacy grouped/segmented exports

Historical lower-level grouped/segmented Numba symbols still exist in
`rt.__all__`.  They are documented as export-hygiene debt.  They are not part of
`NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS`, and trying to route their
operation values through the new public Numba partner API fails closed.

### RayJoin-named native symbols

Some lower-level native/OptiX symbols retain RayJoin-era names, including the
CDB point-location bridge and the legacy LSI native alias.  These are deferred
native-symbol rename debts, not public API names.

Some RayJoin-named Python helpers also remain as legacy public exports for
compatibility:

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

Those names are compatibility debt or RayJoin paper-app support exports and are
not part of the new v2.14.4 public generic API surface.

Allowed wording:

```text
Public API names are generic. Some lower-level native symbols retain RayJoin-era
names for compatibility and are not user-facing public contracts.
```

Amended wording for Python exports:

```text
Some RayJoin-named Python helpers remain legacy public exports for compatibility.
They are compatibility debt or paper-app support exports, not new v2.14.4
public generic API contracts.
```

Forbidden wording:

```text
All core/internal symbols are RayJoin-free.
```

## Review Debt

The user explicitly authorized accumulating a few review debts before pausing.
Open review debts:

```text
Goal5048 external review
Goal5049 external review
Goal5050 external review
Goal5051 external review
```

These debts block public release wording, but do not block local internal
implementation work.

## POD Debt

Open POD debts:

```text
POD CUDA smoke for public NumbaPartnerContinuation wrapper
POD runtime check for RayJoin app path after device_order_by public migration
```

Until those are run, no end-to-end performance claim may cite the new public
wrapper or migrated app path.

## Closeout Position

v2.14.4 is internally coherent as an API consolidation milestone:

- public surfaces are named, narrow, and claim-bounded;
- RayJoin has begun migrating to those public surfaces as an app;
- at least one non-RayJoin shape checks the Numba partner API;
- `device_group_by` is intentionally held back;
- legacy naming debts are documented instead of hidden.

Recommended next actions:

1. retire the accumulated review debt;
2. run POD CUDA smoke for the public Numba partner wrapper;
3. run one POD app-path check for the migrated `device_order_by` route;
4. only then prepare any user-facing v2.14.4 release note.
