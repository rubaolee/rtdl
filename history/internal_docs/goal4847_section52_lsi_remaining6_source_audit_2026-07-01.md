# Goal4847 - RayJoin Section 5.2 Remaining Six LSI Source Audit

Date: 2026-07-01

## Objective

Acquire or prove unavailable the six missing RayJoin Section 5.2 Lakes/Parks exact CDB input pairs, then run AuthorPatch-vs-RTDL LSI correctness for every acquired pair without using regenerated data as exact paper input.

## Result

Status: `partial_available_pairs_pass__remaining6_missing_exact_input_after_source_audit`

No exact CDB inputs were acquired for the six Lakes/Parks pairs. No RTDL correctness runs were executed for those six pairs because the required exact CDB inputs are absent.

This is not a full 8/8 Section 5.2 reproduction. The two currently runnable pairs remain:

| Pair | AuthorPatch LSI | RTDL LSI | Delta | Status |
|---|---:|---:|---:|---|
| County x Zipcode | 961165 | 961165 | 0 | completed in Goal4845 |
| Block x Water | 649605 | 649605 | 0 | completed in Goal4846 |

The remaining six are closed for now as source-unavailable, not as failed correctness tests.

## Clarification After Broader Web Search

The Lakes/Parks **names and raw source datasets are not private**. SpatialHadoop's public dataset page lists OpenStreetMap-derived Lakes and Parks datasets and says the datasets are extracted from public sources and can be freely used and redistributed:

- SpatialHadoop Datasets: `https://spatialhadoop.cs.umn.edu/datasets.html`
- OpenStreetMap new datasets:
  - `Lakes` - 9GB uncompressed, 8.4M records, 2.7GB download
  - `Parks` - 9.3GB uncompressed, 10M records, 2.9GB download
- OpenStreetMap old datasets:
  - `lakes` - 2.6GB uncompressed, 4.3M polygons, 798MB download
  - `parks` - 102MB uncompressed, 234K polygons, 34MB download

This does **not** contradict the Goal4847 result. It changes the wording precision:

- `exact_paper_preprocessed_cdb`: still unavailable from the current POD, author repo, and Dryad share.
- `raw_public_lakes_parks_source`: publicly listed and should be pursued for a same-source regeneration goal.
- `same_source_regenerated_cdb`: can be built if we download and reproduce the conversion/continent-splitting pipeline, but it must not be called exact paper input unless it is byte/provenance-equivalent to the author CDBs.

Therefore the correct next route is not to claim "private data"; it is to start a separate same-source regeneration goal if exact CDBs remain unavailable.

## Remaining Six Required Inputs

| Pair | Required left CDB | Required right CDB | Current status |
|---|---|---|---|
| LKAF x PKAF | `point_cdb/lakes/Africa/lakes_Africa_Point.cdb` | `point_cdb/parks/Africa/parks_Africa_Point.cdb` | missing exact input |
| LKAS x PKAS | `point_cdb/lakes/Asia/lakes_Asia_Point.cdb` | `point_cdb/parks/Asia/parks_Asia_Point.cdb` | missing exact input |
| LKAU x PKAU | `point_cdb/lakes/Australia/lakes_Australia_Point.cdb` | `point_cdb/parks/Australia/parks_Australia_Point.cdb` | missing exact input |
| LKEU x PKEU | `point_cdb/lakes/Europe/lakes_Europe_Point.cdb` | `point_cdb/parks/Europe/parks_Europe_Point.cdb` | missing exact input |
| LKNA x PKNA | `point_cdb/lakes/North_America/lakes_North_America_Point.cdb` | `point_cdb/parks/North_America/parks_North_America_Point.cdb` | missing exact input |
| LKSA x PKSA | `point_cdb/lakes/South_America/lakes_South_America_Point.cdb` | `point_cdb/parks/South_America/parks_South_America_Point.cdb` | missing exact input |

## Evidence 1 - Current POD Exact-CDB Search

Command run on the current POD:

```text
ssh root@157.157.221.29 -p 23132 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod

python3 search over /workspace, /data, /root for:
  lakes_Africa_Point.cdb, parks_Africa_Point.cdb,
  lakes_Asia_Point.cdb, parks_Asia_Point.cdb,
  lakes_Australia_Point.cdb, parks_Australia_Point.cdb,
  lakes_Europe_Point.cdb, parks_Europe_Point.cdb,
  lakes_North_America_Point.cdb, parks_North_America_Point.cdb,
  lakes_South_America_Point.cdb, parks_South_America_Point.cdb
```

Observed output:

```text
FOUND_COUNT 0
```

Interpretation: the current POD does not contain the required exact Lakes/Parks CDB files under the searched data/work roots.

## Evidence 2 - Current POD Raw/Archive Search

Because exact CDB files might have been absent while raw inputs or archives were present, I also searched for Lakes/Parks raw/source/archive artifacts under `/workspace`, `/data`, and `/root` with extensions such as `.wkt`, `.shp`, `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.7z`, `.geojson`, `.json`, and `.csv`.

Observed output:

```text
FOUND_RAW_OR_ARCHIVE 0
```

Interpretation: the current POD also lacks obvious Lakes/Parks raw/archive artifacts that could be promoted to exact paper CDB inputs.

## Evidence 3 - `/dev/shm` Serialized-Map Check

I checked whether serialized map caches existed in `/dev/shm`.

Observed Lakes/Parks result: no Lakes/Parks serialized maps.

