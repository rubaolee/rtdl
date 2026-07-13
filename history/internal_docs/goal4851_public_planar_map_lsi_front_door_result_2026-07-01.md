# Goal4851 Result: Public Planar-Map LSI Front Door

Date: 2026-07-01

## Verdict

`pass_public_planar_map_lsi_front_door_available_pairs__claude_amendments_addressed`

Goal4851 repaired the public-language gap exposed by Goal4850. Ordinary RTDL users now have a public CDB/planar-map LSI count primitive instead of having to call the bundled `rtdsl.rayjoin_overlay` helper or manually set a hidden predicate environment variable.

The three Goal4851 validation gates now pass through the public API:

| Pair | Expected | Public API count | Match | Expected provenance | Artifact |
|---|---:|---:|---|---|---|
| Australia Lakes x Parks representative | 13622 | 13622 | yes | Goal4848 RTDL bundled/helper representative count | `history/internal_docs/goal4851_current_osm_au_public_front_door_summary.json` |
| County x Zipcode restored exact/same-source CDB | 961165 | 961165 | yes | Goal4845 AuthorPatch and RTDL historical route count | `history/internal_docs/goal4851_county_zipcode_restored_public_front_door_summary.json` |
| Block x Water restored exact/same-source CDB | 649605 | 649605 | yes | Goal4846 AuthorPatch and RTDL historical route count | `history/internal_docs/goal4851_block_water_restored_public_front_door_summary.json` |

All three runs report:

- `rtdl_public_api: "prepare_planar_map_lsi_2d_optix"`
- `public_generic_rtdl_primitive: true`
- `bundled_rayjoin_helper_used: false`
- `section52_lsi_count_only: true`

This authorizes the bounded claim that RTDL now exposes a public generic planar-map LSI primitive for the available Section 5.2 LSI pairs. It does not authorize full 8/8 Section 5.2 completion, Section 5.7 overlay, or performance claims.

After Claude second-seat review, the implementation was amended so the public path uses the generic predicate mode name `planar_map_lsi`. The native layer still accepts the historical alias `rayjoin_lsi` for compatibility. The original POD artifacts were generated before this rename and therefore show `native_predicate_mode: "rayjoin_lsi"`; that is a historical artifact field, not the post-amendment public mode.

The amended native library was rebuilt on the POD with `OPTIX_PREFIX=/tmp/optix-sdk-probe`. A post-rebuild metadata smoke confirms `native_predicate_mode: "planar_map_lsi"` and `native_predicate_legacy_alias: "rayjoin_lsi"`:

- `history/internal_docs/goal4851_am1_make_build_optix_with_prefix.log`
- `history/internal_docs/goal4851_planar_map_lsi_metadata_after_am1.json`
- `history/internal_docs/goal4851_synthetic_after_am1_stdout.json`

## Public API Added

User shape:

```python
from rtdsl import load_cdb, prepare_planar_map_lsi_2d_optix

base = load_cdb("base_Point.cdb")
query = load_cdb("query_Point.cdb")

with prepare_planar_map_lsi_2d_optix(base) as lsi:
    count = lsi.count(query)
```

Implemented symbols:

- `src/rtdsl/optix_runtime.py`
  - `PreparedOptixPlanarMapLsi2D`
  - `prepare_planar_map_lsi_2d_optix`
- `src/rtdsl/__init__.py`
  - exports `PreparedOptixPlanarMapLsi2D`
  - exports `prepare_planar_map_lsi_2d_optix`

The new front door internally selects the existing native author-style planar-map LSI predicate and restores the environment afterward. User code does not import `rtdsl.rayjoin_overlay`.

Concurrency caveat: the current native selector is still backed by the process environment variable `RTDL_OPTIX_SEGMENT_PAIR_PREDICATE`. The public front door guards its own selection with a Python process-local lock and records this in metadata. Code that mutates that environment variable outside the public API can still interfere. The durable product direction is a future native ABI that passes predicate mode as an explicit parameter.

## Historical Primitive Audit

A separate read-only subagent audit answered the user's question: "did we already have this primitive?"

Short answer: no.

What existed before Goal4851:

- raw segment-pair OptiX primitives:
  - `prepare_segment_pair_intersection_optix`
  - `prepare_segment_pair_left_set_optix`
  - `count_prepared_left_exact_intersections`
- bundled RayJoin helper path:
  - `rtdsl.rayjoin_overlay._run_lsi_rows`
  - `run_rayjoin_overlay_rtdl_from_cdb_paths`
