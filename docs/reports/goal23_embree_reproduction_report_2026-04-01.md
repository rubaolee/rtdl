# RTDL Embree Reproduction of RayJoin Experiments

_Generated: 2026-04-01T15:05:13. Total package wall time: 289.38 s._

## Abstract

This report presents the current bounded local reproduction of the RayJoin evaluation structure on top of RTDL's Intel Embree backend.
The purpose is not to claim exact paper-scale equivalence. Instead, the report documents what the current Python-hosted DSL, lowered runtime, and Embree execution engine can already execute on a local Mac while preserving the frozen `5-10 minute` wall-time policy for iterative development.
The executed slice includes bounded analogues for Table 3, Figure 13, Figure 14, Table 4, and Figure 15. Missing dataset families remain explicitly labeled as source-identified and unexecuted.

## 1. Introduction

RayJoin evaluates spatial join workloads over ray-tracing style acceleration structures. RTDL is a Python-like DSL and runtime stack that aims to express the same workload family while remaining portable across backends.
In the current pre-NVIDIA phase, the concrete backend is Intel Embree. The work in Goal 23 therefore asks a narrower question: how much of the RayJoin experiment structure can be reproduced honestly on the bounded local Embree path, given current machine limits and incomplete access to the paper's preprocessed datasets?

## 2. RTDL Language Overview

RTDL exposes a compact kernel DSL with explicit geometry inputs, candidate traversal, predicate refinement, and emitted row schemas.
A workload such as `lsi` is written as a kernel over segment inputs, lowered into RTDL IR, then executed through a prepared Embree path. The same language surface also supports `pip`, `overlay`, `ray_tri_hitcount`, `segment_polygon_hitcount`, and `point_nearest_segment`.

## 3. Architecture

The current execution stack is: Python-like DSL -> `CompiledKernel` -> backend-oriented RayJoin-style plan -> prepared Embree execution -> raw or dictionary result materialization.
For Goal 23, all scalability-style runs use the low-overhead prepared raw execution path so the report reflects the current best local Embree implementation rather than the older dict-heavy runtime path.

## 4. Datasets and Fidelity Boundary

RTDL currently mixes three kinds of inputs: checked-in fixture subsets, deterministic derived enlargements, and synthetic generators. The fidelity labels in this report are critical because not all paper-original dataset families are locally executable yet.

### 4.1 Public Source Registry

| Asset | Status | Preferred Use |
| --- | --- | --- |
| `rayjoin_preprocessed_share` | `source-identified` | Preferred exact-input source for all paper dataset families when accessible. |
| `uscounty_arcgis` | `source-identified` | Exact-input source family for County ⊲⊳ Zipcode when using raw public data. |
| `zipcode_arcgis` | `source-identified` | Exact-input source family for County ⊲⊳ Zipcode when using raw public data. |
| `blockgroup_arcgis` | `source-identified` | Exact-input source family for Block ⊲⊳ Water when using raw public data. |
| `waterbodies_arcgis` | `source-identified` | Exact-input source family for Block ⊲⊳ Water when using raw public data. |
| `lakes_parks_spatialhadoop` | `source-identified` | Derived-input source for continent-level Lakes/Parks pairs when exact-input share is unavailable. |

### 4.2 Bounded Preparation Policy

| Dataset Handle | Status | Deterministic Rule |
| --- | --- | --- |
| `USCounty__Zipcode` | `source-identified` | Prefer exact-input Dryad share; otherwise derive a bounded CDB subset from raw USCounty + Zipcode with a fixed face/chain limit and stable sort by chain id. |
| `USACensusBlockGroupBoundaries__USADetailedWaterBodies` | `source-identified` | Prefer exact-input Dryad share; otherwise derive bounded CDB subsets from raw BlockGroup + WaterBodies with fixed chain/face limits and stable sort by chain id. |
| `lakes_parks_continents` | `source-identified` | If exact-input share is unavailable, derive each continent pair deterministically from public Lakes/Parks sources and then apply a fixed chain-limit reduction per continent. |

## 5. Experimental Setup

- Goal boundary: `bounded-local executable slice only; missing source-identified families remain reported but unexecuted`
- Backend: Intel Embree only; no NVIDIA GPU or OptiX path is used here.
- Runtime mode: prepared raw execution for bounded Figure 13 / Figure 14 analogue runs.
- Figure 13 profile: fixed `R=100000` polygons, `S=100000, 200000, 300000, 400000, 500000`.
- Figure 14 profile: fixed `R=100000` polygons, `S=2000, 4000, 6000, 8000, 10000`.
- Scalability iterations / warmup: `2` / `1`.
- Table iterations / warmup: `3` / `1`.

## 6. Results

### 6.1 Table 3 Executed Rows

