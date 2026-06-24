# RayJoin Exact Paper Reproduction Suite

This suite redefines the RayJoin benchmark app as exact reproduction of the ICS'24 RayJoin programs:

- LSI via RayJoin `query_exec -query=lsi`
- PIP via RayJoin `query_exec -query=pip`
- polygon overlay via RayJoin `polyover_exec`

Analogue inputs do not count as exact reproduction. Current RTDL overlay seed rows do not count as polygon overlay.

## Dataset Pairs

| Pair | Left CDB | Right CDB | Paper stats |
|---|---|---|---|
| County x Zipcode | `point_cdb/dtl_cnty/dtl_cnty_Point.cdb` | `point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb` | County 1.0M segs/3.1K polys; Zipcode 23.9M segs/32.2K polys |
| Block x Water | `point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb` | `point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb` | Block 29.3M segs/239.2K polys; Water 25.6M segs/463.6K polys |
| LKAF x PKAF | `point_cdb/lakes/Africa/lakes_Africa_Point.cdb` | `point_cdb/parks/Africa/parks_Africa_Point.cdb` | LKAF 1.8M segs/18.2K polys; PKAF 1.3M segs/25.7K polys |
| LKAS x PKAS | `point_cdb/lakes/Asia/lakes_Asia_Point.cdb` | `point_cdb/parks/Asia/parks_Asia_Point.cdb` | LKAS 10.3M segs/151.6K polys; PKAS 11.9M segs/172.6K polys |
| LKAU x PKAU | `point_cdb/lakes/Australia/lakes_Australia_Point.cdb` | `point_cdb/parks/Australia/parks_Australia_Point.cdb` | LKAU 1.2M segs/14.5K polys; PKAU 567.1K segs/12.8K polys |
| LKEU x PKEU | `point_cdb/lakes/Europe/lakes_Europe_Point.cdb` | `point_cdb/parks/Europe/parks_Europe_Point.cdb` | LKEU 27.9M segs/654.8K polys; PKEU 65.9M segs/1.9M polys |
| LKNA x PKNA | `point_cdb/lakes/North_America/lakes_North_America_Point.cdb` | `point_cdb/parks/North_America/parks_North_America_Point.cdb` | LKNA 69.3M segs/1.6M polys; PKNA 26.9M segs/303.0K polys |
| LKSA x PKSA | `point_cdb/lakes/South_America/lakes_South_America_Point.cdb` | `point_cdb/parks/South_America/parks_South_America_Point.cdb` | LKSA 2.4M segs/32.6K polys; PKSA 3.2M segs/49.5K polys |

## RTDL Program Status

| Program | RTDL OptiX route | RTDL Embree route | Status | Gap |
|---|---|---|---|---|
| lsi | prepared segment-pair intersection count | prepared segment-pair intersection count | `implemented` | Need exact paper input CDBs before full matrix timing. |
| pip | RayJoin CDB closest-hit face-id point-location | RayJoin CDB closest-hit face-id point-location | `implemented` | Need exact paper input CDBs before full matrix timing. |
| overlay | LSI + PIP + full overlay polygon assembly | LSI + PIP + full overlay polygon assembly | `missing_full_overlay` | Current RTDL overlay_seed rows are not enough; exact reproduction requires full polygon materialization. |

## Current Availability

