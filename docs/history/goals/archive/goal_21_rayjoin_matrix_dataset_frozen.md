# Goal 21 Frozen RayJoin Matrix and Dataset Setup

This document is the frozen Goal 21 output for the Embree RayJoin reproduction program.

It defines:

- the paper artifact mapping,
- dataset provenance and acquisition status,
- local reduced-size profiles bounded to the current Mac,
- and the blocker handoff for Goal 22.

## 1. Artifact Matrix

| Paper Artifact | RTDL Workload(s) | Current Reproduction Status | Notes |
| --- | --- | --- | --- |
| Table 3 | `lsi`, `pip` | `planned` | Needs larger RayJoin-aligned dataset pairs plus bounded local profiles. |
| Figure 13 | `lsi` | `partial-done` | Scaled synthetic analogue already exists; Goal 23 should rerun it under the frozen local profile policy. |
| Figure 14 | `pip` | `partial-done` | Scaled synthetic analogue already exists; Goal 23 should rerun it under the frozen local profile policy. |
| Table 4 | `overlay` | `planned` | Must be labeled as overlay-seed analogue rather than full overlay materialization. |
| Figure 15 | `overlay` | `planned` | Derived from Table 4 analogue outputs; same fidelity caveat as Table 4. |

## 2. Dataset Families and Provenance

| Paper Pair / Family | RTDL Target Workloads | Source Family | Preferred Provenance | Current Status | Local Embree Plan |
| --- | --- | --- | --- | --- | --- |
| `County ⊲⊳ Zipcode` | `lsi`, `pip`, `overlay` | `USCounty` + `Zipcode` | `exact-input` preferred | `partial` | Use checked-in county fixture for parity now; add zipcode acquisition/conversion in Goal 22. |
| `Block ⊲⊳ Water` | `lsi`, `pip`, `overlay` | `BlockGroup` + `WaterBodies` | `exact-input` preferred | `missing` | Needs acquisition/conversion path. |
| `LKAF ⊲⊳ PKAF` | `lsi`, `pip`, `overlay` | Lakes + Parks / Africa | `exact-input` preferred, `derived-input` acceptable | `missing` | Acquire or derive continent pair. |
| `LKAS ⊲⊳ PKAS` | `lsi`, `pip`, `overlay` | Lakes + Parks / Asia | `exact-input` preferred, `derived-input` acceptable | `missing` | Acquire or derive continent pair. |
| `LKAU ⊲⊳ PKAU` | `lsi`, `pip`, `overlay` | Lakes + Parks / Australia | `exact-input` preferred, `derived-input` acceptable | `missing` | Acquire or derive continent pair. |
| `LKEU ⊲⊳ PKEU` | `lsi`, `pip`, `overlay` | Lakes + Parks / Europe | `exact-input` preferred, `derived-input` acceptable | `missing` | Acquire or derive continent pair. |
| `LKNA ⊲⊳ PKNA` | `lsi`, `pip`, `overlay` | Lakes + Parks / North America | `exact-input` preferred, `derived-input` acceptable | `missing` | Acquire or derive continent pair. |
| `LKSA ⊲⊳ PKSA` | `lsi`, `pip`, `overlay` | Lakes + Parks / South America | `exact-input` preferred, `derived-input` acceptable | `missing` | Acquire or derive continent pair. |

## 3. Fidelity Labels

Goal 23 must label every generated table row and figure input as one of:

- `exact-input`
- `derived-input`
- `fixture-subset`
- `synthetic-input`

Current frozen labeling policy:

- checked-in tiny fixtures: `fixture-subset`
- deterministic continent-scale reconstructions or sliced public datasets: `derived-input`
- directly acquired public RayJoin-paper source families: `exact-input`
- synthetic scalability generators: `synthetic-input`

## 4. Reduced Local Profiles

The default local package must stay in the `5–10 minute` range on this Mac.

### Figure 13 Local Profile (`lsi`)

- workload: `lsi`
- fidelity: `synthetic-input`
- distributions: `uniform`, `gaussian`
- fixed build size: `R = 100,000 polygons`
- varying probe series: `S = 100,000, 200,000, 300,000, 400,000, 500,000 polygons`
- intended budget: about `4–5 minutes`
- rationale: this is the current accepted local five-point LSI analogue profile

### Figure 14 Local Profile (`pip`)

- workload: `pip`
- fidelity: `synthetic-input`
- distributions: `uniform`, `gaussian`
- fixed build size: `R = 100,000 polygons`
- varying probe series: `S = 2,000, 4,000, 6,000, 8,000, 10,000 polygons`
- intended budget: about `3–5 minutes`
- rationale: this is the current accepted local five-point PIP analogue profile

### Table 3 Local Policy

Table 3 is not a single synthetic scaling series. Goal 22 must define one bounded local profile per dataset pair after acquisition/conversion status is known.

Frozen local policy:

- each Table 3 pair must have a bounded profile that stays under about `2 minutes` per workload on this Mac
- `lsi` and `pip` may use different scaled row counts for the same dataset family if needed
- total Table 3 package for all selected local cases should stay inside about `10 minutes`

### Table 4 / Figure 15 Local Policy

Overlay is more expensive semantically and currently remains an overlay-seed analogue.

Frozen local policy:

- each overlay dataset pair must stay under about `2 minutes`
- the full local overlay package should stay inside about `5 minutes`
- every output must explicitly say `overlay-seed analogue`

## 5. Current Exactness / Semantic Boundaries

The frozen Goal 21 setup inherits these repo-wide boundaries:

- precision remains `float_approx`
- PIP supports only `boundary_mode="inclusive"`
- `segment_polygon_hitcount` and `point_nearest_segment` are not part of the RayJoin paper target
- `overlay` is currently seed generation rather than full polygon materialization

## 6. Goal 22 Blockers

Goal 22 should address only the blockers named here.

### Dataset Blockers

1. reproducible acquisition/conversion path for `Zipcode`
2. reproducible acquisition/conversion path for `BlockGroup`
3. reproducible acquisition/conversion path for `WaterBodies`
4. reproducible acquisition/derivation path for continent-level lakes/parks pairs

### Evaluation Blockers

5. explicit Table 3 generator from acquired or derived dataset pairs
6. explicit Table 4 generator for the overlay-seed analogue
7. explicit Figure 15 generator from Table 4 analogue outputs

### Reporting Blockers

8. a report template that distinguishes:
   - exact reproduction,
   - derived local reproduction,
   - synthetic scalability analogue,
   - and overlay-seed analogue

## 7. Goal 23 Inputs

Goal 23 should consume exactly this frozen setup plus the Goal 22 resolved blockers.

No new paper-target case should be added to the reproduction package unless this document is updated first.
