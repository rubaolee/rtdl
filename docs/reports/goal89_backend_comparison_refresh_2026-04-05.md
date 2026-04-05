# Goal 89 Report: Backend Comparison Refresh

Date: 2026-04-05
Status: complete

## Objective

Refresh the accepted backend-vs-PostGIS comparison after Goals 87 and 88.

## Scope

- workload family: `county_zipcode`
- query shape: positive-hit `pip`
- compared systems:
  - PostGIS
  - RTDL + OptiX
  - RTDL + Embree
  - RTDL + Vulkan

## Long Exact-Source Surface

This is the same accepted long exact-source surface already used by the OptiX,
Embree, and now Vulkan exact-source rounds.

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

- backend:
  - `6.139390790 s`
  - `6.164127524 s`
- PostGIS:
  - `3.259119608 s`
  - `3.046611804 s`
- parity: `true`

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

- first run: `16.140240988 s`
- repeated best: `6.709643080 s`
- PostGIS:
  - `3.125241542 s`
  - `3.088001120 s`
  - `3.124289108 s`
- parity: `true`

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

- parity-clean on the accepted long exact-source prepared boundary
- parity-clean on the accepted long exact-source repeated raw-input boundary
- improves materially after the first raw-input call
- still slower than PostGIS on both accepted long exact-source boundaries

## Honest Claim Surface

Safe claims:

- RTDL now has two mature high-performance backends for the accepted long exact
  source RayJoin-style `county_zipcode` positive-hit `pip` surface:
  - OptiX
  - Embree
- Vulkan now has a complete long exact-source story on both prepared and
  repeated raw-input boundaries:
  - hardware-backed
  - parity-clean
  - not performance-competitive

Non-claims:

- this is not a claim that all three backends are equally mature
- this is not a claim that Vulkan now matches OptiX or Embree

## Conclusion

The backend story is now fully clarified:

- OptiX and Embree provide the strong RTDL performance story against PostGIS on
  the accepted long exact-source surface
- Vulkan is no longer blocked or unmeasured on that same surface
- Vulkan remains a supported but slower backend for this workload family
