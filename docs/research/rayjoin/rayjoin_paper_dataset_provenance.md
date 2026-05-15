# RayJoin Paper Dataset Provenance

This document records the dataset provenance plan for Goal 13.

Its purpose is to make the Embree-phase paper reproduction honest and reproducible:

- every paper target is mapped to a named dataset family,
- every RTDL case declares whether it uses exact-input, derived-input, fixture-subset, or synthetic-input,
- and every substitution is documented before benchmark results are treated as part of the reproduction baseline.

## Source References

The RayJoin repository README identifies the dataset families used in the paper:

- `USCounty`
- `Zipcode`
- `BlockGroup`
- `WaterBodies`
- `Lakes and Parks`

RayJoin README:

- [pwrliang/RayJoin README](https://github.com/pwrliang/RayJoin)

The README also links to the public source families:

- USCounty: [ArcGIS item](https://www.arcgis.com/home/item.html?id=14c5450526a8430298b2fa74da12c2f4)
- Zipcode: [ArcGIS item](https://www.arcgis.com/home/item.html?id=d6f7ee6129e241cc9b6f75978e47128b)
- BlockGroup: [ArcGIS item](https://www.arcgis.com/home/item.html?id=1c924a53319a491ab43d5cb1d55d8561)
- WaterBodies: [ArcGIS item](https://www.arcgis.com/home/item.html?id=48c77cbde9a0470fb371f8c8a8a7421a)
- Lakes and Parks: [SpatialHadoop datasets page](https://spatialhadoop.cs.umn.edu/datasets.html)

## Provenance Labels

Goal 13 uses these labels:

- `exact-input`
  - the dataset pair is directly sourced from the RayJoin paper's named dataset family
- `derived-input`
  - the dataset is deterministically derived from a source family by tiling, slicing, or scaling
- `fixture-subset`
  - the dataset is a checked-in small public subset used for parity and smoke checks
- `synthetic-input`
  - the dataset is deterministically generated and used only when no practical paper-aligned public input is available

## Table 3 / Table 4 Dataset Families

The RayJoin paper evaluation names these artifact pairs:

- `County ⊲⊳ Zipcode`
- `Block ⊲⊳ Water`
- `LKAF ⊲⊳ PKAF`
- `LKAS ⊲⊳ PKAS`
- `LKAU ⊲⊳ PKAU`
- `LKEU ⊲⊳ PKEU`
- `LKNA ⊲⊳ PKNA`
- `LKSA ⊲⊳ PKSA`

RayJoin's experiment scripts map those pairs to internal dataset names:

- `LKAF ⊲⊳ PKAF` -> `lakes_parks_Africa`
- `LKAS ⊲⊳ PKAS` -> `lakes_parks_Asia`
- `LKAU ⊲⊳ PKAU` -> `lakes_parks_Australia`
- `LKEU ⊲⊳ PKEU` -> `lakes_parks_Europe`
- `LKNA ⊲⊳ PKNA` -> `lakes_parks_North_America`
- `LKSA ⊲⊳ PKSA` -> `lakes_parks_South_America`

This mapping is visible in the RayJoin experiment scripts under `expr/draw/ag.py` and `expr/draw/draw_speedup.py`.

The current bounded-closure provenance policy for them is:

| Paper Pair | Source Family | Current RTDL Provenance Plan | Current Status | Notes |
| --- | --- | --- | --- | --- |
| County ⊲⊳ Zipcode | USCounty + Zipcode | accepted bounded exact-source package on `top4_tx_ca_ny_pa` | `done-bounded` | Accepted four-system bounded package. |
| Block ⊲⊳ Water | BlockGroup + WaterBodies | accepted bounded exact-source analogue on `county2300_s10` | `done-bounded` | The stable public family currently available in RTDL is `BlockGroup ⊲⊳ WaterBodies`; this is the accepted bounded analogue used for closure. |
| LKAF ⊲⊳ PKAF | Lakes + Parks / `lakes_parks_Africa` | exact-input preferred or `derived-input` from public SpatialHadoop sets | `deferred-unavailable` | Africa pair naming is resolved, but the public acquisition path proved unstable. |
| LKAS ⊲⊳ PKAS | Lakes + Parks / `lakes_parks_Asia` | exact-input preferred or `derived-input` | `deferred-unavailable` | Unstaged continent pair. |
| LKAU ⊲⊳ PKAU | Lakes + Parks / `lakes_parks_Australia` | accepted bounded derived-input `sunshine_tiny` analogue | `done-bounded` | Accepted four-system bounded analogue. |
| LKEU ⊲⊳ PKEU | Lakes + Parks / `lakes_parks_Europe` | exact-input preferred or `derived-input` | `deferred-unavailable` | Unstaged continent pair. |
| LKNA ⊲⊳ PKNA | Lakes + Parks / `lakes_parks_North_America` | exact-input preferred or `derived-input` | `deferred-unavailable` | Unstaged continent pair. |
| LKSA ⊲⊳ PKSA | Lakes + Parks / `lakes_parks_South_America` | exact-input preferred or `derived-input` | `deferred-unavailable` | Unstaged continent pair. |

## Current Checked-In Inputs

Today the RTDL repo contains these checked-in public fixture subsets:

- `tests/fixtures/rayjoin/br_county_subset.cdb`
- `tests/fixtures/rayjoin/br_soil_subset.cdb`

These are classified as:

- `fixture-subset`

They are valid for:

- parity tests,
- authored examples,
- small baseline runner cases,
- and regression coverage.

They are not yet sufficient for:

- full Table 3 analogue,
- or full Table 4 / Figure 15 analogue.

Figure 13 and Figure 14 are now supported through a scaled synthetic Embree analogue rather than through the original paper-scale inputs.

## Scalability Dataset Policy

Figures 13 and 14 require meaningful scaling series.

For the Embree phase, each scaling case must declare:

- generator type: `exact-input`, `derived-input`, or `synthetic-input`
- size series
- deterministic seed or deterministic transformation rule
- query/workload mapping

Preferred order for Goal 13:

1. `exact-input` large public dataset if practical
2. `derived-input` deterministic enlargement from a RayJoin-aligned public source
3. `synthetic-input` only if no practical public path exists

Current implemented Section 5.6 analogue:

- generator type: `synthetic-input`
- fixed build-side size: `R = 800 polygons`
- varying probe-side series: `S = 160, 320, 480, 640, 800 polygons`
- distributions: `uniform`, `gaussian`
- workload mapping:
  - `lsi`: polygon-set to segment-set conversion, throughput in intersections/s
  - `pip`: polygon-set to probe-point conversion, throughput in probe-points/s

## Overlay Fidelity Note

The paper's polygon overlay workload is an end application composed from LSI and PIP.

Current RTDL status:

- `overlay` is implemented as compositional seed generation
- not as full overlay polygon materialization

Therefore:

- Goal 13 can produce a Table 4 / Figure 15 analogue for the current RTDL overlay workload
- but every artifact must explicitly state that it is an Embree-phase overlay-seed analogue, not a full materialized overlay reproduction

## Required Deliverables Before Goal 13 Closure

For bounded paper closure, the dataset side must include:

1. a frozen provenance label for every case in the paper reproduction matrix
2. explicit size notes for all scaling cases
3. a clear statement for every substitution away from paper-original inputs
4. 2-agent review agreement that the provenance is honest enough for the Embree phase

Under the current closure rule, unstable or unavailable public acquisition paths
may be recorded as `deferred-unavailable` rather than blocking bounded closure.
