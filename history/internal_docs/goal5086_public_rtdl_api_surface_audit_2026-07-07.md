# Goal5086 Public RTDL API Surface Audit

Date: 2026-07-07

## Verdict Label

```text
completed_public_rtdl_api_surface_audit_for_two_paper_apps
```

## Purpose

Goal5086 audits the RTDL language/system surface exercised by the first two
paper-reproduction apps:

- RayJoin paper app
- RT-BarnesHut paper app

The goal is to separate:

- APIs that are ready to be documented as public RTDL language features,
- APIs that are public-contract but still experimental or narrowly bounded,
- legacy/internal names that must not be promoted,
- app-owned assets that must remain outside RTDL core.

This is an audit and design-boundary goal. It adds no runtime behavior.

## Source Evidence

The audit checked:

```text
src/rtdsl/__init__.py
src/rtdsl/optix_runtime.py
src/rtdsl/device_column_row_buffer.py
src/rtdsl/device_ordering.py
src/rtdsl/aggregate_hierarchy.py
Paper-reproduction-apps/rayjoin-paper/
Paper-reproduction-apps/rt-barneshut-paper/
```

Key public exports observed:

```text
prepare_planar_map_lsi_2d_optix
prepare_planar_map_point_location_2d_optix
prepare_directed_segment_point_location_2d_optix
device_column_buffer
device_column_row_buffer_from_native_pair_columns
device_column_row_buffer_from_point_location_id_columns
device_order_by
describe_device_order_by_contract
aggregate_hierarchy_3d
prepare_aggregate_hierarchy_3d
SizeDistanceOpening
ContinuationPayloadOpening
LeafOnlyOpening
aggregate_frontier_reduce_reference_3d
aggregate_frontier_reduce_numba_3d
describe_aggregate_hierarchy_3d_contract
```

Legacy or debt-bearing exports observed:

```text
prepare_rayjoin_cdb_point_location_2d_optix
prepare_rayjoin_cdb_point_location_2d_embree
```

The audit also confirmed that `optix_runtime.py` still contains legacy
RayJoin-named native internals behind some generic public front doors. That is
a naming/implementation debt, not a new regression.

## Classification

### A. Public And Documentable Now

These APIs can be documented as RTDL language features, with their current
scope and backend limits stated explicitly.

#### Planar-map LSI

```text
prepare_planar_map_lsi_2d_optix
```

Reason:

- used by RayJoin Section 5.2 and 5.7 paths,
- exposed under generic planar-map naming,
- does not require users to call bundled RayJoin overlay helpers,
- suitable as a public OptiX-backed planar-map LSI primitive.

Required wording:

- OptiX backend only in the current public route,
- do not claim whole-app RayJoin speedup from this primitive alone,
- do not hide the historical internal native naming debt.

#### Planar-map point location / PIP

```text
prepare_planar_map_point_location_2d_optix
prepare_directed_segment_point_location_2d_optix
```

Reason:

- used by RayJoin Section 5.3 and 5.7 paths,
- users no longer set legacy `RTDL_RAYJOIN_CDB_*` variables directly,
- public API boundary is generic planar-map / directed point-location.

Required wording:

- OptiX route only for this prepared public path,
- historical native bridge names remain implementation debt,
- PIP correctness claims must remain tied to tested contracts and regressions.

#### Generic aggregate hierarchy, reference execution

```text
aggregate_hierarchy_3d
prepare_aggregate_hierarchy_3d
SizeDistanceOpening
ContinuationPayloadOpening
LeafOnlyOpening
aggregate_frontier_reduce_spec_3d
aggregate_frontier_reduce_reference_3d
describe_aggregate_hierarchy_3d_contract
validate_aggregate_hierarchy_3d_contract
```

Reason:

- introduced through RT-BarnesHut but no longer app-named,
- has independent non-RT-BarnesHut consumers for genericity,
- supports multiple opening policies and reducers,
- reference executor is implemented and contract-checked.

Required wording:

- reference CPU executor is the stable documented execution path,
- optional Numba parity/prototype may be mentioned only as optional,
- no native CUDA/OptiX/Embree/HIPRT backend is authorized,
- no full RT-BarnesHut paper reproduction claim follows from this API.

### B. Public-Contract But Experimental / Advanced

These APIs exist and are useful, but should be documented as advanced or
experimental until more cross-app validation and release gates are complete.

#### Device column buffers and row-buffer handoff

```text
DeviceColumnBuffer
RtdlDeviceColumnRowBuffer
device_column_buffer
device_column_row_buffer_from_native_pair_columns
device_column_row_buffer_from_point_location_id_columns
prepare_device_column_row_buffer_partner_handoff
plan_device_column_row_buffer_partner_handoff
```

Reason:

- provides typed primitive-output columns, lifetime metadata, stream-ordering
  metadata, and host-materialization status,
