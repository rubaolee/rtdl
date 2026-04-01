# RayJoin Public Dataset Sources

This document records the public-source acquisition picture for the remaining RayJoin paper dataset families in the Embree-only phase.

It is intentionally conservative:

- it distinguishes `source-identified` from `acquired`,
- it keeps the Dryad preprocessed share separate from raw public source families,
- and it records bounded-local preparation rules without claiming that every paper-scale dataset is already staged in the repo.

## Exact-Input Preferred Source

RayJoin's README points to a public Dryad share for preprocessed datasets:

- [RayJoin preprocessed datasets (Dryad)](https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA)

This is the preferred exact-input source for the paper families when it is accessible, because it avoids reconstructing the authors' CDB preprocessing pipeline from scratch.

## Raw Public Source Families

The RayJoin README also points to public source families that can be used when the exact-input share is unavailable or when a deterministic derived-input path is needed.

### U.S. Families

- USCounty
  - [ArcGIS item](https://www.arcgis.com/home/item.html?id=14c5450526a8430298b2fa74da12c2f4)
- Zipcode
  - [ArcGIS item](https://www.arcgis.com/home/item.html?id=d6f7ee6129e241cc9b6f75978e47128b)
- BlockGroup
  - [ArcGIS item](https://www.arcgis.com/home/item.html?id=1c924a53319a491ab43d5cb1d55d8561)
- WaterBodies
  - [ArcGIS item](https://www.arcgis.com/home/item.html?id=48c77cbde9a0470fb371f8c8a8a7421a)

As of this Goal 22 slice:

- `USCounty`, `Zipcode`, and `WaterBodies` resolve to current ArcGIS-hosted items.
- `BlockGroup` resolves to a currently listed ArcGIS item, but the item type is a retired layer-package listing rather than a clean Feature Service endpoint.
- all four are treated as `source-identified`, not `acquired`.

### Lakes / Parks Families

- [SpatialHadoop datasets page](https://spatialhadoop.cs.umn.edu/datasets.html)

RayJoin's README points to the SpatialHadoop dataset catalog for the Lakes and Parks family. For the continent-level paper pairs, the RayJoin scripts resolve the internal handles:

- `lakes_parks_Africa`
- `lakes_parks_Asia`
- `lakes_parks_Australia`
- `lakes_parks_Europe`
- `lakes_parks_North_America`
- `lakes_parks_South_America`

In the current RTDL policy:

- the Dryad share remains the preferred exact-input path,
- the SpatialHadoop catalog is the acceptable derived-input path,
- and any historical dead download link must remain labeled as a source problem rather than silently treated as acquired data.

## Bounded Local Preparation Policy

For the current Mac-only Embree reproduction phase, all public dataset work is bounded by a local runtime target of roughly `5-10 minutes` per experiment package.

This means:

- raw public input is not run directly at paper scale on this machine,
- exact-input is preferred when available,
- otherwise deterministic derived-input is acceptable,
- and every reduced local dataset must record the rule used to obtain it.

Current deterministic preparation rule:

- for CDB inputs already available locally, stable reduction is performed by chain order using fixed limits,
- and the reduced dataset is written back in CDB form with deterministic point formatting.

The helper functions for that path live in:

- [datasets.py](/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py)

## Current Status

- `USCounty__Zipcode`: `source-identified`
- `USACensusBlockGroupBoundaries__USADetailedWaterBodies`: `source-identified`
- `lakes_parks_*`: `source-identified`

None of those handles should yet be described as fully acquired exact-input datasets in the repo.
