# Goal 136 Report: Jaccard Similarity Evaluation

Date: 2026-04-06
Status: accepted-with-notes

## Executive decision

RTDL may reasonably take on Jaccard similarity from the old pathology paper,
but only under a narrow and honest scope:

- accept **pathology-style polygon-set Jaccard**
- reject **generic arbitrary set-similarity / string-similarity Jaccard**
- enter through a lower-level spatial primitive first:
  - `polygon_pair_overlap_area_rows`
- then build the aggregate workload above it:
  - `polygon_set_jaccard`

So the right answer is:

- **yes, RTDL may pursue it as a narrow next direction**
- but **not** as a vague “generic Jaccard” feature

## What the old paper actually does

The 2012 paper is not about token-set similarity or MinHash-style approximate
similarity search.

It is about **spatial cross-comparison** of two polygon sets extracted from the
same pathology image, using Jaccard similarity:

- `J(P, Q) = |P ∩ Q| / |P ∪ Q|`

where:

- `P` and `Q` are sets of polygons
- the hard part is repeated computation of intersection/union areas across many
  candidate polygon pairs

The paper also makes two important workload assumptions:

1. the polygons are produced from pathology-image segmentations
2. the polygons have image-grid structure that the paper exploits heavily:
   - axis-aligned edges
   - integer-valued vertices

The old paper’s acceleration win is therefore not:

- generic exact polygon overlay

It is:

- high-throughput spatial cross-comparison for a special and important
  pathology polygon family

## Why this fits RTDL

It fits RTDL because it is still a spatial workload with the same broad shape:

1. candidate generation over polygon pairs
2. exact or accepted-specialized refine
3. aggregation into an application-level result

In other words:

- RTDL already knows how to do:
  - spatial candidate search
  - row materialization
  - per-case aggregation
  - PostGIS-backed validation
- the Jaccard line would add a **new geometric value primitive**:
  - overlap area

This is still within RTDL’s non-graphical spatial-computing identity.

## Why it is not already covered

Current RTDL does **not** already have this feature.

The main reason is simple:

- current `overlay` is a seed-generation analogue
- it does **not** compute full overlap geometry or overlap area

Current RTDL also has no accepted first-class primitive for:

- exact polygon-pair intersection area
- exact polygon-pair union area

So although the workload is spatial and legitimate, it is **not** a trivial
rename of any existing feature.

## Why RTDL may do it

RTDL may take it on for four reasons:

1. **Historical fit**
- the workload comes directly from Rubao Lee’s older research line
- it is not random scope creep

2. **Spatial fit**
- it is still polygon-vs-polygon spatial cross-comparison
- candidate pruning still matters

3. **Product fit**
- it would broaden RTDL beyond rows/counts into value-aggregating spatial
  analytics

4. **Validation fit**
- PostGIS can act as an external correctness baseline
- public pathology datasets are available that can be converted into polygon
  sets

## Why RTDL should not do the broad version

RTDL should **not** take on the broadest possible interpretation now.

Bad version:

- “generic Jaccard similarity for arbitrary sets”
- “generic exact polygon-set similarity over every polygon family”

That broad form is wrong for current RTDL because:

- it leaves the spatial path
- or it silently becomes a full exact overlay/materialization program
- or it overclaims backend maturity too early

So the accepted version should be:

- **pathology polygon-set Jaccard**
- with explicit geometry and data-family boundaries

## Recommended workload decomposition

The right technical path is two-layered.

### Layer 1: `polygon_pair_overlap_area_rows`

Meaning:

- input:
  - left polygons
  - right polygons
- output:
  - one row per true overlapping pair with:
    - `left_polygon_id`
    - `right_polygon_id`
    - `intersection_area`
    - optionally `left_area`
    - optionally `right_area`
    - optionally `union_area`

This is the real missing primitive.

### Layer 2: `polygon_set_jaccard`

Meaning:

- input:
  - two polygon sets plus a grouping key such as `image_pair_id`
- output:
  - one row per image/set pair with:
    - `image_pair_id`
    - `overlap_area_total`
    - `union_area_total`
    - `jaccard_similarity`

This lets RTDL keep:

- candidate search and refine explicit
- aggregation explicit
- correctness checks explicit

## Honest implementation boundary

The first accepted implementation should be:

- pathology-style polygon Jaccard
- CPU/Python/PostGIS trustworthy first
- Linux primary platform
- exactness boundary explicit

The first accepted implementation should **not** claim:

- generic full exact polygon overlay for all polygon families
- immediate RT-core-native maturity
- equal maturity across CPU, Embree, OptiX, and Vulkan on day one

## PostGIS backing story

The PostGIS story is strong enough to justify doing this.

Reference shape:

1. load left polygons and right polygons
2. build GiST indexes on both geometry columns
3. use MBR-accelerated pair filtering
4. compute `ST_Area(ST_Intersection(...))`
5. derive union area as:
   - `area(left) + area(right) - intersection_area`
6. aggregate by image/set pair into a final Jaccard score

That gives RTDL:

- an external correctness baseline
- a practical comparison baseline
- a reproducible SQL truth path

## Public-data story

A public-data-backed implementation path also exists.

Good candidate public sources:

1. **NuInsSeg**
- large public nuclei instance-segmentation dataset
- ROI/mask assets can be converted into polygons
- strong modern public source for testing and conversion work

2. **MoNuSAC / MoNuSeg family**
- public nuclei segmentation challenge datasets
- directly aligned with pathology-segmentation workloads

These are suitable because they offer:

- real segmentation objects
- per-image grouping
- realistic pathology geometry

## Recommended next goals if this line is adopted

If RTDL accepts this line, the clean next-goal sequence is:

### Goal 137: Jaccard workload charter and semantics

Close:

- workload naming
- exact emitted schema
- pathology-only boundary
- accepted exactness story
- PostGIS reference contract

Deliverables:

- one goal doc
- one semantics report
- one SQL reference note

### Goal 138: CPU/Python/PostGIS primitive closure

Implement:

- `polygon_pair_overlap_area_rows` on:
  - Python reference
  - native CPU/oracle
  - PostGIS cross-check path

Close:

- authored minimal cases
- synthetic rectilinear cases
- one fixture-backed case

### Goal 139: Public pathology data acquisition and conversion

Build:

- public-data acquisition plan
- conversion pipeline from masks/ROIs to polygon sets
- deterministic derived cases
- one checked-in bounded public subset

Target sources:

- NuInsSeg
- one MoNuSAC/MoNuSeg-style source if license/access remains practical

### Goal 140: Aggregate Jaccard workload closure

Implement:

- `polygon_set_jaccard`

Close:

- Python reference parity
- CPU parity
- PostGIS parity
- user-facing example

### Goal 141: Linux large-scale correctness and performance audit

Run:

- Linux large deterministic rows
- PostGIS-backed correctness
- backend comparison where realistic

Honest target:

- CPU first
- Embree/OptiX/Vulkan only if the primitive maps cleanly enough to be worth it

### Goal 142: Documentation and generate-only expansion

Add:

- user guide section
- cookbook entry
- generate-only support if the workload is stable enough

## Final recommendation

RTDL may pursue this line because it is:

- genuinely spatial
- historically aligned
- technically meaningful
- externally checkable with PostGIS
- supportable with public pathology data

But the accepted project statement should be:

> RTDL may pursue **pathology polygon-set Jaccard** as a narrow spatial
> experimental line, entering through a `polygon_pair_overlap_area_rows`
> primitive and only then attempting `polygon_set_jaccard` above it.

That is the honest and technically coherent version of the goal.
