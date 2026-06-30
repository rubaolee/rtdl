# Goal 139 Public Pathology Data Acquisition and Conversion

## Decision

Goal 139 is accepted with a split public-data strategy:

- **NuInsSeg** is the preferred public source for the later unit-cell Jaccard line
- **MoNuSeg** is the first actually integrated public conversion surface now

## What landed

- public dataset registry and manifest support:
  - [goal139_pathology_data.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal139_pathology_data.py)
- manifest writer script:
  - [goal139_public_pathology_manifest.py](/Users/rl2025/rtdl_python_only/scripts/goal139_public_pathology_manifest.py)
- MoNuSeg XML parser:
  - [goal139_pathology_data.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal139_pathology_data.py)
- focused tests:
  - [goal139_pathology_data_test.py](/Users/rl2025/rtdl_python_only/tests/goal139_pathology_data_test.py)
  - [monuseg_sample.xml](/Users/rl2025/rtdl_python_only/tests/fixtures/pathology/monuseg_sample.xml)

## Public sources recorded

- NuInsSeg:
  - Zenodo archive:
    - [NuInsSeg.zip](https://zenodo.org/api/records/10518968/files/NuInsSeg.zip/content)
  - size:
    - `1627427342` bytes
- MoNuSeg:
  - public data page:
    - [MoNuSeg Data](https://monuseg.grand-challenge.org/Data/)
  - public training-data link is exposed on that page via Google Drive

## Why NuInsSeg is preferred later

- It publishes segmentation masks in addition to ROI files.
- Goal 138’s current primitive uses unit-cell area semantics.
- That means mask-based public data is the better long-term semantic fit than raw freehand polygons.

## Why MoNuSeg is the first integrated converter now

- The repo currently has no built-in PNG image decoder dependency.
- MoNuSeg XML polygon annotations can be parsed now with stdlib-only tooling.
- So Goal 139 closes a real public annotation conversion path without pretending NuInsSeg mask ingestion is already solved.
- This means XML-to-polygon parsing is real now, not that MoNuSeg raw polygons already satisfy the stricter Goal 138 orthogonal integer-grid/unit-cell contract.

## Validation

- local focused tests:
  - `5 tests`, `OK`
- manifest generation:
  - clean

## Honest boundary

Goal 139 does **not** claim that public pathology data is already fully usable by the Goal 138 primitive.

Current reality:

- public data discovery and conversion have started
- MoNuSeg XML parsing is real
- NuInsSeg full mask ingestion is still a next-step task

## Recommended next goals

- Goal 140: `polygon_set_jaccard` closure above the primitive
- Goal 141: public-data/Linux audit
- Goal 142: docs and generate-only expansion
