# Goal 139: Public Pathology Data Acquisition and Conversion

## Purpose

Add a real public-data entry path for the pathology Jaccard line.

## Accepted scope

- record the real public datasets that matter first
- choose the preferred near-term source for RTDL
- land one real public annotation conversion surface in code
- keep the package honest about what is still missing

## Accepted closure for Goal 139

- public dataset registry in repo
- NuInsSeg recorded as the preferred future public mask source
- MoNuSeg XML parser landed as the first public polygon-annotation converter
- focused tests
- manifest/report artifacts

## Why the scope is split

- Goal 138 currently works on orthogonal integer-grid polygons with unit-cell area
- NuInsSeg matches that direction best because it publishes segmentation masks
- but the repo currently has no image decoder dependency for PNG mask ingestion
- MoNuSeg XML annotations are easier to integrate immediately with only stdlib tooling

So Goal 139 closes:

- acquisition knowledge for both datasets
- direct conversion support for MoNuSeg XML

And leaves for later:

- full NuInsSeg mask ingestion into RTDL polygons/cells

## Not claimed

- public-data Jaccard closure
- NuInsSeg full download performed in routine tests
- Goal 138 primitive already accepting raw freehand pathology polygons directly
