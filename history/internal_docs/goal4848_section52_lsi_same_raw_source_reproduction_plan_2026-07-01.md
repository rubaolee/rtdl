# Goal4848 - RayJoin Section 5.2 LSI Same-Raw-Source Reproduction

Date: 2026-07-01

## Objective

Complete RayJoin Section 5.2 LSI reproduction for the six remaining Lakes/Parks pairs by using the same public raw source family referenced by the RayJoin author README, following the author-documented preprocessing path into CDB, and then running AuthorPatch-vs-RTDL LSI correctness on the generated CDBs.

This goal continues after Goal4847 proved the exact Dryad preprocessed CDB share is currently unavailable.

## Correct Standard

The target is:

```text
same_raw_source_author_pipeline_regenerated_cdb
```

This is a serious reproduction route:

1. use the public raw Lakes/Parks data source named by the author;
2. follow the author preprocessing pipeline as closely as possible;
3. generate the CDB files under the author path contract;
4. run the author patched binary and RTDL on the same generated CDBs;
5. compare LSI counts.

This is **not**:

- a toy dataset;
- a random replacement source;
- the lost Dryad exact preprocessed CDB;
- a claim that regenerated CDB bytes equal the author's private/preprocessed CDB bytes.

## Six Remaining Section 5.2 Rows

| Pair | Required generated left CDB | Required generated right CDB |
|---|---|---|
| LKAF x PKAF | `point_cdb/lakes/Africa/lakes_Africa_Point.cdb` | `point_cdb/parks/Africa/parks_Africa_Point.cdb` |
| LKAS x PKAS | `point_cdb/lakes/Asia/lakes_Asia_Point.cdb` | `point_cdb/parks/Asia/parks_Asia_Point.cdb` |
| LKAU x PKAU | `point_cdb/lakes/Australia/lakes_Australia_Point.cdb` | `point_cdb/parks/Australia/parks_Australia_Point.cdb` |
| LKEU x PKEU | `point_cdb/lakes/Europe/lakes_Europe_Point.cdb` | `point_cdb/parks/Europe/parks_Europe_Point.cdb` |
| LKNA x PKNA | `point_cdb/lakes/North_America/lakes_North_America_Point.cdb` | `point_cdb/parks/North_America/parks_North_America_Point.cdb` |
| LKSA x PKSA | `point_cdb/lakes/South_America/lakes_South_America_Point.cdb` | `point_cdb/parks/South_America/parks_South_America_Point.cdb` |

## Work Plan

### A. Source Version Lock

Determine whether the author used SpatialHadoop's new OSM Lakes/Parks datasets or old OSM Lakes/Parks datasets.

Evidence to use:

- RayJoin README;
- SpatialHadoop dataset page;
- author logs' graph scale by continent;
- any author script assumptions.

Exit gate:

- a written source-version decision with evidence and a fallback if the first source is no longer downloadable.

### B. Raw Data Acquisition

Download or otherwise acquire the selected SpatialHadoop Lakes/Parks raw files on the POD.

Record:

- source URLs;
- file sizes;
- checksums if practical;
- local paths.

Exit gate:

- raw Lakes and Parks files exist on the POD, or acquisition fails with documented HTTP/tool errors and a next-source fallback.

### C. Author Pipeline Reproduction

Follow the author-documented preprocessing path:

```text
raw SpatialHadoop Lakes/Parks
  -> WKT/shapefile conversion if required
  -> polygon-to-line with neighbor face information
  -> CDB via author misc/shp2cdb.py
  -> continent split preserving author path contract
```

If ArcGIS-only polygon-to-line behavior cannot be run directly on the POD, implement an auditable equivalent converter and explicitly document equivalence assumptions:

- chain records;
- first/last point ids;
- left/right face ids;
- stable ordering.

Exit gate:

- all six left/right CDB pairs exist under one Goal4848 dataset root, or the exact missing preprocessing capability is documented.

### D. AuthorPatch-vs-RTDL Correctness

For each generated pair:

1. run AuthorPatch:

```text
query_exec -poly1 <left.cdb> -poly2 <right.cdb> -serialize=/dev/shm -grid_size=15000 -mode=rt -query=lsi -warmup=0 -repeat=1 -xsect_factor 0.1 -enlarge=3.5 -check=false
```

2. run RTDL OptiX on the same CDB pair;
3. compare LSI counts.

Exit gate:

- each generated pair has AuthorPatch count, RTDL count, delta, and provenance label.

### E. Report and Review

Write:

- acquisition/preprocessing report;
- correctness result table;
- call-for-review packet;
- Antigravity review or review debt;
- Claude review debt if unavailable.

## Expected Problems

1. SpatialHadoop Google Drive links may be rate-limited or changed.
2. The raw files may be large: new Lakes/Parks downloads are multi-GB.
3. Author's README uses ArcGIS for polygon-to-line neighbor information; reproducing this without ArcGIS may require a careful converter.
4. New vs old SpatialHadoop source mismatch can change graph scale and counts.
5. Same raw source plus regenerated CDB is rigorous, but still not the lost Dryad exact CDB.

## Completion Labels

- `complete_section52_lsi_same_raw_source_all6_correctness_passed`
- `partial_section52_lsi_same_raw_source_some_pairs_passed`
- `blocked_by_raw_source_download_unavailable`
- `blocked_by_author_pipeline_preprocessing_gap`
- `blocked_by_lsi_count_mismatch_with_pair_diff`

## Non-Authorization

This goal does not authorize:

- calling regenerated CDBs exact Dryad paper CDBs;
- Section 5.7 overlay claims;
- V3/V4 claims;
- Embree claims;
- broad performance claims;
- random/toy data substitution.
