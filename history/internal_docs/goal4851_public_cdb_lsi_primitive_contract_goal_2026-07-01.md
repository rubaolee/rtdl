# Goal4851: Promote Section 5.2 LSI Into A Public Generic RTDL Primitive

Date: 2026-07-01

## Trigger

Goal4850 proved that ordinary public prepared segment-pair primitives currently return raw exact segment-pair intersections, not RayJoin Section 5.2 LSI counts:

- expected AuthorPatch/RayJoin LSI count: `13622`
- public generic prepared segment-pair count: `103869`

Therefore the clean user-level Section 5.2 implementation is blocked by a public primitive contract gap.

## Objective

Create a public, generic RTDL primitive/front-door for CDB/planar-map line-segment intersection count that matches the AuthorPatch/RayJoin Section 5.2 LSI contract without requiring users to call the bundled `rayjoin_overlay` helper.

This goal must not create a hidden "RayJoin app kernel." It must expose a reusable CDB/planar-map LSI primitive that a user can call from an ordinary Python RTDL app.

## Required Investigation

1. Compare three routes on the same input:
   - AuthorPatch `query_exec -query=lsi`
   - RTDL bundled helper route that matches AuthorPatch
   - RTDL public raw segment-pair primitive that overcounts
2. Identify the semantic delta:
   - duplicate/candidate collapse rules
   - shared-boundary or vertex-touch handling
   - CDB chain/face/topology filters
   - direction contract (`poly2` query over `poly1` base)
   - any exact/scaled coordinate rules
3. Build small synthetic CDB-like cases that reproduce the overcount without loading huge datasets.

## Implementation Boundary

Allowed:

- Add a public RTDL API/front-door if the semantics are generic CDB/planar-map LSI.
- Reuse existing native OptiX work where appropriate.
- Add tests.
- Keep bundled helper as a compatibility layer if needed, but do not require it for user code.

Forbidden:

- Do not add a RayJoin-identity public API as the only solution.
- Do not claim full Section 5.7 overlay.
- Do not bury application-specific policy under a generic name.
- Do not optimize performance before correctness matches on small synthetic cases.

## Target Public Shape

The exact name can change after implementation review, but the user-level shape should be close to:

```python
from rtdsl import load_cdb
from rtdsl.optix_runtime import prepare_cdb_lsi_2d_optix

base = load_cdb("A_Point.cdb")
query = load_cdb("B_Point.cdb")

with prepare_cdb_lsi_2d_optix(base) as lsi:
    count = lsi.count(query)
```

The important property is not the name; it is that the route is public, documented, generic to CDB/planar-map LSI, and does not import `rtdsl.rayjoin_overlay`.

## Validation Gates

Gate 1: Synthetic Cases

- At least three tiny CDB-like cases where raw segment-pair count and LSI count differ.
- The new public primitive must match the expected LSI count.

Gate 2: Existing Section 5.2 Pairs

- County x Zipcode: `961165`
- Block x Water: `649605`
- Australia current OSM Lakes x Parks representative: `13622`

Gate 3: User-Mode Script

- Update the Goal4850 script or create a successor script that uses only the new public primitive.
- It must import no `rtdsl.rayjoin_overlay`.

Gate 4: Review

- Produce a call-for-review packet asking reviewers whether this is a generic CDB/planar-map LSI primitive or a disguised RayJoin shortcut.

## Exit Labels

- `pass_public_cdb_lsi_primitive_matches_authorpatch`: public primitive matches all available Section 5.2 counts.
- `blocked_by_unclear_lsi_semantics`: the semantic delta cannot be stated cleanly from author/source evidence.
- `blocked_by_app_specific_semantics`: the only matching semantics are RayJoin-identity specific and should not be promoted as generic RTDL.
- `blocked_by_implementation_gap`: the contract is clear but the implementation is not completed.

## User-Facing Claim If Passed

Only if all gates pass:

> Section 5.2 LSI can be written as a normal RTDL user app using a public CDB/planar-map LSI primitive, with Python orchestration and RT-core execution.

Do not claim full Section 5.7 overlay from this goal.
