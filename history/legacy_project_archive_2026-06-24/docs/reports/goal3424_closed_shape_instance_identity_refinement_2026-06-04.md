# Goal3424 Closed-Shape Instance-Identity Refinement

Status: implemented with pod evidence in
`docs/reports/goal3424_closed_shape_instance_identity_refinement_probe_2026-06-04.json`.

## Purpose

Goal3424 corrects the interpretation of Goals3421-3422. The public RayJoin CDB
contains duplicate public point ids and duplicate public closed-shape ids. The
previous CuPy refinement helper treated public ids as unique lookup keys, so it
could refine the wrong point/shape instance even though the RT candidate stream
was conservative.

The generic v2.8 fix is not app-specific topology logic. It is an instance-aware
typed relation stream:

```text
public id columns:       point_id, shape_id
instance identity cols:  point_ordinal, shape_ordinal
```

Public ids remain the grouping/output contract. Ordinals let a partner refine
against the exact input point row and prepared shape row that produced the RT
candidate.

## Implementation

- `RtdlNativeDevicePairColumns` was extended append-only with
  `left_ordinals_device_ptr` and `right_ordinals_device_ptr`.
- The OptiX prepared point/closed-shape candidate producer fills those ordinal
  columns as `point_index_offset + pidx` and `prim`.
- `OptixNativeDevicePairColumnOutput.as_cupy_columns()` now exposes optional
  ordinal columns when present.
- `rtdsl.refine_closed_shape_membership_candidate_columns_exact_cupy(...)`
  keeps its legacy public-id lookup mode for old streams, but switches to
  instance-ordinal lookup when `point_ordinal` and `shape_ordinal` are present.
- Host exact refinement also has a generic bbox fail-closed guard before GEOS or
  fallback predicates can accept a point/shape row.

## Pod Result

Full public RayJoin county CDB, NVIDIA RTX A5000, 16,545 probe points and
15,700 closed shapes:

| Path | Pair rows | Pair relation to host | Group relation to host |
| --- | ---: | --- | --- |
| Host exact oracle | 47,262 | authority | authority |
| RT device predicate candidates | 47,570 | 0 missing, 308 extra | conservative superset |
| RT candidates + CuPy simple-ring refine with instance columns | 47,262 | exact multiset match | exact grouped-count match |

The dataset has duplicate public ids:

| Input | Records | Unique public ids | Duplicate public ids | Max multiplicity |
| --- | ---: | ---: | ---: | ---: |
| Points | 16,545 | 16,480 | 65 | 2 |
| Closed shapes | 15,700 | 15,640 | 60 | 2 |

The corrected interpretation:

- Goal3421's 217 missing rows were caused by public-id lookup collapse in the
  partner helper, not by an inherent GEOS-vs-simple-ring topology gap on this
  dataset.
- Goal3422 remains useful as a warning: public ids are not always geometry
  instance identities. Partner/refinement paths must carry both.
- The 308 RT broad-phase extras are now removed on device by the partner
  predicate.

## Boundary

- Host exact rows are still used only as a correctness oracle.
- The exact refinement is still produced by CuPy, not by a native device-only
  exact predicate.
- This is app-agnostic: the native stream exposes generic public ids plus input
  instance ordinals; RayJoin/CDB policy stays outside the engine.
- Release, public speedup, RayJoin reproduction, RT-core speedup, true-zero-copy,
  hidden dispatch, automatic retry, and native default-route claims remain
  blocked.
