# Goal 195: v0.4 Working Plan

Date: 2026-04-09
Status: completed

## Result

The `v0.4` nearest-neighbor line now has an executable working plan.

The plan keeps `v0.4` inside RTDL's core non-graphical lane and avoids the
mistake of letting the `v0.3.0` demo line define the new milestone.

## Final plan

### v0.4 goal count

Recommended implementation count:

- **9 goals**

This is the smallest clean plan that keeps:

- public contract design
- correctness closure
- backend closure
- external evidence
- user-facing release material

all as separate reviewable slices.

## Recommended goal ladder

### Goal 1: freeze the public `fixed_radius_neighbors` contract

Define:

- inputs
- emitted row fields
- radius semantics
- `k_max` overflow behavior
- tie policy
- deterministic output ordering

### Goal 2: add the DSL/Python surface

Add the public user-facing workload entry point with no backend claims yet.

### Goal 3: build the truth path

Add:

- brute-force Python reference
- deterministic synthetic fixtures
- external-dataset ingestion helpers for the first public point sets

This is the correctness anchor.

### Goal 4: close CPU/oracle

Make the new workload real on the native CPU/oracle path and close row-parity
tests there.

### Goal 5: close Embree

Embree should be the first high-confidence accelerated backend for the new
family.

### Goal 6: add the external baseline harness

Add a bounded harness for:

- `scipy.spatial.cKDTree`
- moderate-size PostGIS comparison cases

This goal is about evidence, not product identity.

### Goal 7: close `knn_rows`

After `fixed_radius_neighbors` is stable, add:

- `knn_rows`

as the second workload in the same family.

### Goal 8: close OptiX and Vulkan under explicit bounded contracts

Bring GPU backends in after:

- the contract is stable
- the truth path is trusted
- the CPU/Embree path is already closed

### Goal 9: examples, docs, benchmark report, and release audit

Finish:

- release-facing example chain
- tutorial extension
- bounded benchmark evidence
- final `v0.4` audit and release package

## Why the count is 9 and not fewer

The extra slices are intentional.

- dataset/baseline work deserves its own goal
- `knn_rows` should not blur the first contract
- release-facing docs/examples should not be mixed into backend closure

That keeps the plan reviewable and prevents another long mixed-goal cleanup
phase.

## Dataset plan

The recommended dataset ladder is now fixed in:

- [datasets_and_baselines.md](/Users/rl2025/rtdl_python_only/docs/release_reports/v0_4_preview/datasets_and_baselines.md)

### Selected open dataset ladder

#### Tier 0: in-repo synthetic fixtures

Use for:

- exact contract tests
- tie and overflow cases
- backend parity

#### Tier 1: Natural Earth populated places

Source:

- <https://www.naturalearthdata.com/>

Use for:

- first public examples
- tutorial material
- small correctness smoke tests

#### Tier 2: NYC Street Tree Census

Source:

- <https://data.cityofnewyork.us/d/ye4j-rp7z>

Use for:

- medium-scale correctness and bounded scaling

#### Tier 3: Geofabrik OpenStreetMap extracts

Source:

- <https://download.geofabrik.de/>

Use for:

- larger dense point subsets
- stress tests
- release-benchmark subsets

## How PostGIS should back v0.4

PostGIS is useful, but only in a bounded support role.

### Recommended role

Use PostGIS to:

- verify moderate-size radius predicates with `ST_DWithin`
- verify nearest-order behavior with `<->` and `ORDER BY ... LIMIT`
- provide one familiar SQL baseline on the same public point subsets

### Not recommended

Do not make PostGIS:

- the primary truth path
- the only external benchmark
- the central identity argument for `v0.4`

### Why

The main `v0.4` story is:

- RTDL adds a first-class nearest-neighbor workload family

not:

- RTDL reproduces one SQL feature through another system

The stronger CPU baseline for day-to-day development is:

- `scipy.spatial.cKDTree`

with PostGIS used as supporting evidence where it is a clean fit.

## Sharp proposal and rebuttal

### Proposal A: make Hausdorff distance the headline

Rejected.

Reason:

- too derivative for the first milestone
- depends on nearest-neighbor machinery anyway
- harder to explain and test cleanly as the first public contract

### Proposal B: make KNN the first accepted workload

Rejected.

Reason:

- `fixed_radius_neighbors` has cleaner first-release row semantics
- easier overflow language
- easier tutorial surface

### Proposal C: make PostGIS the main external benchmark story

Rejected.

Reason:

- useful but too SQL-shaped for the whole release identity
- weaker development baseline than `scipy.spatial.cKDTree`
- better as supporting evidence than as the main backbone

## Final recommended execution story

The clean `v0.4` build line is:

1. freeze `fixed_radius_neighbors`
2. get the truth path right
3. close CPU/oracle and Embree
4. add the external baseline harness
5. then expand to `knn_rows` and GPU backends
6. finish with release-facing docs and audit

## Review outcome requested

The review for this goal should answer:

- Is the goal ladder tight enough?
- Are the dataset sources realistic and public?
- Is the PostGIS role honest and useful?
- Is the milestone still clearly non-graphical?
