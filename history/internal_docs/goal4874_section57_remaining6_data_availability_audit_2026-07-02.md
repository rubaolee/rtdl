# Goal4874 - RayJoin Remaining Six Lakes/Parks Data Availability Audit

Date: 2026-07-02

## Purpose

Answer the immediate data-availability question:

- The author baseline for additional Section 5.7 pairs is not expected today.
- Check which of the remaining six Lakes/Parks pairs can be obtained or used now.
- Clarify whether the Section 5.2 / 5.3 currently used data slices are okay.

This is a data availability audit only. It does not authorize broad Section 5.7, all-eight, or performance claims.

## Short Answer

The two U.S. pairs are available on the current POD:

- County x Zipcode
- Block x Water

The exact paper-preprocessed CDB inputs for the remaining six Lakes/Parks continent pairs are still not present on the current POD:

- LKAF x PKAF
- LKAS x PKAS
- LKAU x PKAU
- LKEU x PKEU
- LKNA x PKNA
- LKSA x PKSA

One regenerated representative Lakes/Parks pair is already available:

- Australia current OSM regenerated CDBs under `/workspace/goal4848_rep/current_osm_au`

That Australia representative is useful for engineering coverage and public-source regeneration experiments, but it is not exact paper input.

## Current POD Evidence

Command target:

```text
ssh root@157.157.221.29 -p 23132 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod
```

Observed roots:

```text
/workspace/rayjoin_section57_data/cdb_topology        missing
/workspace/rayjoin_section57_same_source_cdb         exists
/workspace/goal4806_section57_arcgis_full_us_20260630 missing
/workspace/goal4848_rep/current_osm_au               exists
/data                                                missing
/root                                                exists
```

Current CDB files relevant to this audit:

```text
/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb
/workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb
/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb
/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb
```

Exact Lakes/Parks paper CDB name search result:

| Required exact file | Current POD status |
|---|---|
| `lakes_Africa_Point.cdb` | missing |
| `parks_Africa_Point.cdb` | missing |
| `lakes_Asia_Point.cdb` | missing |
| `parks_Asia_Point.cdb` | missing |
| `lakes_Australia_Point.cdb` | missing |
| `parks_Australia_Point.cdb` | missing |
| `lakes_Europe_Point.cdb` | missing |
| `parks_Europe_Point.cdb` | missing |
| `lakes_North_America_Point.cdb` | missing |
| `parks_North_America_Point.cdb` | missing |
| `lakes_South_America_Point.cdb` | missing |
| `parks_South_America_Point.cdb` | missing |

## Pair-by-Pair Status

| Pair | Exact paper CDB on POD? | Public/current-source route? | Immediate status |
|---|---:|---|---|
| County x Zipcode | yes, same-source CDB present | ArcGIS-derived U.S. route already in current POD cache | usable now |
| Block x Water | yes/current regenerated route already used in recent full-stream work | ArcGIS-derived U.S. route | usable now in current repaired line, but exact-paper provenance must stay bounded |
| LKAF x PKAF | no | Geofabrik Africa current OSM possible; SpatialHadoop raw source identified but not acquired | obtainable as regenerated/current-source, not exact |
| LKAS x PKAS | no | Geofabrik Asia current OSM possible but large | obtainable as regenerated/current-source, high resource cost |
| LKAU x PKAU | no exact paper CDB | current Australia OSM regenerated CDB already exists | usable now as representative only |
| LKEU x PKEU | no | Geofabrik Europe current OSM possible but very large | obtainable as regenerated/current-source, high resource cost |
| LKNA x PKNA | no | Geofabrik North America current OSM possible but very large | obtainable as regenerated/current-source, high resource cost |
| LKSA x PKSA | no | Geofabrik South America current OSM possible; moderate relative size | best next regenerated continent candidate after Australia |

## 5.2 / 5.3 Data Status

For Section 5.2 LSI:

- County x Zipcode and Block x Water have bounded passed records under the AuthorPatch-vs-RTDL count standard.
- Australia Lakes x Parks has a representative current-OSM regenerated route and count agreement for that route.
- The remaining six exact Lakes/Parks paper CDBs are still unavailable; therefore 8/8 exact-input Section 5.2 is not complete.

For Section 5.3 PIP / point-location:

- The public front door and cleanup work exist for the current bounded input routes.
- The same data availability boundary applies: U.S. available slices and Australia representative are usable; six exact Lakes/Parks paper CDBs are not present.
- This does not authorize an all-eight exact Section 5.3 claim.

## External Source State

SpatialHadoop publicly lists the OpenStreetMap Lakes/Parks sources. It lists new OSM Lakes as 9GB uncompressed / 8.4M records / 2.7GB download and new OSM Parks as 9.3GB uncompressed / 10M records / 2.9GB download. It also lists older OSM lakes and parks datasets. These are source datasets, not the exact RayJoin paper-preprocessed CDBs.

Geofabrik provides current OSM extracts for each continent. Its current public continent PBF sizes are approximately:

| Region | Current Geofabrik PBF size |
|---|---:|
| Africa | 7.3 GB |
| Asia | 14.9 GB |
| Australia/Oceania | 1.4 GB |
| Europe | 32.2 GB |
| North America | 17.8 GB |
| South America | 3.8 GB |

Australia has already been regenerated from Geofabrik current OSM into CDBs on the POD. South America is the next most reasonable regenerated continent candidate by size after Australia.

## Practical Recommendation

Do not wait for the author baseline today.

Use the following split:

1. Exact paper reproduction track:
   - Continue to mark the remaining six Lakes/Parks exact CDB pairs as blocked by missing exact paper-preprocessed input.
   - If the author later provides the exact CDBs or answer files, run them directly.

2. Regenerated/current-source engineering track:
   - Use Australia current OSM immediately as the available representative Lakes/Parks route.
   - If one more continent is needed today, choose South America first, then Africa.
   - Label every result as `current_osm_regenerated`, never as exact paper input.

3. Section 5.7 work:
   - The current verified full-stream Section 5.7 evidence remains the two U.S. pairs only: County x Zipcode and Block x Water.
   - A Lakes/Parks Section 5.7 run on Australia current OSM would be useful engineering evidence, but it would not be paper-exact.

## Not Authorized

This audit does not authorize:

- saying the six Lakes/Parks exact paper CDBs are available;
- treating current OSM regenerated data as exact paper input;
- claiming full 8/8 Section 5.2, Section 5.3, or Section 5.7 reproduction;
- using author logs as input geometry;
- using V3/V4 evidence or terminology;
- broad performance claims.
