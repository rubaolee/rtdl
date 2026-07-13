# Goal4961 Larger Representative Input Availability Audit

Date: 2026-07-04

## Exit Label

`completed_input_availability_audit__no_larger_representative_input_on_current_pod__goal4962_requires_data_restore`

## Purpose

Goal4960 settled the public County x Soil fresh-vs-cached measurement boundary.
Goal4961 asks whether the next measurement can be repeated on a larger
representative Section 5.7 input before moving to deeper implementation work.

This audit treats the current POD and current workspace as authoritative. Older
Goal4806/4879/4881 artifacts are useful only as a data-restoration index. They
are not fresh Goal4962 evidence.

## Current POD

```text
host: root@213.173.108.15 -p 10689
workspace: /root/rtdl_goal4955
```

## Direct Current-Workspace Scan

Command:

```bash
cd /root/rtdl_goal4955
find Paper-reproduction-apps/rayjoin-paper -maxdepth 5 \
  \( -name '*.cdb' -o -name '*.txt' -o -name '*manifest*.json' \) -print | sort
```

Observed files:

```text
Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_countyXbr_soil_answer.txt
Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_county_clean_25_odyssey_final.txt
Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_soil_ascii_odyssey_final.txt
Paper-reproduction-apps/rayjoin-paper/data/public_sample_manifest.json
```

Interpretation: the current repo checkout on the POD contains only the public
County x Soil sample.

## Historical Path Probe

The following previously documented larger inputs were checked on the current
POD. All are missing.

| Candidate | Historical path status |
|---|---|
| South America bounded 150k/50k lakes/parks | missing |
| County x Zipcode same-source CDBs | missing |
| Block x Water regenerated ArcGIS CDBs | missing |
| Australia current OSM lakes/parks representative | missing |
| Goal4380 exact Australia lakes/parks CDBs | missing |

Concrete missing paths checked:

```text
/workspace/goal4881_section57_south_america/cdb_bounded_150k_50k/lakes_South_America_current_osm_bounded150k_Point.cdb
/workspace/goal4881_section57_south_america/cdb_bounded_150k_50k/parks_South_America_current_osm_bounded50k_Point.cdb
/workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb
/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb
/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb
/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset/point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb
/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb
/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb
/workspace/rayjoin_section57_data/cdb_topology/point_cdb/lakes/Australia/lakes_Australia_Point.cdb
/workspace/rayjoin_section57_data/cdb_topology/point_cdb/parks/Australia/parks_Australia_Point.cdb
```

## Limited Global Scan

A bounded scan of `/root`, `/workspace`, `/tmp`, and `/dev/shm` looked for CDB
files and known RayJoin data names. It found only the same three public-sample
text files:

```text
/root/rtdl_goal4955/Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_county_clean_25_odyssey_final.txt
/root/rtdl_goal4955/Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_soil_ascii_odyssey_final.txt
/root/rtdl_goal4955/Paper-reproduction-apps/rayjoin-paper/_data/public_sample/br_countyXbr_soil_answer.txt
```

No larger `.cdb` files were found.

## Historical Candidate Index

The most useful restoration index is:

```text
history/internal_docs/goal4879_section57_representative_data_manifest_2026-07-02.json
```

It identifies these candidates:

| Priority | Pair | Label | Why useful now | Current status |
|---:|---|---|---|---|
| 1 | LKSA x PKSA bounded 150k/50k | representative current OSM bounded | Much larger than public sample but bounded enough to run; existing Goal4881 reports include phase evidence and byte-equality under AuthorOfficial. | Historical paths missing on current POD |
| 2 | LKAU x PKAU | representative current OSM regenerated | Previously completed representative current-source pair. | Historical paths missing on current POD |
| 3 | County x Zipcode | available current same-source CDB | High-value US paper pair shape, but historically much larger and correctness-sensitive. | Historical paths missing on current POD |
| 4 | Block x Water | regenerated ArcGIS pair | Large stress pair; good later-scale test. | Historical paths missing on current POD |

Goal4962 should prefer the South America bounded 150k/50k pair if restored,
because it is large enough to test the binary route without immediately jumping
to the extreme Block x Water scale.

## Decision

Goal4962 is not authorized to run on a larger representative input from the
current POD state, because no such input is present.

Allowed next actions:

1. Restore one larger pair to the POD, preferably:

```text
/workspace/goal4881_section57_south_america/cdb_bounded_150k_50k/lakes_South_America_current_osm_bounded150k_Point.cdb
/workspace/goal4881_section57_south_america/cdb_bounded_150k_50k/parks_South_America_current_osm_bounded50k_Point.cdb
```

2. After restoration, run Goal4962 fresh binary route on that pair and record
   the same fresh/cached boundary used in Goal4960.
3. If no larger input is restored, proceed with Goal4963 exact LSI pair-id
   device-column design, because it directly targets the remaining fresh-route
   bottleneck and does not depend on larger input availability.

## Not Authorized

- Do not use old Goal4881/4380 summaries as fresh Goal4962 measurements.
- Do not claim larger representative performance from the public sample.
- Do not rerun cached/replay mode and compare it to AuthorPatch as if it were a
  fresh overlay.
- Do not regenerate a new large input silently and call it an exact paper input.

## Next

Proceed to Goal4963 while waiting for larger input restoration, or restore the
South America bounded pair and then run Goal4962.