| Paper Pair | Workload | Local Case | Fidelity | CPU Mean (s) | Embree Mean (s) | Speedup |
| --- | --- | --- | --- | ---: | ---: | ---: |
| County ⊲⊳ Zipcode | `lsi` | `county_fixture_subset_lsi` | `fixture-subset` | 0.000071 | 0.000169 | 0.42x |
| County ⊲⊳ Zipcode | `lsi` | `county_tiled_x8_lsi` | `derived-input` | 0.000624 | 0.000182 | 3.43x |
| County ⊲⊳ Zipcode | `pip` | `county_fixture_subset_pip` | `fixture-subset` | 0.000066 | 0.000085 | 0.78x |
| County ⊲⊳ Zipcode | `pip` | `county_tiled_x8_pip` | `derived-input` | 0.000986 | 0.000289 | 3.41x |

### 6.2 Missing / Unexecuted Families

| Paper Pair | Workload | Status | Source Requirement |
| --- | --- | --- | --- |
| Block ⊲⊳ Water | `lsi` | `missing` | Add public acquisition and conversion path before any bounded local analogue is treated as complete. |
| Block ⊲⊳ Water | `pip` | `missing` | Add public acquisition and conversion path before any bounded local analogue is treated as complete. |
| LKAF ⊲⊳ PKAF | `lsi` | `missing` | Acquire or derive the continent pair before bounded local runs. |
| LKAF ⊲⊳ PKAF | `pip` | `missing` | Acquire or derive the continent pair before bounded local runs. |
| LKAS ⊲⊳ PKAS | `lsi` | `missing` | Acquire or derive the continent pair before bounded local runs. |
| LKAS ⊲⊳ PKAS | `pip` | `missing` | Acquire or derive the continent pair before bounded local runs. |
| LKAU ⊲⊳ PKAU | `lsi` | `missing` | Acquire or derive the continent pair before bounded local runs. |
| LKAU ⊲⊳ PKAU | `pip` | `missing` | Acquire or derive the continent pair before bounded local runs. |
| LKEU ⊲⊳ PKEU | `lsi` | `missing` | Acquire or derive the continent pair before bounded local runs. |
| LKEU ⊲⊳ PKEU | `pip` | `missing` | Acquire or derive the continent pair before bounded local runs. |
| LKNA ⊲⊳ PKNA | `lsi` | `missing` | Acquire or derive the continent pair before bounded local runs. |
| LKNA ⊲⊳ PKNA | `pip` | `missing` | Acquire or derive the continent pair before bounded local runs. |
| LKSA ⊲⊳ PKSA | `lsi` | `missing` | Acquire or derive the continent pair before bounded local runs. |
| LKSA ⊲⊳ PKSA | `pip` | `missing` | Acquire or derive the continent pair before bounded local runs. |

### 6.3 Table 4 Overlay-Seed Analogue

| Local Case | Fidelity | CPU Mean (s) | Embree Mean (s) | Speedup |
| --- | --- | ---: | ---: | ---: |
| `overlay_fixture_subset` | `overlay-seed analogue / fixture-subset` | 0.000103 | 0.000123 | 0.84x |
| `overlay_tiled_x8` | `overlay-seed analogue / derived-input` | 0.000230 | 0.000178 | 1.29x |

### 6.4 Embedded Figures

#### Figure 13: Bounded LSI Analogue

![Figure 13 bounded LSI analogue](../../build/goal23_reproduction/figures/figure13_lsi_bounded.svg)

#### Figure 14: Bounded PIP Analogue

![Figure 14 bounded PIP analogue](../../build/goal23_reproduction/figures/figure14_pip_bounded.svg)

#### Figure 15: Bounded Overlay Speedup Analogue

![Figure 15 bounded overlay speedup analogue](../../build/goal23_reproduction/figures/figure15_overlay_speedup_bounded.svg)

## 7. Discussion

The executed results show that RTDL can already reproduce a meaningful bounded slice of the RayJoin experiment structure on the local Embree backend.
However, the report is intentionally explicit about the remaining gap: most Table 3 paper-original dataset families are still source-identified rather than fully acquired and converted. In addition, the overlay rows remain an `overlay-seed analogue` rather than a claim of full paper-equivalent polygon overlay execution.

## 8. Conclusion

Goal 23 completes the bounded local reproduction package: a paper-style report, embedded figures, explicit tables, dataset provenance, and fidelity labeling.
This report should be read as the current Embree-phase research baseline: reproducible, locally executable, and honest about what is executed, what is scaled, and what remains to be acquired before a fuller RayJoin reproduction can be claimed.

## Fidelity Labels

- `fixture-subset`: checked-in tiny public subset
- `derived-input`: deterministic enlargement or bounded reduction from an available source
- `synthetic-input`: deterministic synthetic generator
- `overlay-seed analogue`: current RTDL overlay path, not full polygon materialization
