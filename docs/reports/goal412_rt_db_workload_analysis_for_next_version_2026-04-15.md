# Goal 412 Report: RT Database Workload Analysis For The Next Version

Date: 2026-04-15
Goal: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_412_rt_db_workload_analysis_for_next_version.md`
Sources:
- `/Users/rl2025/Downloads/2024-rtscan.pdf`
- `/Users/rl2025/Downloads/2025-raydb.pdf`

## Question

For the next RTDL version, what kind of database-style operations should be
supported if RTDL is not trying to become a full database system?

## Executive answer

RTDL should support a bounded family of **RT-friendly analytical database
workloads**, not a general DBMS.

The strongest common pattern across RTScan and RayDB is:

- denormalized or pre-joined data
- offline or amortized index/BVH construction
- RT-based candidate discovery over an encoded geometric space
- limited operator fusion around scan/filter/group/aggregate
- non-RT or host-side handling for the rest of the query pipeline

The most defensible next-version RTDL target is therefore:

1. predicate-driven scan/filter workloads over denormalized records
2. grouped aggregation fused with scan over a bounded query area
3. offline-prepared RT indices/encodings as an explicit assumption

RTDL should **not** claim:

- a full SQL engine
- online joins as a first-class RT workload
- arbitrary relational operator closure
- transactional processing
- optimizer completeness

## What RTScan contributes

RTScan is not a full database engine. It is a specialized RT-core method for
accelerating **selection/index-scan style work**.

Its useful lessons are:

- RT cores are viable for **conjunctive predicate evaluation**
- the key transformation is to map several predicates into one RT job in 3D
- naive "one operator to one RT job" mappings underperform unless they solve:
  - parallelism
  - ray load
  - load balance under skew
- approximation plus refine is central:
  - `Uniform Encoding`
  - `Data Sieving`
  - `Matrix RT Refine`

The RTScan pattern is:

- build side:
  - encoded attribute groups
  - BVHs over those groups
  - approximate bit-vector filters
- query side:
  - a conjunctive predicate group transformed into query regions and rays
- refine side:
  - exact intersection/refinement over a small remaining region

This makes RTScan a strong argument that RTDL can support:

- range filter
- equality filter
- conjunctive scan
- approximate-filter + exact-refine scan
- skew-aware encoded scan

RTScan does **not** justify RTDL claiming:

- joins
- grouped aggregation by itself
- arbitrary SQL support
- a full query engine

## What RayDB contributes

RayDB is much broader than RTScan, but its strongest result still depends on a
bounded problem shape rather than general database completeness.

Its useful lessons are:

- the RT-friendly target is **data-warehouse / OLAP style**, not OLTP
- online joins are avoided by **offline denormalization**
- building BVHs during query execution is too expensive, so RT indices must be
  **pre-built offline**
- the winning pattern is **query-level operator fusion**, not one independent
  RT operator per relational operator
- the fused RT core is specifically:
  - `Scan`
  - `GroupBy`
  - `Aggregation`
- remaining operators like `Having` and `OrderBy` stay outside RT processing

RayDB therefore supports a more ambitious but still bounded RTDL direction:

- scan + grouped aggregate kernels over denormalized tables
- grouped `count`, `sum`, `avg`, `min`, and `max`
- operator fusion as a single RT job when the workload shape is right
- pre-built BVH/index families selected per query

RayDB also gives very important negative guidance:

- standalone RT acceleration of individual operators is not the right default
- joins should not be in the first RTDL DB-workload surface
- subqueries are only workable if rewritten away externally
- RTDL should not pretend to own the full optimizer/planner stack

RayDB also exposes one important performance boundary that should remain
explicit in RTDL planning:

- fused scan + aggregate without meaningful grouping is a weaker case
- when all hits contend on the same aggregate slot, atomic accumulation can
  collapse parallelism
- this means RTDL should treat grouped analytical workloads as the stronger
  first target than pure global aggregation

## Common pattern across both papers

RTScan and RayDB agree on a narrow but important point:

**RT helps when a data-processing workload can be remapped into spatially
encoded candidate discovery with a bounded post-processing step.**

That common pattern includes:

- offline encoding/index build
- workload-specific attribute grouping
- query-time RT traversal over only the relevant region
- direct access to already-encoded attributes at hit time
- restricted post-processing outside RT

The pattern does **not** support the stronger claim that RT is a natural fit
for every database operator.

## Recommended RTDL scope for the next version

### 1. Positioning

RTDL should present this as:

- **RT-accelerated analytical data workloads**
- or
- **RT database-style kernels for denormalized analytic queries**

RTDL should not present this as:

- a database engine
- a SQL runtime
- a general relational execution system

### 2. First workload family: predicate scan kernels

These are the most direct extension from RTScan.

Recommended kernels:

- `filter_scan`
- `range_scan`
- `conjunctive_scan`
- `scan_refine`

Expected shape:

- build side:
  - encoded columns or attribute groups
  - RT index/BVH over those groups
- probe side:
  - predicate bundle / query region
- emit:
  - row ids
  - match bitmap
  - projected values if bounded projection is supported

### 3. Second workload family: fused grouped aggregates

These are the strongest bounded extension from RayDB.

Recommended kernels:

- `grouped_count`
- `grouped_sum`
- `grouped_avg`
- `grouped_min`
- `grouped_max`
- one higher-level fused form:
  - `scan_group_aggregate`

Expected shape:

- build side:
  - denormalized records encoded into RT-addressable coordinates
  - pre-built BVH/index selected from a bounded set
- probe side:
  - scan predicates
  - aggregate spec
  - grouping spec
- emit:
  - grouped partials or final grouped aggregates

### 4. Data model assumption

The next version should be explicit that the database-style RTDL path assumes:

- denormalized / pre-joined wide tables
- or bounded flat record arrays equivalent to denormalized tables

That assumption should not be hidden. It is the reason the workload remains
tractable.

### 5. Build assumption

The next version should also be explicit that:

- encoded forms and BVHs are built offline or amortized
- query execution is not expected to build a fresh RT structure per query

This is a core practical lesson from RayDB.

## What should stay out of scope

For the first RTDL database-style version, keep these out:

- online join execution as a primary RT workload
- arbitrary multi-join query plans
- disjunctive predicates as a claimed first-class RT workload
- full SQL parsing/planning/optimization
- storage engine concerns
- updates / transactions / concurrency control
- row-store/column-store completeness claims
- arbitrary subquery support
- `OrderBy` / `Having` / window functions as RT-native workloads

Some of these may exist in the surrounding host application, but they should
not define the RTDL kernel surface.

## Proposed RTDL kernel interpretation

The current RTDL mental model already fits this bounded direction.

Recommended interpretation:

- `build`:
  - encoded denormalized records
  - attribute-group BVHs
  - optional approximate filter structures
- `probe`:
  - query predicate bundle
  - grouping/aggregate spec for bounded fused kernels
- `traverse`:
  - discover candidate records in the query region
- `refine`:
  - exact predicate confirmation
  - dedupe
  - group accumulation / partial aggregation
- `emit`:
  - matching row ids
  - grouped aggregates
  - partial aggregates for later host reduction

This preserves RTDL as a workload-kernel system rather than turning it into a
database front end.

## Recommended staged roadmap

### Stage 1

Add bounded truth-path kernels for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

using tiny denormalized tables and exact host-truth checks.

### Stage 2

Add oracle/native closure and one external correctness anchor such as:

- PostgreSQL
- DuckDB

for bounded denormalized workloads.

### Stage 3

Add backend closure for:

- Embree
- OptiX
- Vulkan

and measure them against the same bounded workload family.

### Stage 4

Only after the above is stable, consider:

- richer grouped aggregate forms
- larger encoded attribute sets
- optional partial support for more complex analytical patterns

## Final recommendation

The next RTDL version should support **database-like analytical kernels**, not
a database system.

The highest-confidence scope is:

- denormalized analytic data
- scan/filter kernels
- fused scan + group + aggregate kernels
- explicit offline encoding / BVH assumptions
- explicit non-goals for joins, full SQL, and general DBMS behavior

That is the scope justified by RTScan and RayDB. Anything broader would be
mis-scoped at this stage.
