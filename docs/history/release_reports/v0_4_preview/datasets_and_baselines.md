# RTDL v0.4 Preview: Datasets And Baselines

## Dataset ladder

### Tier 0: deterministic synthetic fixtures

Use in-repo generated fixtures first:

- uniform grids
- clustered Gaussian clouds
- adversarial tie cases
- empty and overflow cases

Purpose:

- contract tests
- tie-policy tests
- exact row-order tests
- backend parity checks

### Tier 1: small public point datasets

Recommended first public dataset:

- Natural Earth populated places
  - source: <https://www.naturalearthdata.com/>

Why:

- public domain
- easy to redistribute or mirror in reduced form
- small enough for copy-paste examples and tutorial material

Use:

- first external correctness smoke
- tutorial examples
- release-facing example artifacts

### Tier 2: medium-density civic point datasets

Recommended medium-density public dataset:

- NYC Street Tree Census
  - source: <https://data.cityofnewyork.us/d/ye4j-rp7z>

Why:

- public city dataset
- real urban point density
- stable enough for repeatable medium-scale checks

Use:

- bounded scaling checks
- moderate-size radius-neighbor validation
- public benchmark appendix

### Tier 3: dense regional point extracts

Recommended dense real-world source:

- Geofabrik OpenStreetMap regional extracts
  - source: <https://download.geofabrik.de/>

Recommended derived inputs:

- OSM point features directly
- centroids derived from polygons when the derivation is explicitly documented

Why:

- easy access to real regional point distributions
- multiple size tiers by geography
- strong realism for neighbor workloads

Use:

- release-benchmark subsets
- backend stress tests
- larger-scale evaluation once correctness is already closed

## Baseline ladder

### Required truth paths

- brute-force Python reference
- native CPU/oracle implementation

These are the correctness anchors.

### Required external CPU baseline

- `scipy.spatial.cKDTree`
  - docs:
    - <https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.cKDTree.html>
    - <https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.cKDTree.query_ball_point.html>

Use:

- radius-neighbor baseline for `fixed_radius_neighbors`
- KNN baseline for `knn_rows`

### Optional literature-comparison baselines

Only when reproducible on the target host:

- RTNN comparison-set libraries
- `PCLOctree`
- `FRNN`
- `FastRNN`

These are helpful for research positioning but should not block the core
release.

## PostGIS role

PostGIS should support `v0.4`, but not define it.

### What PostGIS can do for us

- verify moderate-scale radius predicates with `ST_DWithin`
- verify nearest-order behavior with the `<->` operator and `ORDER BY ... LIMIT`
- provide a familiar SQL baseline on public point datasets
- help demonstrate that RTDL remains relevant to classic spatial-data users

Reference:

- PostGIS nearest-neighbour searching workshop:
  - <https://postgis.net/workshops/postgis-intro/knn.html>

### What PostGIS should not be in v0.4

- not the primary truth path
- not the only benchmark story
- not the implementation model for RTDL semantics

Reason:

- `v0.4` is about a direct nearest-neighbor runtime workload, not just a SQL
  wrapper comparison

## Practical release recommendation

For `v0.4`, the benchmark/evidence ladder should be:

1. brute-force Python reference
2. native CPU/oracle
3. `scipy.spatial.cKDTree`
4. bounded PostGIS comparison on the same public point subsets
5. optional wider library comparisons if they are reproducible
