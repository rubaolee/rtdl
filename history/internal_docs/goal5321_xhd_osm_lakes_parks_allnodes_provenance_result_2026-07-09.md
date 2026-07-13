# Goal5321 - X-HD OSM Lakes/Parks/AllNodes Provenance Search

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5321 classifies the remaining OSM-derived X-HD workload family after the
WaterBodies/BG, graphics, and County-ZCTA exact-provenance searches.

The question:

```text
Can public SpatialHadoop / OSM catalog evidence support exact paper input
status for lakes.bz2.wkt, parks.bz2.wkt, or all_nodes.wkt?
```

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5321_osm_lakes_parks_allnodes_provenance_search.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5321.osm_lakes_parks_allnodes_provenance_search.v1
```

## Evidence Checked

Project evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5301_non_graphics_dataset_provenance_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5267_full_paper_coverage_gap_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_author_log_workload_manifest_goal5175_2026-07-08.json
src/rtdsl/datasets.py
history/internal_docs/docs_reports/goal54_lkau_pkau_four_system_2026-04-03.md
```

External public source:

```text
https://spatialhadoop.cs.umn.edu/datasets.html
```

## Author Log Evidence

The author logs contain the large OSM Lakes/Parks pair:

```text
lakes.bz2.wkt -> parks.bz2.wkt
HDResult = 55.734275817871094
input point counts = 301,704,289 / 403,688,408
records = 5
sections = auto_tune, eb_gpu, hybrid_gpu, rt_gpu
```

This proves the workload exists in the paper-branch logs. It does not provide
input bytes, hashes, snapshot date, or extraction filters.

## Public SpatialHadoop Evidence

The public SpatialHadoop datasets page is live and contains OSM-derived
datasets.

New OSM datasets:

```text
All Nodes: 2.7 Billion records, 96GB uncompressed, 24.9GB download
Lakes:     8.4M records,       9GB uncompressed,  2.7GB download
Parks:     10M records,        9.3GB uncompressed,2.9GB download
```

Old OSM datasets:

```text
all_nodes: 1.7 Billion points, 62.3GB uncompressed, 17GB download
lakes:     4.3M Polygons,      2.6GB uncompressed, 798MB download
parks:     234K Polygons,      102MB uncompressed, 34MB download
```

The page states the datasets were extracted from public sources and recommends
linking to the page because datasets will be updated and more added. That is
useful public-source evidence, but it is not exact author input provenance.

## Prior Bounded Analogue

The old Goal54 result remains useful only as a bounded analogue:

```text
source = live OSM Overpass way geometry
bbox = sunshine_tiny
lakes source elements = 280
parks source elements = 264
accepted as = bounded four-system Australia analogue
```

It was explicitly not:

```text
continent-scale LKAU/PKAU completion;
exact SpatialHadoop or author HDDatasets reproduction;
multipolygon relation reconstruction.
```

## Exit Label

```text
osm_lakes_parks_allnodes_exact_provenance_not_found__snapshot_filter_blocked
```

## Interpretation

Current status:

```text
source_public_but_exact_snapshot_and_conversion_blocked
```

Primary blocker:

```text
OSM snapshot/filter/conversion identity, not RTDL route code.
```

The public catalog is too large to download casually, and downloading it would
not by itself change exact-input status because the missing evidence is:

```text
author files/hashes;
OSM planet snapshot date/hash;
extraction filters;
conversion scripts / WKT generation rule;
external review accepting a deterministic public-source regeneration.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5321_osm_lakes_parks_allnodes_provenance_search.json
py -m unittest tests.goal5321_xhd_osm_lakes_parks_allnodes_provenance_test
```

Expected:

```text
tests pass; no POD required
```

## Claim Boundary

Allowed:

```text
Goal5321 shows that OSM Lakes/Parks/AllNodes has public-source catalog evidence
but remains exact-input blocked on snapshot/filter/conversion provenance.
```

Forbidden:

```text
OSM Lakes/Parks/AllNodes exact paper input recovery;
SpatialHadoop public catalog entries are exact author inputs;
bounded Overpass analogues reproduce the X-HD OSM paper workloads;
Figure 5, Figure 7, or Figure 10 OSM reproduction;
author-vs-RTDL performance ratio.
```

## POD Use

Goal5321 did not use POD.

POD is not expected until concrete author files, accepted public snapshots, or
route execution candidates exist.