- hidden predicate selection:
  - `RTDL_OPTIX_SEGMENT_PAIR_PREDICATE=rayjoin_lsi`
- public post-amendment predicate name:
  - `RTDL_OPTIX_SEGMENT_PAIR_PREDICATE=planar_map_lsi`
- CDB conversion/loading helpers.

What was missing:

- a normal public API that accepts CDB/path/planar-map inputs;
- selects the author-style planar-map LSI predicate internally;
- avoids `rtdsl.rayjoin_overlay`;
- exposes the operation as a reusable CDB/planar-map LSI primitive.

This matches the Goal4850 failure: the clean public raw segment-pair attempt returned `103869` for the Australia representative pair where AuthorPatch/bundled LSI expected `13622`.

## Synthetic Semantic Delta

Artifact:

`history/internal_docs/goal4851_synthetic_planar_map_lsi_probe_summary.json`

The synthetic probe compared:

- raw public segment-pair count;
- the new public planar-map LSI front door.

It found 6 differing tiny cases. The main localized semantic delta is shared-boundary / shared-endpoint behavior:

| Case | Raw segment-pair count | Planar-map LSI count |
|---|---:|---:|
| shared_left_endpoint | 1 | 0 |
| shared_left_endpoint_diagonal_up | 1 | 0 |
| shared_left_endpoint_diagonal_down | 1 | 0 |
| vertical_base_shared_bottom_endpoint_right | 1 | 0 |
| vertical_base_shared_bottom_endpoint_left | 1 | 0 |
| reversed_base_shared_endpoint | 1 | 0 |

Proper crossing remains counted by both routes. Identical and collinear overlap cases remain rejected by both routes.

This proves that the public raw segment-pair primitive and the planar-map LSI contract are not the same contract. Goal4851 is therefore not just an API alias; it exposes a distinct CDB/planar-map LSI operation.

## POD Validation

### Australia Lakes x Parks Representative

Input:

- `/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb`
- `/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb`

Artifact:

`history/internal_docs/goal4851_current_osm_au_public_front_door_summary.json`

Result:

```json
{
  "count": 13622,
  "expected_count": 13622,
  "expected_count_provenance": "goal4848_rtdl_bundled_lsi_representative_count",
  "matched_expected": true,
  "rtdl_public_api": "prepare_planar_map_lsi_2d_optix",
  "claim_boundary": {
    "bundled_rayjoin_helper_used": false,
    "public_generic_rtdl_primitive": true,
    "section52_lsi_count_only": true
  }
}
```

### County x Zipcode Restored Exact/Same-Source CDB

The ordinary CDB files used by earlier Section 5.2 work were no longer present at their historical paths on the active POD. However, the RayJoin serialized planar-graph caches for those paths still existed in `/dev/shm`. Goal4851 restored the text CDBs from those caches using the author source layout in `src/map/planar_graph.h`.

Recovery artifact:

`history/internal_docs/goal4851_restore_rayjoin_pgraph_cache_to_cdb.py`

Restored inputs:

- `/workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb`
- `/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb`

Restore stats:

| CDB | Chains | Row index entries | Points | Segments |
|---|---:|---:|---:|---:|
| County | 8662896 | 8662897 | 17325792 | 8662896 |
| Zipcode | 23931046 | 23931047 | 47862092 | 23931046 |

Artifact:

`history/internal_docs/goal4851_county_zipcode_restored_public_front_door_summary.json`

Result:

```json
{
  "count": 961165,
  "expected_count": 961165,
  "expected_count_provenance": "goal4845_authorpatch_and_rtdl_historical_route_count",
  "matched_expected": true,
  "rtdl_public_api": "prepare_planar_map_lsi_2d_optix",
  "claim_boundary": {
    "bundled_rayjoin_helper_used": false,
    "public_generic_rtdl_primitive": true,
    "section52_lsi_count_only": true
  },
  "timings_sec": {
    "load_poly1": 84.12088251113892,
    "load_poly2": 233.92310099303722,
    "prepare": 19.81895126402378,
    "count": 57.08775374293327,
    "total_observed": 394.9506885111332
  }
}
```

### Block x Water Restored Exact/Same-Source CDB

Restored inputs:

- `/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb`
- `/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb`

Restore stats:

| CDB | Chains | Row index entries | Points | Segments |
|---|---:|---:|---:|---:|
| Block | 28473338 | 28473339 | 56946676 | 28473338 |
| Water | 22431809 | 22431810 | 44863618 | 22431809 |

