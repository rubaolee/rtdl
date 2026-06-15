# RayJoin Exact Paper Reproduction Contract

This document supersedes the older bounded-analogue RayJoin benchmark framing for the top-priority RayJoin track.

## Purpose

The RayJoin benchmark app is now defined as exact reproduction of the RayJoin ICS'24 program surface:

1. `query_exec -query=lsi`
2. `query_exec -query=pip`
3. `polyover_exec`

The comparison target is:

| Implementation | Meaning |
|---|---|
| RayJoin author code | `rubaolee/RayJoin` / paper implementation, measured on our pod |
| RTDL OptiX | RTDL program using NVIDIA OptiX / RT cores |
| RTDL Embree | RTDL program using Intel Embree CPU BVH traversal |

## Non-Negotiable Rules

- Analogue, fixture-subset, or synthetic inputs do not count as exact paper reproduction.
- RTDL `overlay_seed` rows do not count as polygon overlay.
- A row is public-ready only if the exact input status, backend route, correctness contract, and timing protocol are recorded together.
- Published RayJoin paper numbers are historical reference values; the fair measured comparison is RayJoin author code vs RTDL OptiX vs RTDL Embree on the same pod and same input files.
- `same_source_regenerated_cdb` inputs may be used for an apples-to-apples RayJoin-author-code vs RTDL comparison, but they are not labeled `paper_preprocessed_cdb` unless their CDB stats and provenance match the paper artifacts.
- RTDL is a general language/runtime system, not a RayJoin-specific rewrite. RTDL reports must not imply a guarantee that generic RTDL plus partners will beat hand-specialized C++/CUDA/OptiX code.
- RTDL reports must separate end-to-end time from app ingestion, packed-cache load/pack, backend prepare, native traversal, output materialization, and postprocess time when those phases are material.
- Avoidable Python-side CDB parsing, repeated packing, repeated materialization, or host/device ping-pong is an RTDL/partner optimization debt, not an acceptable public-performance excuse.

## Dataset Matrix

The exact suite uses the eight paper real-world pairs and RayJoin's `point_cdb` path layout:

| Pair | Left CDB | Right CDB |
|---|---|---|
| County x Zipcode | `point_cdb/dtl_cnty/dtl_cnty_Point.cdb` | `point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb` |
| Block x Water | `point_cdb/USACensusBlockGroupBoundaries/USACensusBlockGroupBoundaries_Point.cdb` | `point_cdb/USADetailedWaterBodies/USADetailedWaterBodies_Point.cdb` |
| LKAF x PKAF | `point_cdb/lakes/Africa/lakes_Africa_Point.cdb` | `point_cdb/parks/Africa/parks_Africa_Point.cdb` |
| LKAS x PKAS | `point_cdb/lakes/Asia/lakes_Asia_Point.cdb` | `point_cdb/parks/Asia/parks_Asia_Point.cdb` |
| LKAU x PKAU | `point_cdb/lakes/Australia/lakes_Australia_Point.cdb` | `point_cdb/parks/Australia/parks_Australia_Point.cdb` |
| LKEU x PKEU | `point_cdb/lakes/Europe/lakes_Europe_Point.cdb` | `point_cdb/parks/Europe/parks_Europe_Point.cdb` |
| LKNA x PKNA | `point_cdb/lakes/North_America/lakes_North_America_Point.cdb` | `point_cdb/parks/North_America/parks_North_America_Point.cdb` |
| LKSA x PKSA | `point_cdb/lakes/South_America/lakes_South_America_Point.cdb` | `point_cdb/parks/South_America/parks_South_America_Point.cdb` |

The paper reports the dataset statistics in Table 2. The suite stores those labels as provenance expectations; exact CDB files still need direct availability or deterministic regeneration from the paper's public sources. The RayJoin README's old preprocessed Dryad share is the preferred paper-preprocessed source when accessible; if it is unavailable, regenerated public-source CDBs must be labeled `same_source_regenerated_cdb`.

## Program Mapping

| Program | RayJoin author command | Input contract | RTDL OptiX route | RTDL Embree route | Current RTDL status |
|---|---|---|---|---|---|
| LSI | `query_exec -query=lsi` | all edges from query map S against base map R | prepared segment-pair intersection count | prepared segment-pair intersection count | implemented |
| PIP | `query_exec -query=pip` | all points from query map S via `S.get_points()` against base map R | directed-segment closest-hit face-id point-location | directed-segment closest-hit face-id point-location | implemented |
| Overlay | `polyover_exec` | LSI, vertex PIP in both directions, midpoint classification, optional output-chain write when `-output` is supplied | LSI + PIP + midpoint classification; optional output-chain assembly | LSI + PIP + midpoint classification; optional output-chain assembly | implemented compute path; optional output assembly |

The PIP row is intentionally strict: one representative point per CDB chain is a bounded/legacy RTDL probe, not the RayJoin paper PIP query stream.

## Timing Protocol

Default RayJoin paper-script parameters:

- `-grid_size=15000`
- `-xsect_factor 0.1`
- `-enlarge=3.5`
- `-serialize=/dev/shm`
- `-warmup=5`
- `-repeat=5`
- mode default for author-code comparison: `rt`

The runner must also be able to emit RayJoin `grid` and `lbvh` commands for reference, because the original scripts measure those modes.

## RTDL Partner And Overhead Policy

The RayJoin CDB file format is app-specific. RTDL may use an app-level partner for CDB parsing, packed-array layout, packed-cache creation, and mmap/cache reuse. This is consistent with RTDL's architecture: generic RT engine plus RTDL primitives plus app-specific partner logic.

The RTDL exact-suite runner enables a RayJoin CDB packed-array partner cache by default at:

`<dataset-root>/.rtdl_rayjoin_overlay_packed_cache`

Runner controls:

- `--packed-cache-dir <path>` selects a cache directory.
- `--disable-packed-cache` disables the partner cache for diagnosis.

Public performance tables must include both:

| Timing View | Meaning |
|---|---|
| End-to-end | User-visible command time, including app ingestion/cache/pack and RTDL execution |
| Compute / native | RTDL primitive execution phases after data are already in the required packed layout |

If RTDL is slower than RayJoin author code, the report must classify the gap as necessary generality, partner/cache gap, materialization gap, transfer gap, correctness-contract cost, or unknown. Unknown gaps are not public-ready.

## First Execution Gate

The first exact-suite gate is not performance. It is source integrity:

1. Generate the exact-suite manifest.
2. Stage or regenerate all eight exact CDB pairs.
3. Scan CDB file stats and compare them to the paper Table 2 labels.
4. Run RayJoin author code on at least one exact pair for LSI, PIP, and overlay.
5. Run RTDL OptiX and RTDL Embree for LSI/PIP on that pair.
6. Use the RTDL exact overlay runner, not legacy `overlay_seed`, before claiming any overlay comparison.

The suite helper lives at `scripts/rayjoin_paper_reproduction_suite.py`; the core definition lives at `src/rtdsl/rayjoin_paper_suite.py`.
