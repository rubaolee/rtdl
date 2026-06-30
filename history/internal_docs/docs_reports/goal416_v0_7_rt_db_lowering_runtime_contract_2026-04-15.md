# Goal 416 Report: v0.7 RT DB Lowering Runtime Contract

Date: 2026-04-15
Goal:
`/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_416_v0_7_rt_db_lowering_runtime_contract.md`
Inputs:
- `/Users/rl2025/Downloads/2024-rtscan.pdf`
- `/Users/rl2025/Downloads/2025-raydb.pdf`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal415_v0_7_rt_db_execution_interpretation_2026-04-15.md`

## Question

What bounded lowering contract should RTDL adopt so that Embree, OptiX, and
Vulkan can implement the first DB kernel family honestly?

## Executive answer

RTDL should adopt **two backend-neutral RT lowerings**, not one pretend-general
database lowering:

1. `DbScanXYZ`
   - for `conjunctive_scan`
   - up to three primary scan clauses mapped to `x/y/z`
2. `DbGroupAggScan`
   - for `grouped_count` and `grouped_sum`
   - bounded to one group key and one aggregate field
   - with one primary scan axis and exact refine payload for the rest

Over-boundary cases should be decomposed into multiple bounded RT jobs or
rejected for the first backend wave.

## Backend-neutral primitive contract

Every RT backend should see the same logical primitive payload:

- `row_id`
- primary encoded coordinates
- exact scalar payload for refine
- optional group-key code
- optional aggregate value

The first implementation should use AABB/cube-style primitives, because:

- RTScan already demonstrates cube-region scanning
- AABB support is natural across Embree, OptiX, and Vulkan
- the kernels need region intersection semantics more than triangle mesh detail

## Lowering 1: `DbScanXYZ`

### Target kernel

- `conjunctive_scan`

### Intended use

- one to three primary conjunctive scan clauses
- scalar numeric columns only in the first backend wave

### Build lowering

1. Choose up to three scan clauses as primary RT clauses.
2. Uniform-encode those three columns into normalized integer ranges.
3. Emit one cube/AABB primitive per row positioned by the encoded
   `x/y/z` coordinates.
4. Store:
   - `row_id`
   - exact original values for all scan columns
   - optional payload fields for later projection

### Probe lowering

1. Convert each primary clause into an interval on its axis.
2. Form a cuboid query region.
3. If Data-Sieving-style summaries exist, shrink the refine region first.
4. Launch short matrix-style rays through the cuboid, not one long ray.

### Refine rule

At hit time:

- re-check the exact primary clauses
- check all remaining secondary scan clauses
- emit `row_id` only on exact success

### Over-boundary rule

If more than three scan clauses are present:

1. partition them into groups of at most three
2. run one `DbScanXYZ` RT job per group
3. intersect candidate row-id bitsets host-side
4. run final exact refine on the intersection

This mirrors RTScan's grouped-predicate logic and avoids pretending that
arbitrarily many clauses fit naturally into one 3D RT job.

## Lowering 2: `DbGroupAggScan`

### Target kernels

- `grouped_count`
- `grouped_sum`

### First-wave support bound

- exactly one group key
- exactly one aggregate field for `grouped_sum`
- conjunctive scan predicates only

### Layout

Use a bounded three-role layout inspired by RayDB:

- `x`
  - aggregate lane / value-distribution coordinate
- `y`
  - encoded group-key coordinate
- `z`
  - primary scan coordinate

The important point is not perfect relational completeness. The important point
is that the primitive payload carries all exact values needed for:

- group identification
- sum accumulation
- refine checks

### Build lowering

1. Encode one group key on `y`.
2. Encode one primary scan attribute on `z`.
3. Encode one aggregate-distribution coordinate on `x`.
   - for `grouped_count`, `x` may be a constant or row-spread coordinate
   - for `grouped_sum`, `x` distributes the measure field while the exact
     numeric value remains in payload
4. Store payload:
   - `row_id`
   - exact group key
   - exact aggregate value
   - remaining scan attributes for refine

### Probe lowering

1. Convert the primary scan clause into the `z` query interval.
2. Launch rays over the bounded `(x, y, z)` region selected for the grouped job.
3. On hit:
   - exact-refine any secondary scan clauses
   - emit a bounded partial keyed by the group code

### Emit/merge rule

- `grouped_count`
  - emit `(group_code, 1)` partials
- `grouped_sum`
  - emit `(group_code, value)` partials

The backend may accumulate locally, but the final merge remains bounded
host-side. This avoids overclaiming complete database aggregation on RT cores.

## Canonical numeric semantics for `grouped_sum`

For the first backend wave, `grouped_sum` parity is defined only for exact
integer sums:

- accepted aggregate types:
  - signed 64-bit integer
  - unsigned 64-bit integer
- correctness reference:
  - Python arbitrary-precision integer
- backend rule:
  - a backend may keep narrower native partials internally
  - but it must emit exact integer partials for the host merge

The first backend wave does not claim floating-point grouped-sum parity across
Embree, OptiX, and Vulkan. Floating-point `sum` remains out of scope until RTDL
defines:

- reduction order
- rounding behavior
- tolerated error model

## Why this split is acceptable

This contract preserves the real lessons of the papers:

- RTScan:
  - three-dimensional conjunctive candidate discovery
  - uniform encoding
  - region shrinkage
  - short-ray matrix traversal
- RayDB:
  - fuse the bounded core
  - keep the rest outside the RT job
  - pre-build a small family of usable BVHs/layouts

It also matches RTDL's actual scope:

- workload kernels
- not a query optimizer
- not a DBMS

## First-wave support matrix

### Supported

- `conjunctive_scan`
  - scalar conjunctive clauses
  - one to three primary RT clauses per job
  - host decomposition for any remaining clauses beyond the first three
- `grouped_count`
  - one group key
  - one primary scan clause in RT layout
  - secondary conjunctive refine clauses
- `grouped_sum`
  - one group key
  - one numeric sum field
  - one primary scan clause in RT layout
  - secondary conjunctive refine clauses

### Explicitly not first-wave

- disjunctive predicates
- arbitrary numbers of group keys
- grouped `avg/min/max` on RT backends
- joins
- subqueries
- full SQL lowering

## Operational capacity bounds

The first backend wave is only accepted under explicit bounded ceilings.

### Query-shape ceilings

- `conjunctive_scan`
  - one to three primary RT clauses per RT job
  - additional clauses require decomposition into more bounded jobs
- `grouped_count`
  - exactly one group key
  - up to three total scan clauses
- `grouped_sum`
  - exactly one group key
  - exactly one integer sum field
  - up to three total scan clauses

### Runtime ceilings

- max rows per RT job:
  - `1_000_000`
- max candidate rows emitted by one RT job before forced decomposition or
  fallback:
  - `250_000`
- max distinct groups accepted in one grouped RT job:
  - `65_536`

If a query exceeds one of these ceilings, the first-wave rule is:

- decompose into multiple bounded RT jobs if the kernel shape still fits
- otherwise reject RT lowering for that query and fall back to non-RT engines

### Skew rule

Even inside the ceilings above, a backend should reject or decompose an RT job
if one group or one refine region dominates the candidate fan-out enough to
collapse the expected RT parallelism. This is especially relevant for:

- very hot group keys
- very wide scan regions with weak refine
- grouped workloads that effectively degenerate into one global aggregate

## Backend implementation order

1. Embree
   - easiest place to prove the primitive/payload contract
   - CPU-side debug visibility
2. OptiX
   - same logical lowering on an actual RT-core path
3. Vulkan
   - match the OptiX contract as closely as possible

Only after all three use the same logical lowering should RTDL run the
cross-engine PostgreSQL correctness gate.

## Result

Goal 416 accepts the following backend contract:

- `conjunctive_scan` lowers through `DbScanXYZ`
- `grouped_count` and `grouped_sum` lower through `DbGroupAggScan`
- over-boundary cases are decomposed or rejected, not hand-waved
- Embree/OptiX/Vulkan must all implement the same logical primitive/payload
  model before RTDL claims DB RT-backend support