Observed `/dev/shm` serialized maps:

```text
/dev/shm/-workspace-rayjoin_section57_same_source_cdb-point_cdb-USAZIPCodeArea-USAZIPCodeArea_Point.cdb.bin
/dev/shm/-workspace-rayjoin_section57_same_source_cdb-point_cdb-dtl_cnty-dtl_cnty_Point.cdb.bin
/dev/shm/artifacts-goal4806_section57_arcgis_full_us_20260630-dataset-point_cdb-USACensusBlockGroupBoundaries-USACensusBlockGroupBoundaries_Point.cdb.bin
/dev/shm/artifacts-goal4806_section57_arcgis_full_us_20260630-dataset-point_cdb-USADetailedWaterBodies-USADetailedWaterBodies_Point.cdb.bin
```

Interpretation: only the two U.S. same-source pairs have serialized caches. The six Lakes/Parks pairs do not.

## Evidence 4 - Author Repository README and Scripts

The author repository README says the project does not currently provide preprocessed datasets and users need to download/process datasets themselves. It lists:

- ArcGIS sources for the U.S. rows;
- SpatialHadoop Lakes/Parks for continent rows;
- a Dryad share for preprocessed datasets.

The author scripts do not download data. They assume this environment variable:

```bash
DATASET_ROOT="/local/storage/liang/Downloads/Datasets"
```

and build paths such as:

```bash
$DATASET_ROOT/point_cdb/lakes/$con/lakes_${con}_Point.cdb
$DATASET_ROOT/point_cdb/parks/$con/parks_${con}_Point.cdb
```

Interpretation: the scripts confirm the required exact path contract, but they do not provide the data or a download mechanism.

## Evidence 5 - Author Logs Exist, But They Are Not Inputs

The author repository contains historical run logs for all six Lakes/Parks LSI RT rows. These logs confirm the expected paths, sizes, and author-side intersection counts.

| Pair | Author log count | Left graph scale from log | Right graph scale from log |
|---|---:|---|---|
| LKAF x PKAF | 4765 | chains 27178, points 1872496, edges 1845318 | chains 41991, points 1358103, edges 1316112 |
| LKAS x PKAS | 37333 | chains 194573, points 10541220, edges 10346647 | chains 277198, points 12209639, edges 11932441 |
| LKAU x PKAU | 12618 | chains 16702, points 1254743, edges 1238041 | chains 22386, points 589464, edges 567078 |
| LKEU x PKEU | 278461 | chains 831264, points 28687526, edges 27856262 | chains 3299874, points 69273661, edges 65973787 |
| LKNA x PKNA | 1251343 | chains 1910184, points 69273661, edges 67363477 | chains 603325, points 27465008, edges 26861683 |
| LKSA x PKSA | 22383 | chains 43757, points 2418375, edges 2374618 | chains 85371, points 3264379, edges 3179008 |

These logs are useful author-side references, but they are not CDB files and cannot be used to run RTDL correctness.

## Evidence 6 - Dryad Share and API Checks

The recorded preprocessed-data share is:

```text
https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA
```

Current direct check:

```text
effective_url=https://datadryad.org/404
http_code=404
content_type=text/html; charset=utf-8
```

Dryad API searches:

```text
GET https://datadryad.org/api/v2/search?q=RayJoin
=> count=0, total=0

GET https://datadryad.org/api/v2/search?q=RayJoin%20spatial%20join
=> count=0, total=0
```

Interpretation: the preferred exact-input share is not currently accessible, and a Dryad API search did not reveal a replacement RayJoin dataset record.

## Evidence 7 - Historical Consistency

This source-audit result agrees with earlier internal records:

- `history/internal_docs/docs_reports/goal4375_section57_overlay_8x8_2026-06-14/rayjoin_section57_overlay_8x8_status_report_2026-06-14.md` recorded 2/8 complete and 6/8 blocked on missing exact Lakes/Parks CDB inputs.
- `exp-project-1/untracked-current/tools___archive__goal4806_released_rtdl_rayjoin_attempt_2026-06-30/docs_reports/goal4806_rayjoin_section57_current_status_and_8pair_data_audit_2026-06-30.md` recorded the same missing paths and Dryad final URL `https://datadryad.org/404`.

Goal4847 rechecked the same issue on the current date and current POD rather than relying only on those older records.

## Why No RTDL Runs Were Started

Running RTDL on regenerated Lakes/Parks data would answer a different question. It would be a same-source or regenerated experiment, not an exact paper-input Section 5.2 reproduction.

Running RTDL against author logs is impossible because logs are not input geometry.

Therefore no RTDL correctness run is authorized for the six Lakes/Parks pairs until exact CDB inputs are acquired.

## Completion Judgment

Goal4847 satisfies the "acquire or prove unavailable" part for the six Lakes/Parks exact CDB inputs under current public/POD conditions.

Exit label:

```text
partial_available_pairs_pass__remaining6_missing_exact_input_after_source_audit
```

The full 8/8 Section 5.2 exact-input claim remains blocked by missing exact Lakes/Parks CDB files.

## Not Authorized

This report does not authorize:

- calling regenerated Lakes/Parks data exact paper input;
- claiming full 8/8 Section 5.2 reproduction;
- claiming Section 5.7 overlay completion;
- using V3/V4 artifacts or claims;
- Embree claims;
- broad RayJoin/RTDL performance wording;
- treating author logs as RTDL correctness evidence.
