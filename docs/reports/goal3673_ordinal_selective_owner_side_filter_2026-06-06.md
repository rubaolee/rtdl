# Goal3673 Ordinal-Selective Owner-Side Filter

Date: 2026-06-06

Status: implemented as a generic Python/CuPy continuation and validated on an
RTX A5000 full-county RayJoin PIP probe.

## Why This Goal Exists

Goal3671 proved that side-aware topology ownership can repair the two
full-county CDB extras in the tuned fast PIP candidate stream:

```text
candidate rows: 47,264
exact rows:     47,262
extras:         (893, 16312), (894, 16312)
```

The first attempt to derive owner side for every source point exposed a new
identity problem: public CDB point ids are not sufficient as lookup keys because
the public id may be repeated across input occurrences. This goal adds the
missing ordinal-aware contract and then tests the design choice directly.

## What Changed

`filter_closed_shape_membership_candidate_columns_by_owner_face_side_columns(...)`
and
`filter_closed_shape_membership_candidate_columns_by_owner_face_side_cupy(...)`
now accept optional generic identity columns:

- `candidate_point_ordinals`
- `candidate_shape_ordinals`
- `topology_shape_ordinals`
- `owner_point_ordinals`

When ordinals are supplied, lookup identity uses input/prepared ordinals while
the output still preserves public `point_id` and `shape_id` columns.

Added
`run_selective_closed_shape_owner_face_side_membership_pipeline_cupy(...)`, a
generic selective-repair continuation:

- non-selected candidate rows pass through unchanged;
- selected rows are filtered by caller-supplied `(owner_face_id, owner_side)`;
- rows may be selected by public point id or by input point ordinal;
- duplicate public ids are safe when the caller selects by ordinal;
- no CDB, RayJoin, map, or GIS ownership policy enters the native engine.

The owner-face priority pipeline contract now records that side-aware filtering
uses public ids by default, or ordinals when supplied.

## A5000 Evidence

Artifacts:

```text
docs/reports/goal3673_rayjoin_ordinal_owner_side_probe_a5000/full_county_ordinal_owner_side_route_probe.json
docs/reports/goal3673_rayjoin_ordinal_owner_side_probe_a5000/full_county_selective_ordinal_owner_side_route_probe.json
```

The full-county dataset was:

```text
/root/rtdl_goal3671_topology/data/rayjoin_public_cdb/br_county_start0_count16545.cdb
```

GPU:

```text
NVIDIA RTX A5000, driver 580.126.09
```

### Negative Probe: All-Point Owner-Side Filtering

All-point owner-side filtering is not a universal replacement for membership.
It over-filters valid rows:

| Measure | Value |
| --- | ---: |
| Exact rows | 47,262 |
| Candidate rows before filter | 47,264 |
| Filtered rows | 22,639 |
| Extra rows after filter | 0 |
| Missing rows after filter | 24,623 |
| Multiset parity | false |

This is the design lesson: owner-side topology is a selective repair mechanism
for ambiguous rows, not the entire point/closed-shape membership predicate.

### Positive Probe: Selective Ordinal-Aware Repair

The selective ordinal-aware side filter repaired only the known ambiguous input
ordinals:

| Public point id | Input ordinal |
| ---: | ---: |
| 893 | 892 |
| 894 | 893 |

Result:

| Measure | Value |
| --- | ---: |
| Exact rows | 47,262 |
| Candidate rows before filter | 47,264 |
| Selected candidate rows | 4 |
| Passthrough candidate rows | 47,260 |
| Removed rows | `(893, 16312)`, `(894, 16312)` |
| Filtered rows | 47,262 |
| Extra rows after filter | 0 |
| Missing rows after filter | 0 |
| Multiset parity | true |

This closes the immediate `47264 != 47262` full-county mismatch as a generic
selective continuation. It does not yet authorize automatic default route
selection because the caller still supplies the selected ambiguity set and the
owner-side derivation policy.

## Boundary

This is major v2.9 performance-direction work, not v2.9 closeout.

Blocked claims remain blocked:

- release authorization;
- public v2.9 speedup claims;
- RTDL-beats-RayJoin wording;
- RayJoin paper reproduction wording;
- broad RT-core speedup wording;
- true zero-copy wording;
- native default route selection.

The engine remains app-agnostic: RTDL/OptiX emits generic candidate id columns
plus input/prepared ordinals; the caller supplies ambiguity ordinals and
owner-face side policy; the CuPy continuation filters only those selected rows.

## Validation

Local:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3673_ordinal_selective_owner_side_filter_test tests.goal3671_side_aware_owner_face_filter_test tests.goal3672_gemini_review_goal3671_side_aware_owner_face_filter_test tests.goal3602_v2_9_benchmark_status_after_resident_evidence_test
```

Pod:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal3671_topology/build/librtdl_optix.so python3 -m unittest tests.goal3673_ordinal_selective_owner_side_filter_test tests.goal3671_side_aware_owner_face_filter_test
```

Reproducible positive probe:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_goal3671_topology/build/librtdl_optix.so RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS=1e-9 python3 scripts/goal3673_rayjoin_selective_ordinal_owner_side_probe.py --dataset data/rayjoin_public_cdb/br_county_start0_count16545.cdb --output docs/reports/goal3673_rayjoin_ordinal_owner_side_probe_a5000/full_county_selective_ordinal_owner_side_route_probe.json --selected-point-id 893 --selected-point-id 894 --max-rows 1000000
```

## Next Major Direction

The next performance step is not another epsilon knob. It is a generic
ambiguity-set derivation contract:

```text
candidate stream + topology/boundary signals -> selected input ordinals
```

That selector must remain caller/data-layer policy or a generic ambiguity signal
primitive. It must not become hidden CDB/RayJoin logic in the native engine.
