# RTDL v0.1 Support Matrix

Date: 2026-04-05
Status: release candidate

## Reading guide

Status wording used below:

- `accepted`: part of the release claim surface
- `accepted, slower`: supported and verified, but not part of the strongest
  performance claim
- `trust reference`: correctness-oriented, not a peer performance backend

## Backend roles

| Backend | Role | Current status |
| --- | --- | --- |
| PostGIS | external indexed comparison baseline | accepted |
| Python oracle | correctness/trust reference on mini envelopes | accepted |
| native C oracle | correctness/trust reference on small envelopes | accepted |
| Embree | primary CPU performance backend | accepted |
| OptiX | primary NVIDIA GPU performance backend | accepted |
| Vulkan | portable GPU backend | accepted, slower |

## Accepted workload / boundary status

| Workload family | Boundary | PostGIS | Embree | OptiX | Vulkan | Claim status |
| --- | --- | --- | --- | --- | --- | --- |
| `county_zipcode` positive-hit `pip` exact-source | prepared | accepted | parity-clean, faster | parity-clean, warmed win | parity-clean, slower | strongest backend comparison surface |
| `county_zipcode` positive-hit `pip` exact-source | repeated raw-input | accepted | parity-clean, faster | parity-clean, faster | parity-clean, slower | strongest end-user performance surface |
| `county_zipcode` positive-hit `pip` bounded package | bounded accepted package | accepted | accepted | accepted | bounded-only older surface | trust anchor support |
| `blockgroup_waterbodies` positive-hit `pip` | bounded accepted package | accepted | accepted | accepted | not a promoted performance row | bounded package support |
| `LKAU ⊲⊳ PKAU` | bounded accepted package | accepted where applicable | accepted | not a main performance row | not a promoted row | bounded package support |
| `overlay` seed analogue | bounded accepted package | accepted where applicable | accepted | not a main performance row | not a promoted row | seed-generation analogue only |

## Current API limits

| Area | Current limit |
| --- | --- |
| native `pip` boundary mode | `inclusive` only |
| overlay | seed-generation analogue, not full polygon materialization |
| Vulkan performance | correct and supported, but slower on the accepted long exact-source surface |
| oracle performance | not a release performance target |

## Honest summary

- OptiX and Embree are the two mature high-performance RTDL backends for the
  accepted long exact-source `county_zipcode` positive-hit `pip` surface
- Vulkan is a real supported backend and part of the multi-backend story, but
  is not yet part of the strongest performance claim
- the bounded package remains the release trust anchor even though the strongest
  current performance evidence is the long exact-source `county_zipcode` row
