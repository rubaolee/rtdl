# Goal 141 Public Jaccard Linux Audit

## Status

Accepted as a real public-data/Linux audit under an explicit derived-pair boundary.

## What landed

- public-data audit helper:
  - [goal141_public_jaccard_audit.py](/Users/rl2025/rtdl_python_only/src/rtdsl/goal141_public_jaccard_audit.py)
- Linux runner:
  - [goal141_public_jaccard_audit.py](/Users/rl2025/rtdl_python_only/scripts/goal141_public_jaccard_audit.py)
- focused tests:
  - [goal141_public_jaccard_audit_test.py](/Users/rl2025/rtdl_python_only/tests/goal141_public_jaccard_audit_test.py)

## Public-data source actually used

- dataset:
  - `MoNuSeg 2018 Training Data`
- public source page:
  - [MoNuSeg Data](https://monuseg.grand-challenge.org/Data/)
- downloaded training zip:
  - public Google Drive file linked from the challenge page
- XML slide used:
  - `MoNuSeg 2018 Training Data/Annotations/TCGA-38-6178-01Z-00-DX1.xml`

## Public-data derivation actually used

- the source XML contains freehand nucleus polygons, which do **not** directly satisfy the Goal 140 narrow orthogonal integer-grid contract
- so Goal 141 converts the first `16` nuclei from that XML into unit-cell coverage
- each covered unit cell is re-encoded as a `1x1` square polygon
- that yields the accepted RTDL input geometry for this narrow Jaccard line
- the right-hand set is then derived from the same real-data-based unit-cell polygon set by shifting it by `+1` cell in `x`

This is honest public-data evidence for the current workload, but it is **not**
the same claim as “MoNuSeg raw polygon Jaccard is directly closed.”

## Local results

- `python3 -m py_compile` on the new helper/script/tests:
  - clean
- local focused tests:
  - `3 tests`, `OK`

## Linux results

- focused tests on `lestat@192.168.1.20`:
  - `3 tests`, `OK`
- accepted public-data audit scale:
  - `polygon_limit = 16`
  - `copies = 1, 4`

Concrete dataset stats:

- raw polygons in the source XML:
  - `424`
- selected polygons for this closure:
  - `16`
- resulting unit-square polygons per side at base scale:
  - `8556`

Audit rows:

| copies | left_polygon_count | right_polygon_count | python_sec | cpu_sec | postgis_sec | python_parity_vs_postgis | cpu_parity_vs_postgis | jaccard_similarity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `1` | `8556` | `8556` | `0.135213` | `0.061195` | `4.362636` | `true` | `true` | `0.917956` |
| `4` | `34224` | `34224` | `0.497132` | `0.211040` | `54.827503` | `true` | `true` | `0.917956` |

Artifacts:

- [summary.json](/Users/rl2025/rtdl_python_only/docs/reports/goal141_public_jaccard_audit_artifacts_2026-04-06/summary.json)
- [summary.md](/Users/rl2025/rtdl_python_only/docs/reports/goal141_public_jaccard_audit_artifacts_2026-04-06/summary.md)

## Honest boundary

Goal 141 is a **public-data-derived** closure, not a raw public-data closure.

That distinction matters:

- the source annotations are real public MoNuSeg polygons
- the RTDL workload still requires unit-cell orthogonal polygons
- so the public XML is converted into unit-square polygons first
- and the left/right pair is derived by a deterministic shift because the dataset does not ship paired alternative segmentations for the same field

## Scale boundary observed during execution

An initial more aggressive Linux audit attempt with a larger polygon limit and a
larger copy matrix did not finish in a practical closure window. This goal is
therefore accepted on the smaller but still real public-data scale above,
rather than pretending the first larger run already counted as a clean audit.

## Recommended next goal

- Goal 142: docs and generate-only expansion for the Jaccard line
