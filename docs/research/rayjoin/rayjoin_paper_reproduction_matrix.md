# RayJoin Paper Reproduction Matrix

This matrix freezes the initial paper-target evaluation surface for Goal 13 on the Embree baseline.

It is a planning and execution contract. A case should not be treated as part of the reproduction baseline until it appears here and has explicit status.

## Status Labels

- `done-bounded`: implemented, reviewed, and accepted as a bounded analogue or
  bounded package closure
- `planned`: accepted target, not yet fully implemented
- `deferred-unavailable`: intentionally excluded from bounded closure because
  the current public acquisition path is unstable or unavailable

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

| Paper Target | RTDL Workload | Current Status | Dataset Strategy | Notes |
| --- | --- | --- | --- | --- |
| County ⊲⊳ Zipcode | `lsi`, `pip` | `done-bounded` | bounded exact-source package on `top4_tx_ca_ny_pa` | Accepted four-system package via Goal 50 / Goal 59. |
| Block ⊲⊳ Water | `lsi`, `pip` | `done-bounded` | bounded exact-source analogue via `BlockGroup ⊲⊳ WaterBodies` `county2300_s10` | Accepted four-system package on the closest stable public family available in the repo. |
| LKAF ⊲⊳ PKAF | `lsi`, `pip` | `deferred-unavailable` | `lakes_parks_Africa` | Public acquisition path proved unstable; excluded from bounded closure. |
| LKAS ⊲⊳ PKAS | `lsi`, `pip` | `deferred-unavailable` | `lakes_parks_Asia` | Unstaged continent pair; not required for bounded closure under the current rule. |
| LKAU ⊲⊳ PKAU | `lsi`, `pip` | `done-bounded` | bounded derived-input `sunshine_tiny` analogue | Accepted four-system bounded Australia analogue via Goal 54 / Goal 59. |
| LKEU ⊲⊳ PKEU | `lsi`, `pip` | `deferred-unavailable` | `lakes_parks_Europe` | Unstaged continent pair; not required for bounded closure under the current rule. |
| LKNA ⊲⊳ PKNA | `lsi`, `pip` | `deferred-unavailable` | `lakes_parks_North_America` | Unstaged continent pair; not required for bounded closure under the current rule. |
| LKSA ⊲⊳ PKSA | `lsi`, `pip` | `deferred-unavailable` | `lakes_parks_South_America` | Unstaged continent pair; not required for bounded closure under the current rule. |

## Figure 13 Target Matrix

Figure 13 is LSI scalability:

- fixed `R = 5M polygons`
- varying `S = 1M .. 5M polygons`
- uniform distribution
- gaussian distribution
- query time and throughput

| Figure Target | RTDL Workload | Current Status | Dataset Strategy | Notes |
| --- | --- | --- | --- | --- |
| Figure 13(a) Uniform LSI Query Time | `lsi` | `done-bounded` | deterministic synthetic scalability generator | Accepted scaled analogue. |
| Figure 13(b) Gaussian LSI Query Time | `lsi` | `done-bounded` | deterministic synthetic scalability generator | Accepted scaled analogue. |
| Figure 13(c) Uniform LSI Throughput | `lsi` | `done-bounded` | derived from same benchmark run | Accepted scaled analogue. |
| Figure 13(d) Gaussian LSI Throughput | `lsi` | `done-bounded` | derived from same benchmark run | Accepted scaled analogue. |

## Figure 14 Target Matrix

Figure 14 is PIP scalability:

- fixed `R = 5M polygons`
- varying `S = 1M .. 5M polygons`
- uniform distribution
- gaussian distribution
- query time and throughput

| Figure Target | RTDL Workload | Current Status | Dataset Strategy | Notes |
| --- | --- | --- | --- | --- |
| Figure 14(a) Uniform PIP Query Time | `pip` | `done-bounded` | deterministic synthetic scalability generator | Accepted scaled analogue. |
| Figure 14(b) Gaussian PIP Query Time | `pip` | `done-bounded` | deterministic synthetic scalability generator | Accepted scaled analogue. |
| Figure 14(c) Uniform PIP Throughput | `pip` | `done-bounded` | derived from same benchmark run | Accepted scaled analogue. |
| Figure 14(d) Gaussian PIP Throughput | `pip` | `done-bounded` | derived from same benchmark run | Accepted scaled analogue. |

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

| Paper Target | RTDL Workload | Current Status | Dataset Strategy | Notes |
| --- | --- | --- | --- | --- |
| Table 4 overlay cases | `overlay` | `done-bounded` | bounded overlay-seed analogue on available package families | Current RTDL overlay is compositional seed generation, not full materialization. Goal 56 closes the first accepted four-system row on `LKAU ⊲⊳ PKAU` `sunshine_tiny`, and Goal 23 provides bounded Embree analogue rows. |
| Figure 15 speedup summary | `overlay` | `done-bounded` | derived from bounded overlay analogue outputs | Must be labeled as an `overlay-seed analogue`; accepted bounded closure exists, not paper-identical full overlay. |

## Current Execution Policy

For a paper-target case to move from `planned` to `done-bounded`, all of the
following must exist:

1. RTDL workload path implemented
2. dataset provenance documented
3. CPU-vs-Embree parity check passing
4. evaluation matrix entry implemented
5. table/figure generator using that case implemented
6. 2-agent consensus accepting the step

Cases may instead move to `deferred-unavailable` when the blocker is external
dataset acquisition instability rather than implementation status.
