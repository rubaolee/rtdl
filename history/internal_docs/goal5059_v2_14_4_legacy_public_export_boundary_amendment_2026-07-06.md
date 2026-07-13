# Goal5059 - v2.14.4 Legacy Public Export Boundary Amendment

Date: 2026-07-06

Status:

```text
completed_legacy_public_export_boundary_amendment__release_still_review_blocked
```

## Purpose

Goal5059 amends the v2.14.4 public/private boundary after external review found
a real overclaim in Goal5050/Goal5051.

The principle remains:

```text
RTDL is the generic system. RayJoin is an app on top of RTDL.
```

However, the implementation still exposes RayJoin-named Python helpers, data
types, and app-support registries through `rtdsl.__all__`.  These names cannot
be described as private or absent from the public module namespace.

## Finding

The following names remain in `rtdsl.__all__`:

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

Classification:

```text
legacy public exports / compatibility debt; not new v2.14.4 public generic API
```

This is a boundary wording and governance fix, not a runtime optimization and
not a performance claim.

## Why We Do Not Remove Them In This Goal

Removing these exports in v2.14.4 would be a compatibility break.  The safer
release-staging action is:

1. disclose the exports honestly;
2. exclude them from the new v2.14.4 public generic API surface;
3. keep them out of the contract-first interactive surface where possible;
4. require a later export-hygiene or deprecation plan before removal.

## Amendments Applied

### Goal5050

`history/internal_docs/goal5050_v2_14_4_public_private_boundary_audit_2026-07-06.md`
now includes a Goal5059 amendment that names the RayJoin-named legacy public
exports and classifies them as compatibility debt or paper-app support exports.

### Goal5051

`history/internal_docs/goal5051_v2_14_4_api_consolidation_closeout_packet_2026-07-06.md`
now includes the same distinction between:

- new v2.14.4 public generic API names; and
- legacy RayJoin-named public exports retained for compatibility.

### Release Preflight

`scripts/goal5053_v2144_release_preflight.py` now includes the machine-readable
check:

```text
legacy_rayjoin_public_exports_disclosed
```

That check blocks if the legacy exports exist but the boundary reports fail to
classify them as:

```text
legacy public exports / compatibility debt
```

## Public Generic API Surface Remains

The new v2.14.4 public generic API surface remains:

```text
DeviceColumnBuffer
PreparedGeometrySession
device_order_by
NumbaPartnerContinuation
```

The following remain not authorized:

```text
device_group_by_public_ready
v2_14_4_speedup_claim
author_parity_claim
true_zero_copy_claim
all_public_exports_rayjoin_free
all_internal_symbols_rayjoin_free
public_release_ready_without_review
```

## Verification

Added test:

```text
tests/goal5059_v2144_legacy_public_export_boundary_test.py
```

The test verifies:

- RayJoin-named helpers, types, and app-support registries still exist in
  `rtdsl.__all__`;
- Goal5050, Goal5051, and this Goal5059 report disclose the dynamically scanned
  RayJoin-named public exports as legacy public
  exports / compatibility debt;
- the release preflight includes `legacy_rayjoin_public_exports_disclosed`;
- the release preflight now requires Goal5059 and external review for Goal5059.

## Exit Label

```text
completed_legacy_public_export_boundary_amendment__release_still_review_blocked
```
