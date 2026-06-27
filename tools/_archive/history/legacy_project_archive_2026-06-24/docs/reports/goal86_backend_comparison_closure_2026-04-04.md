# Goal 86 Report: Backend Comparison Closure

Date: 2026-04-04

## Objective

Summarize the current backend-vs-PostGIS state after the completed OptiX,
Embree, and Vulkan rounds.

## Scope

- workload family: `county_zipcode`
- query shape: positive-hit `pip`
- compared systems:
  - PostGIS
  - RTDL + OptiX
  - RTDL + Embree
  - RTDL + Vulkan

## Long Exact-Source Surface

This is the accepted exact-source long surface already used by the OptiX and
Embree closure goals.

### Prepared boundary

OptiX:

- backend:
  - first rerun in clean audit package: `3.429287890 s`
  - warmed prepared rerun: `1.147425041 s`
- PostGIS:
  - `3.139067540 s`
  - `3.142702609 s`
- parity: `true`

Embree:

- backend: `1.773865199 s`
- PostGIS: `3.402695205 s`
- parity: `true`

Vulkan:

- no accepted timed row
- failure on the same long surface:
  - `Vulkan PIP positive-hit output exceeds current Vulkan guardrail of 536870912 bytes`

### Repeated raw-input exact-source boundary

OptiX:

- first run: `3.602868046 s`
- repeated best: `1.086635833 s`
- PostGIS:
  - `3.133568043 s`
  - `3.121261025 s`
  - `3.148949364 s`
- parity: `true`

Embree:

- first run: `1.959970190 s`
- repeated best: `1.092190547 s`
- PostGIS:
  - `3.583030458 s`
  - `3.188612651 s`
- parity: `true`

Vulkan:

- not accepted on this boundary
- no published raw-input long exact-source package

## Bounded Vulkan Hardware-Backed Status

Goal 85 now adds two important Vulkan facts:

1. **Hardware validation is real**
   - `tests.rtdsl_vulkan_test` and the broader goal51 ladder run successfully on
     Linux Vulkan hardware
   - goal51 parity: `8 / 8` targets clean

2. **Bounded prepared exact-source CDB slice is parity-clean**
   - run 1:
     - Vulkan: `0.858198020 s`
     - PostGIS: `0.393232202 s`
   - run 2:
     - Vulkan: `0.333589648 s`
     - PostGIS: `0.400314831 s`
   - row count: `7863`
   - parity: `true`

This proves the Vulkan backend is real and working, but it does not yet lift
Vulkan into the same long exact-source comparison row as OptiX and Embree.

## Backend Status Summary

OptiX:

- parity-clean
- beats PostGIS on the accepted long exact-source prepared boundary once warmed
- beats PostGIS on the accepted repeated raw-input exact-source boundary

Embree:

- parity-clean
- beats PostGIS on the accepted long exact-source prepared boundary
- beats PostGIS on the accepted repeated raw-input exact-source boundary

Vulkan:

- parity-clean on the accepted hardware smoke ladder
- parity-clean on a bounded prepared exact-source CDB slice
- still blocked on the true long exact-source prepared surface by worst-case
  candidate-allocation guardrail

## Honest Claim Surface

Safe claims:

- RTDL now has **two mature high-performance backends** for the accepted long
  exact-source RayJoin-style `county_zipcode` positive-hit `pip` surface:
  - OptiX
  - Embree
- Vulkan is now **hardware-validated and parity-clean on bounded accepted
  surfaces**, but it is not yet part of the long exact-source performance
  closure.

Non-claims:

- this is not a claim that all backends are equally mature
- this is not a claim that Vulkan now matches OptiX or Embree on the long
  exact-source package

## Conclusion

The backend story is now clearer than before:

- OptiX and Embree provide the strong RTDL performance story against PostGIS on
  the accepted long exact-source surface
- Vulkan is no longer speculative, but it remains a bounded backend until the
  current candidate-allocation contract is redesigned for the long surface
