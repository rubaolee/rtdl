# Goal4848 Scope Pivot - Representative Pair Only

Date: 2026-07-01

## User Directive

The user explicitly stopped the six-pair chase:

> Remaining six groups: search rationally, find one usable representative is enough. We are doing paper reproduction, but we are not robots. Authorized: find one.

## Corrected Scope

Goal4848 is therefore narrowed from:

- all six remaining Lakes/Parks continent pairs;

to:

- one usable representative Lakes/Parks pair, preferably `LKAU x PKAU` because it is the smallest Section 5.2 Lakes/Parks family and has the strongest local history.

## Representative Boundary

If the original SpatialHadoop raw files or exact paper CDB files are unavailable, the representative result must be labeled by its actual provenance:

- `exact_paper_cdb` only if the exact paper-preprocessed CDB is found;
- `same_raw_source_author_pipeline_regenerated_cdb` only if the SpatialHadoop raw file is acquired and processed through the author-documented pipeline;
- `current_osm_geofabrik_representative_cdb` if generated from current Geofabrik OSM data;
- `bounded_overpass_analogue` if generated from a small Overpass bounding box.

Only the first two can support a close Section 5.2 paper-input reproduction claim. The latter two are representative RTDL/AuthorPatch route checks, not exact paper reproduction.

## Search Facts So Far

- SpatialHadoop publicly lists New OSM Lakes/Parks and Old OSM Lakes/Parks.
- SpatialHadoop Google Drive IDs for Lakes/Parks return final Google 404 pages in current checks.
- Published S3 mirror hints for `https://s3.amazonaws.com/spatial-hadoop/input/lakes.bz2` and plausible parks variants return S3 404 in current checks.
- Current Geofabrik `australia-oceania-latest.osm.pbf` is reachable and has been selected as the serious representative fallback if exact/raw SpatialHadoop data remains unavailable.

## Anti-Churn Rule

Do not keep searching all six families after the representative route is established. Finish the one representative route, write the boundary, and stop.