| Case | Exact inputs | RTDL status | Blocker |
|---|---:|---|---|
| `lsi_county_zipcode` | False | `implemented` | missing exact CDB input(s): point_cdb/dtl_cnty/dtl_cnty_Point.cdb, point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb |
| `pip_county_zipcode` | False | `implemented` | missing exact CDB input(s): point_cdb/dtl_cnty/dtl_cnty_Point.cdb, point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb |
| `overlay_county_zipcode` | False | `missing_full_overlay` | missing exact CDB input(s): point_cdb/dtl_cnty/dtl_cnty_Point.cdb, point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb |
| `lsi_block_water` | False | `implemented` | missing exact CDB input(s): point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb, point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb |
| `pip_block_water` | False | `implemented` | missing exact CDB input(s): point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb, point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb |
| `overlay_block_water` | False | `missing_full_overlay` | missing exact CDB input(s): point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb, point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb |
| `lsi_lkaf_pkaf` | False | `implemented` | missing exact CDB input(s): point_cdb/lakes/Africa/lakes_Africa_Point.cdb, point_cdb/parks/Africa/parks_Africa_Point.cdb |
| `pip_lkaf_pkaf` | False | `implemented` | missing exact CDB input(s): point_cdb/lakes/Africa/lakes_Africa_Point.cdb, point_cdb/parks/Africa/parks_Africa_Point.cdb |
| `overlay_lkaf_pkaf` | False | `missing_full_overlay` | missing exact CDB input(s): point_cdb/lakes/Africa/lakes_Africa_Point.cdb, point_cdb/parks/Africa/parks_Africa_Point.cdb |
| `lsi_lkas_pkas` | False | `implemented` | missing exact CDB input(s): point_cdb/lakes/Asia/lakes_Asia_Point.cdb, point_cdb/parks/Asia/parks_Asia_Point.cdb |
| `pip_lkas_pkas` | False | `implemented` | missing exact CDB input(s): point_cdb/lakes/Asia/lakes_Asia_Point.cdb, point_cdb/parks/Asia/parks_Asia_Point.cdb |
| `overlay_lkas_pkas` | False | `missing_full_overlay` | missing exact CDB input(s): point_cdb/lakes/Asia/lakes_Asia_Point.cdb, point_cdb/parks/Asia/parks_Asia_Point.cdb |
| `lsi_lkau_pkau` | False | `implemented` | missing exact CDB input(s): point_cdb/lakes/Australia/lakes_Australia_Point.cdb, point_cdb/parks/Australia/parks_Australia_Point.cdb |
| `pip_lkau_pkau` | False | `implemented` | missing exact CDB input(s): point_cdb/lakes/Australia/lakes_Australia_Point.cdb, point_cdb/parks/Australia/parks_Australia_Point.cdb |
| `overlay_lkau_pkau` | False | `missing_full_overlay` | missing exact CDB input(s): point_cdb/lakes/Australia/lakes_Australia_Point.cdb, point_cdb/parks/Australia/parks_Australia_Point.cdb |
| `lsi_lkeu_pkeu` | False | `implemented` | missing exact CDB input(s): point_cdb/lakes/Europe/lakes_Europe_Point.cdb, point_cdb/parks/Europe/parks_Europe_Point.cdb |
| `pip_lkeu_pkeu` | False | `implemented` | missing exact CDB input(s): point_cdb/lakes/Europe/lakes_Europe_Point.cdb, point_cdb/parks/Europe/parks_Europe_Point.cdb |
| `overlay_lkeu_pkeu` | False | `missing_full_overlay` | missing exact CDB input(s): point_cdb/lakes/Europe/lakes_Europe_Point.cdb, point_cdb/parks/Europe/parks_Europe_Point.cdb |
| `lsi_lkna_pkna` | False | `implemented` | missing exact CDB input(s): point_cdb/lakes/North_America/lakes_North_America_Point.cdb, point_cdb/parks/North_America/parks_North_America_Point.cdb |
| `pip_lkna_pkna` | False | `implemented` | missing exact CDB input(s): point_cdb/lakes/North_America/lakes_North_America_Point.cdb, point_cdb/parks/North_America/parks_North_America_Point.cdb |
| `overlay_lkna_pkna` | False | `missing_full_overlay` | missing exact CDB input(s): point_cdb/lakes/North_America/lakes_North_America_Point.cdb, point_cdb/parks/North_America/parks_North_America_Point.cdb |
| `lsi_lksa_pksa` | False | `implemented` | missing exact CDB input(s): point_cdb/lakes/South_America/lakes_South_America_Point.cdb, point_cdb/parks/South_America/parks_South_America_Point.cdb |
| `pip_lksa_pksa` | False | `implemented` | missing exact CDB input(s): point_cdb/lakes/South_America/lakes_South_America_Point.cdb, point_cdb/parks/South_America/parks_South_America_Point.cdb |
| `overlay_lksa_pksa` | False | `missing_full_overlay` | missing exact CDB input(s): point_cdb/lakes/South_America/lakes_South_America_Point.cdb, point_cdb/parks/South_America/parks_South_America_Point.cdb |
