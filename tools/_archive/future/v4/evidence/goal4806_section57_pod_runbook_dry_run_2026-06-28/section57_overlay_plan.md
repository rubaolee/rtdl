# RayJoin Section 5.7 Overlay 8/8 Execution Plan

Dataset root: `data\rayjoin_section57_cdb`
Input provenance: `paper_preprocessed_cdb`
Preprocessed source: https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA

## Coverage

| Metric | Value |
|---|---:|
| overlay_pairs_total | 1 |
| overlay_pairs_input_ready | 0 |
| overlay_pairs_blocked | 1 |
| required_for_section57_full_reproduction | 8/8 overlay pairs with author_rt, rtdl_optix, and rtdl_embree results |

## Overlay Pairs

| Pair | Exact Inputs Ready | Blocker | Paper RayJoin Processing (Preprocess) Sec |
|---|---:|---|---:|
| County x Zipcode | False | missing exact CDB input(s): point_cdb/dtl_cnty/dtl_cnty_Point.cdb, point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb | 0.12 (0.07) |
