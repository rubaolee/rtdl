# Codex Consensus: Goal 228 Heavy v0.4 Nearest-Neighbor Performance

Date: 2026-04-10

## Verdict

Goal 228 is a valid heavy benchmark slice and is worth keeping.

## Reasons

- It upgrades the PostGIS baseline from temp-table loading only to indexed query
  execution with GiST indexes and `ANALYZE`.
- It uses a real-world-derived point corpus instead of tiny authored fixtures.
- It measures all relevant reopened `v0.4` backends:
  - `cpu`
  - `embree`
  - `optix`
  - `vulkan`
  - `postgis`
- It separates row-identity mismatches from pure distance-epsilon drift, which
  is the only honest way to compare `float_approx` GPU outputs against
  double-precision PostGIS.

## Main Findings

- `fixed_radius_neighbors` is performance-healthy on accelerated backends, but
  not yet fully contract-clean on the heavy real-world case because Embree,
  OptiX, and Vulkan all miss the same boundary rows.
- `knn_rows` is the clearest GPU success:
  - OptiX and Vulkan are dramatically faster than CPU, Embree, and PostGIS
  - row identity matches PostGIS
  - only bounded distance epsilon remains
- Embree is currently the weakest backend for `knn_rows` performance.

## Closure Position

This goal should be closed only after the Gemini review is saved and any real
measurement-honesty issues it finds are fixed.
