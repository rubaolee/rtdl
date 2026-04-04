# Goal 54 LKAU PKAU Four-System Closure

Date: 2026-04-03

## Summary

This round upgrades the existing bounded Australia `LKAU ⊲⊳ PKAU` slice into
the same accepted four-system comparison standard used by Goal 50.

Compared systems:

- PostGIS
- native C oracle
- Embree
- OptiX

Execution host:

- `192.168.1.20`

## Boundary

This result is:

- bounded
- derived-input
- Australia only
- built from live OSM Overpass `way` geometry

This result is not:

- continent-scale `LKAU ⊲⊳ PKAU`
- exact-input Dryad or SpatialHadoop reproduction
- multipolygon relation reconstruction

Frozen source boundary:

- bbox label: `sunshine_tiny`
- bbox: `-26.72,152.95,-26.55,153.10`

## Inputs

Observed staged element counts:

- lakes source elements: `280`
- parks source elements: `264`

Observed converted feature counts:

- lakes features: `280`
- parks features: `264`

Load/index build time into PostGIS:

- `0.236009945 s`

## PostGIS Plan Quality

The accepted PostGIS comparison path used indexed plans for both workloads.

`lsi`:

- uses index: `true`
- index name: `left_segments_geom_idx`
- node types:
  - `Index Scan`
  - `Nested Loop`
  - `Seq Scan`
  - `Sort`
- execution time: `60.579 ms`

`pip`:

- uses index: `true`
- index name: `points_geom_idx`
- node types:
  - `Index Scan`
  - `Nested Loop`
  - `Seq Scan`
  - `Sort`
- execution time: `2.646 ms`

So this is an indexed spatial-database comparison, not a brute-force SQL pass.

## Result

### LSI

All four systems matched exactly.

- PostGIS:
  - rows: `15`
  - sec: `0.062259014`
- C oracle:
  - rows: `15`
  - sec: `1.913779297`
  - parity vs PostGIS: `true`
- Embree:
  - rows: `15`
  - sec: `2.128556676`
  - parity vs PostGIS: `true`
- OptiX:
  - rows: `15`
  - sec: `0.507164195`
  - parity vs PostGIS: `true`

### PIP

All four systems matched exactly.

- PostGIS:
  - full-matrix rows: `73920`
  - positive hits: `22`
  - sec: `0.004059802`
- C oracle:
  - rows: `73920`
  - sec: `0.091486801`
  - parity vs PostGIS: `true`
- Embree:
  - rows: `73920`
  - sec: `0.057067710`
  - parity vs PostGIS: `true`
- OptiX:
  - rows: `73920`
  - sec: `0.384443247`
  - parity vs PostGIS: `true`

## Interpretation

Goal 54 closes the first Lakes/Parks family slice under the same accepted
four-system standard already used for the bounded county/zipcode and
blockgroup/waterbodies packages.

What is now proven:

- the bounded Australia `LKAU ⊲⊳ PKAU` slice is parity-clean across:
  - PostGIS
  - native C oracle
  - Embree
  - OptiX
- the PostGIS comparison was performed with indexed spatial plans
- the existing Goal 37 Overpass-derived slice is strong enough to serve as a
  trustworthy bounded family analogue

What remains open:

- continent-scale `LKAU ⊲⊳ PKAU`
- the other lakes/parks continent families
- overlay-family closure for Table 4 / Figure 15

## Acceptance

Goal 54 should be accepted as:

- the first bounded four-system `LKAU ⊲⊳ PKAU` closure
- not as continent-scale Australia-family completion
- not as full lakes/parks matrix closure