- reused by RayJoin device-column experiments,
- explicitly marks `app_specific_schema_allowed: false`.

Boundary:

- do not call it true zero-copy,
- do not claim speedup or whole-app speedup,
- do not document as the default route for normal users yet,
- keep examples narrow and metadata-driven.

#### Device ordering

```text
device_order_by
device_order_by_reference_i64_f64_i64_i64
describe_device_order_by_contract
validate_device_order_by_contract
```

Reason:

- generic lexicographic ordering over typed columns,
- supports an explicit final tie key,
- used by RayJoin device-column route to replace an app-local ordering kernel.

Boundary:

- `describe_device_order_by_contract()` currently reports
  `release_authorized: False`,
- only the `i64_f64_i64_i64_lex` signature is supported,
- `device_group_by` is not public,
- no public speedup or true-zero-copy wording is authorized.

Therefore `device_order_by` should be treated as public-contract /
experimental until the release gate is explicitly upgraded.

#### Aggregate hierarchy optional Numba executor

```text
aggregate_frontier_reduce_numba_3d
run_aggregate_frontier_reduce_numba_3d
```

Reason:

- parity-tested against the CPU reference route,
- useful to app authors and internal validation,
- not a native backend and not a speedup claim.

Boundary:

- optional runtime,
- no native backend completion,
- no performance claim,
- no paper-reproduction closure by itself.

### C. Legacy / Compatibility / Naming Debt

These names should not be promoted as primary public language features.

```text
prepare_rayjoin_cdb_point_location_2d_optix
prepare_rayjoin_cdb_point_location_2d_embree
rtdsl.rayjoin_overlay
legacy RayJoin-named native CDB point-location symbols
legacy rayjoin_lsi native predicate alias
```

Reason:

- they expose app identity or historical implementation naming,
- some generic public APIs still forward into these internals,
- using them as public examples would contradict the "RTDL is generic,
  RayJoin is an app" principle.

Required treatment:

- keep for compatibility or internal implementation only,
- do not use in new user-facing examples,
- keep naming-debt visible in release-boundary docs,
- future cleanup should rename or wrap native symbols without changing the
  tested contracts.

### D. App-Owned Assets

These must remain in paper-app packages and must not be promoted to RTDL core.

#### RayJoin app-owned assets

```text
CDB parsing and paper-workload selection
AuthorOfficial / patched-author comparison machinery
output-chain text formatting
RayJoin Section 5.2 / 5.3 / 5.7 workflow scripts
overlay-specific carrier assembly and descriptor consumer choices
paper-specific expected counts and representative dataset choices
```

#### RT-BarnesHut app-owned assets

```text
author prepared-state binary readers
patched-author comparator runners
sentinel / payload normalization adapters
force-output bridge and text formatting
same-input gate artifacts
phase-boundary and performance envelopes
```

Reason:

- these encode paper-specific reproduction protocol or author-comparator
  behavior,
- they are valuable paper-app assets but not language primitives,
- moving them into core would turn RTDL into an app-specific toolkit.

## Cross-App Conclusions

The two paper apps validate two different generic RTDL directions:

```text
RayJoin        -> planar-map primitives + device-column/order-by pipeline
RT-BarnesHut   -> aggregate hierarchy + opening/reducer execution contract
```

The common system lesson is not "promote every helper." The common lesson is:

```text
RTDL should expose generic spatial operators and typed continuation surfaces;
paper apps should own parsing, comparator protocol, output formatting, and
paper-specific workflow.
```

## Public Documentation Recommendations

For v2.14.5, public docs should prioritize:

1. A planar-map LSI/PIP example using only generic public front doors.
2. An `AggregateHierarchy3D` reference example using a small synthetic
   hierarchy and `aggregate_count`.
3. A paper-app status page that keeps reproduction, performance, and boundary
   columns separate.

Public docs should not yet prioritize:

1. `device_group_by` (not public).
2. `device_order_by` as a release-ready stable API (contract exists, release
   gate is still false).
3. legacy `rayjoin_*` exports as first-class APIs.
4. any "zero-copy" or whole-paper speedup wording.

## Next Recommended Goal

Goal5087 should create a unified paper-app skeleton:

```text
Paper-reproduction-apps/<paper-name>/
  README.md
  manifest.json
  scripts/
  src or app modules
  data/README.md
  results/README.md
```

The skeleton should require every paper app to declare:

- RTDL public APIs exercised,
- app-owned code,
- comparator/source of truth,
- reproduction scope,
- performance regime,
- forbidden claims.

## What This Does Not Close

This audit does not:

- make `device_order_by` release-authorized,
- make `device_group_by` public,
- remove RayJoin-named native implementation debt,
- authorize native aggregate hierarchy backends,
- claim RT-BarnesHut full paper reproduction,
- claim RayJoin broad all-input performance.
