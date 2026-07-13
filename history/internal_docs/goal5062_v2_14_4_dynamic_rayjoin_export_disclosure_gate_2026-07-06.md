# Goal5062 - v2.14.4 Dynamic RayJoin Export Disclosure Gate

Date: 2026-07-06

Status:

```text
completed_dynamic_rayjoin_export_disclosure_gate__bf1_addressed
```

## Purpose

Goal5062 addresses the blocking finding from the consolidated external review:

```text
BF-1: legacy RayJoin public-export enumeration is incomplete, and the gate that
enforces it is hardcoded to the undercount.
```

The review was correct.  Goal5059 originally named only four RayJoin-named
exports.  A dynamic scan of `rtdsl.__all__` shows seventeen RayJoin-named public
exports.

## Current Dynamic Export Set

The current `rtdsl.__all__` RayJoin-named export set is:

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

## Classification

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

All of these are:

```text
legacy public exports / compatibility debt or paper-app support; not new
v2.14.4 public generic API
```

Equivalently:

```text
legacy public exports / compatibility debt; not new v2.14.4 public generic API
```

## Gate Change

`scripts/goal5053_v2144_release_preflight.py` no longer trusts a static four-name
list.  It now derives the RayJoin-named exports by scanning `src/rtdsl/__init__.py`
from `__all__` onward for quoted names containing `rayjoin`.

The preflight check:

```text
legacy_rayjoin_public_exports_disclosed
```

now reports:

```text
exports
expected_exports
missing_expected_exports_from_rtdsl_all
unexpected_rayjoin_exports_from_rtdsl_all
missing_report_phrases
```

This means a newly added RayJoin-named public export cannot silently pass the
release gate.  It will appear as an unexpected export until it is either removed
or classified in the boundary reports.

## Reports Updated

The following reports now enumerate the full dynamic set and classify it:

```text
history/internal_docs/goal5050_v2_14_4_public_private_boundary_audit_2026-07-06.md
history/internal_docs/goal5051_v2_14_4_api_consolidation_closeout_packet_2026-07-06.md
history/internal_docs/goal5059_v2_14_4_legacy_public_export_boundary_amendment_2026-07-06.md
```

## Not Authorized

```text
all_public_exports_rayjoin_free
legacy_export_debt_removed
RayJoin_exports_are_private
v2_14_4_public_generic_api_includes_rayjoin_exports
```

## Exit Label

```text
completed_dynamic_rayjoin_export_disclosure_gate__bf1_addressed
```