Artifact:

`history/internal_docs/goal4851_block_water_restored_public_front_door_summary.json`

Result:

```json
{
  "count": 649605,
  "expected_count": 649605,
  "expected_count_provenance": "goal4846_authorpatch_and_rtdl_historical_route_count",
  "matched_expected": true,
  "rtdl_public_api": "prepare_planar_map_lsi_2d_optix",
  "claim_boundary": {
    "bundled_rayjoin_helper_used": false,
    "public_generic_rtdl_primitive": true,
    "section52_lsi_count_only": true
  },
  "timings_sec": {
    "load_poly1": 280.3469910994172,
    "load_poly2": 234.3873491883278,
    "prepare": 63.036833204329014,
    "count": 58.089697524905205,
    "total_observed": 635.8608710169792
  }
}
```

## Tests

Focused test:

```text
PYTHONPATH=src py -m unittest tests.goal4851_planar_map_lsi_public_front_door_test
```

Result:

```text
Ran 3 tests in 0.011s
OK
```

The tests verify:

- public export from `rtdsl`;
- LSI predicate mode is selected internally and restored afterward;
- the front-door block does not import `rtdsl.rayjoin_overlay`;
- metadata marks `bundled_rayjoin_helper_used: False`.
- support matrix marks `planar_map_lsi_count_2d` as OptiX-native and unsupported-explicit elsewhere.

A broader historical suite attempt also ran, but it failed on unrelated stale-history issues:

- `tests.goal3728_segment_pair_exact_count_front_door_test` expects an old `docs/reports/...` file that was moved during public-surface cleanup;
- `tests.goal4374_rayjoin_exact_paper_suite_test` has a tiny floating equality mismatch around `8e-14`.

Those failures are not Goal4851 API failures, but they should be recorded as residual test hygiene debt.

Claude AM5 follow-up: the `8e-14` failure must not be waved away forever. It is recorded as RayJoin exact-paper-suite hygiene debt because the parallel core SoS work can affect this area. It does not block the count-only LSI front door, but it should be checked before any stronger exact-paper wording.

## Claim Boundary

Authorized:

- RTDL now has a public planar-map/CDB LSI front door.
- The public front door reproduces the available Section 5.2 LSI count gates:
  - Australia Lakes x Parks representative: `13622`;
  - County x Zipcode: `961165`;
  - Block x Water: `649605`.
- The public front door avoids `rtdsl.rayjoin_overlay` in user code and records `bundled_rayjoin_helper_used: false`.
- The expected-count claim is internal/count-consistency evidence for the available pairs, not a full independent author-answer proof for every Section 5.2 pair.

Not authorized:

- full Section 5.2 eight-pair exact-input reproduction;
- Section 5.7 polygon overlay;
- broad RayJoin performance claims;
- broad RTDL performance claims;
- treating regenerated CDBs as exact paper inputs;
- claiming that cache recovery is a substitute for durable dataset management.
- claiming full geometric correctness from scalar count equality alone.

## Current Status

Goal4851 materially advances the product:

> The LSI capability is no longer only accessible through a bundled RayJoin helper; it has a public RTDL primitive shape.

Validation status:

- Synthetic gate: passed for semantic delta exposure.
- Australia representative public-front-door gate: passed.
- County x Zipcode restored exact/same-source public-front-door gate: passed.
- Block x Water restored exact/same-source public-front-door gate: passed.
- Claude AM1: addressed by switching the public predicate mode to `planar_map_lsi` and keeping `rayjoin_lsi` only as a legacy native alias.
- Claude AM1 POD rebuild: passed with `OPTIX_PREFIX=/tmp/optix-sdk-probe`.
- Claude AM2: partially addressed by a Python process-local lock and explicit metadata/documentation; native explicit predicate parameter remains future product debt.
- Claude AM3/AM4: addressed by recording expected-count provenance and preserving `section52_lsi_count_only`.
- Claude AM6: addressed by adding the feature to the user feature guide, engine support matrix, and LSI feature home.

## Remaining Product Debt

The algorithmic/API issue is closed for the available Section 5.2 LSI gates. The remaining debt is data engineering:

- exact CDB assets must be stored durably, not only as ordinary workspace files or `/dev/shm` caches;
- the six additional Section 5.2 pairs still need exact inputs or agreed representative same-source inputs before they can be claimed;
- historical tests that reference moved internal docs should be updated.

Recommended next label:

`goal4851_completed_public_planar_map_lsi_available_pairs_passed`
