# Goal3671 Side-Aware Owner-Face Filter

Date: 2026-06-06

Status: implemented as a generic Python/CuPy topology continuation.

## Why This Goal Exists

The user rejected the v2.9 closeout framing after Goal3668. Goal3668 is superseded:
v2.9 remains open for major performance/contract work, not minor tuning.

Goal3665 made the validated fast PIP route fail closed on the full county CDB
sample because the tuned fast route produced `47264` rows while the exact
prepared route produced `47262` (`47264 != 47262`). A fresh A5000 probe on `origin/main` at
`a0113c68` narrowed the unique mismatch to two extra full-county candidate
pairs:

```text
(893, 16312)
(894, 16312)
```

Both are topology ownership cases, not epsilon cases.

## Design Reading

The prior owner-face continuation could filter candidates by caller-supplied
`owner_face_id`. That is not always expressive enough. Point `894` demonstrates
the gap:

| Point | Candidate shape | Shape faces | Face-only owner | Exact? |
| ---: | ---: | --- | ---: | --- |
| 894 | 891 | left `371`, right `384` | `384` | yes |
| 894 | 16312 | left `384`, right `607` | `384` | no |

Face id alone keeps both shapes. The exact row needs side-aware topology
ownership: `(owner_face_id=384, owner_side=right)`.

## What Changed

Added a generic side-aware owner-face filter family:

- `OWNER_FACE_SIDE_CODES`
- `OWNER_FACE_SIDE_LABELS`
- `filter_closed_shape_membership_candidates_by_owner_face_side(...)`
- `filter_closed_shape_membership_candidate_columns_by_owner_face_side_columns(...)`
- `filter_closed_shape_membership_candidate_columns_by_owner_face_side_cupy(...)`

The contract remains app-agnostic:

- RTDL receives candidate `(point_id, shape_id)` columns.
- RTDL receives topology rows with `left_face_id` and `right_face_id`.
- The caller supplies explicit `(owner_face_id, owner_side)` columns.
- The native engine does not infer CDB, GIS, RayJoin, or benchmark ownership.

The side-aware CuPy filter intentionally preserves duplicate candidate rows
because the current RayJoin PIP row-count contract has row-stream multiplicity.
The face-only CuPy filter remains fail-closed on duplicate candidate pairs by
default.

## Validation

The new unit test covers the full-county failure shape:

- face-only filtering wrongly keeps `(894, 16312)`;
- side-aware filtering keeps `(894, 891)` and drops `(894, 16312)`;
- duplicate accepted candidate rows are preserved;
- the CuPy path matches the columnar reference when CuPy is available;
- `validate_owner_face_priority_pipeline_contract()` lists the new helpers and
  records the duplicate-row policy.

Pod validation on NVIDIA RTX A5000 then wired the new helper into the full
county CDB row stream:

Artifact:

```text
docs/reports/goal3671_rayjoin_topology_probe_a5000/full_county_side_aware_route_probe.json
```

Result:

| Measure | Value |
| --- | ---: |
| Exact prepared rows | 47,262 |
| Tuned candidate rows before side filter | 47,264 |
| Selected ambiguous points | 893, 894 |
| Selected candidate rows | 4 |
| Selected filtered rows | 2 |
| Removed extra rows | `(893, 16312)`, `(894, 16312)` |
| Filtered rows after side-aware repair | 47,262 |
| Multiset parity with exact prepared rows | true |

This is the first full-county constructive proof that the Goal3665 `47264 !=
47262` mismatch can be repaired by a generic topology continuation, provided
the caller supplies the needed owner-side columns.

Command:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3671_side_aware_owner_face_filter_test
```

## Boundary

This is major-direction work, not closeout. It does not authorize a default
RayJoin route yet, because caller-side derivation of `(owner_face_id,
owner_side)` columns still needs a reviewed front door and pod-scale same
contract evidence.

Blocked claims remain blocked:

- release authorization;
- public v2.9 speedup claims;
- RTDL-beats-RayJoin wording;
- RayJoin paper reproduction wording;
- true zero-copy wording;
- app-specific native-engine logic.

## What Still Blocks Default Route Selection

The full-county repair route is:

```text
RTDL/OptiX tuned candidate rows
-> caller-supplied side-aware topology ownership columns
-> side-aware CuPy filter preserving duplicate row multiplicity
-> exact prepared row-count parity
```

The remaining major work is to define the app/data-layer derivation of the
owner-side columns. That derivation is caller policy, not native engine policy.
Until it is reviewed and validated, this is a side-aware repair capability, not
an automatic RayJoin default route.
