# RayJoin Paper Reproduction Matrix

This matrix freezes the initial paper-target evaluation surface for Goal 13 on the Embree baseline.

It is a planning and execution contract. A case should not be treated as part of the reproduction baseline until it appears here and has explicit status.

## Status Labels

- `done`: implemented, parity-checked, and wired into generated artifacts
- `planned`: accepted target, not yet fully implemented
- `deferred`: intentionally postponed to the NVIDIA phase or a later RTDL round

For dataset provenance details, see:

- [docs/rayjoin_paper_dataset_provenance.md](rayjoin_paper_dataset_provenance.md)

## Table 3 Target Matrix

Table 3 in the RayJoin paper reports LSI and PIP processing/preprocessing numbers across these artifact pairs:

- `County ⊲⊳ Zipcode`
- `Block ⊲⊳ Water`
- `LKAF ⊲⊳ PKAF`
- `LKAS ⊲⊳ PKAS`
- `LKAU ⊲⊳ PKAU`
- `LKEU ⊲⊳ PKEU`
- `LKNA ⊲⊳ PKNA`
- `LKSA ⊲⊳ PKSA`

| Paper Target | RTDL Workload | Embree Phase Status | Dataset Strategy | Notes |
| --- | --- | --- | --- | --- |
| County ⊲⊳ Zipcode | `lsi`, `pip` | `planned` | RayJoin-aligned public or reconstructed pair | Current local county subset is too small; needs larger pair for true analogue. |
| Block ⊲⊳ Water | `lsi`, `pip` | `planned` | RayJoin-aligned public or reconstructed pair | Needs provenance note and parity coverage. |
| LKAF ⊲⊳ PKAF | `lsi`, `pip` | `planned` | deterministic imported pair / `lakes_parks_Africa` | Should feed both table and figure inputs where practical. |
| LKAS ⊲⊳ PKAS | `lsi`, `pip` | `planned` | deterministic imported pair / `lakes_parks_Asia` | Same output contract as Table 3. |
| LKAU ⊲⊳ PKAU | `lsi`, `pip` | `planned` | deterministic imported pair / `lakes_parks_Australia` | Same output contract as Table 3. |
| LKEU ⊲⊳ PKEU | `lsi`, `pip` | `planned` | deterministic imported pair / `lakes_parks_Europe` | Same output contract as Table 3. |
| LKNA ⊲⊳ PKNA | `lsi`, `pip` | `planned` | deterministic imported pair / `lakes_parks_North_America` | Also relevant to the paper's precision section. |
| LKSA ⊲⊳ PKSA | `lsi`, `pip` | `planned` | deterministic imported pair / `lakes_parks_South_America` | Same output contract as Table 3. |

## Figure 13 Target Matrix

Figure 13 is LSI scalability:

- fixed `R = 5M polygons`
- varying `S = 1M .. 5M polygons`
- uniform distribution
- gaussian distribution
- query time and throughput

| Figure Target | RTDL Workload | Embree Phase Status | Dataset Strategy | Notes |
| --- | --- | --- | --- | --- |
| Figure 13(a) Uniform LSI Query Time | `lsi` | `done` | deterministic synthetic scalability generator | Implemented as a scaled Embree analogue with fixed `R=800` and varying `S=160..800`. |
| Figure 13(b) Gaussian LSI Query Time | `lsi` | `done` | deterministic synthetic scalability generator | Implemented as a scaled Embree analogue with fixed `R=800` and varying `S=160..800`. |
| Figure 13(c) Uniform LSI Throughput | `lsi` | `done` | derived from same benchmark run | Output as intersects/s analogue from RTDL result rows. |
| Figure 13(d) Gaussian LSI Throughput | `lsi` | `done` | derived from same benchmark run | Output as intersects/s analogue from RTDL result rows. |

## Figure 14 Target Matrix

Figure 14 is PIP scalability:

- fixed `R = 5M polygons`
- varying `S = 1M .. 5M polygons`
- uniform distribution
- gaussian distribution
- query time and throughput

| Figure Target | RTDL Workload | Embree Phase Status | Dataset Strategy | Notes |
| --- | --- | --- | --- | --- |
| Figure 14(a) Uniform PIP Query Time | `pip` | `done` | deterministic synthetic scalability generator | Implemented as a scaled Embree analogue with fixed `R=800` and varying `S=160..800`. |
| Figure 14(b) Gaussian PIP Query Time | `pip` | `done` | deterministic synthetic scalability generator | Implemented as a scaled Embree analogue with fixed `R=800` and varying `S=160..800`. |
| Figure 14(c) Uniform PIP Throughput | `pip` | `done` | derived from same benchmark run | Output as probe-points/s analogue from the generated point set. |
| Figure 14(d) Gaussian PIP Throughput | `pip` | `done` | derived from same benchmark run | Output as probe-points/s analogue from the generated point set. |

## Table 4 and Figure 15 Target Matrix

Table 4 reports polygon overlay execution time over:

- `County ⊲⊳ Zipcode`
- `Block ⊲⊳ Water`
- `LKAF ⊲⊳ PKAF`
- `LKAS ⊲⊳ PKAS`
- `LKAU ⊲⊳ PKAU`
- `LKEU ⊲⊳ PKEU`
- `LKNA ⊲⊳ PKNA`
- `LKSA ⊲⊳ PKSA`

Figure 15 is the overlay speedup summary derived from the same workload family.

| Paper Target | RTDL Workload | Embree Phase Status | Dataset Strategy | Notes |
| --- | --- | --- | --- | --- |
| Table 4 overlay cases | `overlay` | `planned` | same dataset pairs as Table 3 where available | Current RTDL overlay is compositional seed generation, not full materialization. Goal 56 closes the first bounded four-system `overlay-seed analogue` for `LKAU ⊲⊳ PKAU` `sunshine_tiny`. |
| Figure 15 speedup summary | `overlay` | `planned` | derived from Table 4 analogue outputs | Must be labeled as an `overlay-seed analogue`; Goal 56 provides the first accepted bounded four-system input row for that surface. |

## Current Execution Policy

For a paper-target case to move from `planned` to `done`, all of the following must exist:

1. RTDL workload path implemented
2. dataset provenance documented
3. CPU-vs-Embree parity check passing
4. evaluation matrix entry implemented
5. table/figure generator using that case implemented
6. 2-agent consensus accepting the step
