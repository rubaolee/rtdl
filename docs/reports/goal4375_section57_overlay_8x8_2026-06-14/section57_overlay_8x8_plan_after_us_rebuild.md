# RayJoin Section 5.7 Overlay 8/8 Execution Plan

Dataset root: `/workspace/rayjoin_section57_data/cdb_topology`
Input provenance: `same_source_regenerated_cdb`
Preprocessed source: https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA

## Coverage

| Metric | Value |
|---|---:|
| overlay_pairs_total | 8 |
| overlay_pairs_input_ready | 2 |
| overlay_pairs_blocked | 6 |
| required_for_section57_full_reproduction | 8/8 overlay pairs with author_rt, rtdl_optix, and rtdl_embree results |

## Overlay Pairs

| Pair | Exact Inputs Ready | Blocker | Paper RayJoin Processing (Preprocess) Sec |
|---|---:|---|---:|
| County x Zipcode | True |  | 0.12 (0.07) |
| Block x Water | True |  | 0.23 (0.12) |
| LKAF x PKAF | False | missing exact CDB input(s): point_cdb/lakes/Africa/lakes_Africa_Point.cdb, point_cdb/parks/Africa/parks_Africa_Point.cdb | 0.01 (0.01) |
| LKAS x PKAS | False | missing exact CDB input(s): point_cdb/lakes/Asia/lakes_Asia_Point.cdb, point_cdb/parks/Asia/parks_Asia_Point.cdb | 0.04 (0.05) |
| LKAU x PKAU | False | missing exact CDB input(s): point_cdb/lakes/Australia/lakes_Australia_Point.cdb, point_cdb/parks/Australia/parks_Australia_Point.cdb | 0.01 (0.01) |
| LKEU x PKEU | False | missing exact CDB input(s): point_cdb/lakes/Europe/lakes_Europe_Point.cdb, point_cdb/parks/Europe/parks_Europe_Point.cdb | 0.2 (0.2) |
| LKNA x PKNA | False | missing exact CDB input(s): point_cdb/lakes/North_America/lakes_North_America_Point.cdb, point_cdb/parks/North_America/parks_North_America_Point.cdb | 0.25 (0.21) |
| LKSA x PKSA | False | missing exact CDB input(s): point_cdb/lakes/South_America/lakes_South_America_Point.cdb, point_cdb/parks/South_America/parks_South_America_Point.cdb | 0.02 (0.01) |
