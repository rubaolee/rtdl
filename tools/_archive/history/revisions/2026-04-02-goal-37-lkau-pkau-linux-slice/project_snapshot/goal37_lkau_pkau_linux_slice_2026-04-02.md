# Goal 37 LKAU PKAU Linux Slice

Date: 2026-04-02

## Summary

This round closes the first real `LKAU ⊲⊳ PKAU` family slice on the Linux Embree host.

Because the historical SpatialHadoop direct download links remain unavailable, the slice uses a bounded derived-input public OSM path:

- source endpoint: `https://overpass.kumi.systems/api/interpreter`
- frozen bbox label: `sunshine_tiny`
- frozen bbox: `-26.72,152.95,-26.55,153.10`

The run was executed on:

- host: `192.168.1.20`

## Source and Conversion Boundary

The current Australia lakes/parks slice is:

- derived-input, not exact-input
- bounded regional, not continent-scale
- built from OSM `way` geometry only
- not yet reconstructing multipolygon `relation` geometry

Frozen OSM filters:

- parks:
  - `way["leisure"="park"]`
  - `way["boundary"="national_park"]`
- lakes:
  - `way["natural"="water"]`

## Staged Inputs

Observed staged element counts on the Linux host:

- parks source elements: `264`
- lakes source elements: `280`

Observed converted closed-way counts:

- parks closed ways: `264`
- lakes closed ways: `280`

Converted CDB summary:

- parks features: `264`
- parks chains: `264`
- lakes features: `280`
- lakes chains: `280`

## Execution Result

Workload wiring for this slice:

- `lsi`: lakes segments as probe, parks segments as build
- `pip`: lakes probe points against parks polygons

Measured Linux-host result:

- `lsi`
  - CPU rows: `15`
  - Embree rows: `15`
  - parity: `true`
  - CPU sec: `6.397735154`
  - Embree sec: `0.047833586`
  - speedup: about `133.75x`
- `pip`
  - CPU rows: `73920`
  - Embree rows: `73920`
  - parity: `true`
  - CPU sec: `0.288967094`
  - Embree sec: `0.057857322`
  - speedup: about `4.99x`

## Interpretation

This is the first completed Lakes/Parks family slice on the current Embree-only track.

What is now proven:

- RTDL can acquire a real bounded Australia lakes/parks slice from a live public OSM source
- the slice can be converted into RTDL CDB inputs without custom offline GIS tooling
- `lsi` and `pip` are parity-clean between the Python oracle and the Embree backend on the Linux host
- Embree provides a large speedup over the Python oracle even on this first bounded family slice

What is still not closed:

- continent-scale `LKAU ⊲⊳ PKAU`
- exact-input Dryad or historical SpatialHadoop reproduction for this family
- multipolygon relation reconstruction
- the remaining lakes/parks continent families

## Acceptance

Goal 37 is accepted as:

- the first bounded Linux Embree `LKAU ⊲⊳ PKAU` slice
- not as full Australia-family completion
- not as continent-scale RayJoin reproduction
