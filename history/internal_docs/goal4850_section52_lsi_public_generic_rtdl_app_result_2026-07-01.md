# Goal4850 Result: Section 5.2 LSI Public Generic RTDL App Attempt

Date: 2026-07-01

## Verdict

`blocked_by_public_lsi_contract_gap`

Goal4850 answered the user's question directly: for Section 5.2 LSI, we should not rely on a bundled/private RayJoin helper if the claim is "ordinary users can write the app with public generic RTDL primitives." I built and ran that public-generic attempt. It did **not** match the AuthorPatch/RayJoin LSI count.

This is a real product gap, not a documentation wording issue.

## What Was Tested

Script:

`history/internal_docs/goal4850_rayjoin_section52_lsi_public_primitives.py`

It intentionally avoided:

- `rtdsl.rayjoin_overlay`
- underscored helper functions such as `_run_lsi_rows`
- runtime/native/source edits
- Section 5.7 overlay/PIP/output-chain claims

It used only:

- `rtdsl.load_cdb`
- `rtdsl.chains_to_rayjoin_cdb_segments`
- `rtdsl.optix_runtime.prepare_segment_pair_intersection_optix`
- `rtdsl.optix_runtime.prepare_segment_pair_left_set_optix`
- `PreparedOptixSegmentPairIntersection.count_prepared_left_exact_intersections`

## Dataset

The currently available representative Section 5.2 pair:

- `poly1`: Australia current OSM lakes CDB
- `poly2`: Australia current OSM parks CDB
- label: `current_osm_australia_lakes_parks_representative`
- claim level: representative, not exact paper pair

Previously validated AuthorPatch/RayJoin count:

- AuthorPatch forward `-poly1 lakes -poly2 parks`: `13622`
- Bundled RTDL RayJoin LSI helper matched this count when using the observed direction contract.

## Result

The public-generic prepared segment-pair route returned:

```json
{
  "count": 103869,
  "expected_count": 13622,
  "matched_expected": false,
  "bundled_rayjoin_helper_used": false,
  "public_generic_rtdl_primitives": true
}
```

Full artifact:

`history/internal_docs/goal4850_current_osm_au_public_primitives_summary.json`

## Interpretation

The current public prepared segment-pair primitive is a lower-level raw segment-pair intersection counter:

```text
SEGMENT_PAIR_INTERSECTION_ROWS_2D -> scalar_exact_count
```

That is **not** the same contract as RayJoin Section 5.2 LSI. The Section 5.2 LSI contract appears to include additional CDB/RayJoin semantics beyond "count every raw exact segment-pair intersection," such as topology-aware candidate handling, boundary/degeneracy rules, and/or duplicate/crossing semantics encoded in the bundled helper and author code.

Therefore:

- The earlier bundled-helper result remains valid as bounded product evidence.
- It is **not** yet valid to say a normal user can reproduce Section 5.2 LSI with only public generic RTDL primitives.
- The gap is now localized: RTDL needs a public, generic LSI contract/front-door, not a hidden RayJoin app helper.

## Why This Was Missed Earlier

Two shortcuts hid the issue:

1. The bundled helper matched counts, so it was tempting to treat that as "RTDL can do LSI." It can, but through a RayJoin-specific bundled helper, not through the clean public primitive surface.
2. A previous generic kernel attempt used ordinary `Segment` intersection rows and also mismatched; that was dismissed as "wrong route" without finishing the stronger public prepared-primitive route. Goal4850 finished that route and showed it still mismatches.

## What Must Be Done Next

If we want the clean language claim for Section 5.2, the next product goal must be:

> Promote the RayJoin-compatible LSI contract into a public generic RTDL primitive/front-door.

That means:

1. Read the bundled helper and author code to identify the exact semantic delta between raw segment-pair count and Section 5.2 LSI count.
2. Define a public primitive name and contract, for example:

   ```python
   prepare_cdb_lsi_2d_optix(base_segments_or_cdb)
   count_prepared_query_lsi(query_segments_or_cdb)
   ```

   The name should not be `rayjoin_*` if the primitive is genuinely a generic CDB/planar-map LSI operation.
3. Add synthetic tests that show why raw segment-pair count overcounts relative to LSI.
4. Re-run the three already validated Section 5.2 pairs:

   - County x Zipcode: expected `961165`
   - Block x Water: expected `649605`
   - Australia current OSM Lakes x Parks representative: expected `13622`
5. Only then claim:

   > A normal user can write the Section 5.2 LSI workload using public RTDL primitives.

## Scope Boundary

This result does not affect the already recorded facts:

- Section 5.2 bounded reproduction via bundled helper exists.
- Goal4845 and Goal4846 fixed real product correctness issues.
- Full Section 5.7 polygon overlay remains a separate, larger target.

But it does change the language-quality conclusion:

> The clean public primitive surface is still incomplete for Section 5.2 LSI.
