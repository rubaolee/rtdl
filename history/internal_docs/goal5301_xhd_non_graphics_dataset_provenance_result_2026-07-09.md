# Goal5301 X-HD Non-Graphics Dataset Provenance Result

Date: 2026-07-09

## Verdict

`completed_non_graphics_dataset_provenance_matrix__census_tiger_next`

## Purpose

Goal5301 consolidates the non-graphics side of the X-HD full-paper reproduction problem after the graphics Level-B line reached three public-mesh same-source comparisons.

This is intentionally not a route implementation goal. It does not run author code, RTDL code, or POD GPU work. The current blocker for BraTS / Census-TIGER / OSM is input provenance and acquisition, not execution.

## New Artifact

Created:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5301_non_graphics_dataset_provenance_matrix_2026-07-09.json
```

The matrix consolidates these prior evidence files:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_dataset_provenance_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5297_dataset_acquisition_manifest_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5295_figures7_8_10_pod_dataset_availability_2026-07-09.json
```

## Main Findings

### 1. Exact Dataset Rule Remains Strict

Exact paper-dataset status still requires actual dataset file/hash provenance or deterministic author-script regeneration with the same source snapshot and conversion parameters.

Count, point count, or Gini-statistic matching is not enough. A public reconstruction without file/hash proof remains Level-B same-source representative evidence, not Level-C exact-paper input recovery.

### 2. BraTS Is Access-Blocked

BraTS 2020 validation data is registration/license gated. Current workspace and POD assets are absent. Even after authorized access, exact paper identity would still require the author image list and conversion hashes.

Classification:

```text
family_id: brats_2020
status: registration_or_license_required
priority: medium_after_public_geo
```

### 3. Census/TIGER Is The Best Next Non-Graphics Target

The Census/TIGER-like geographic family is public-source-likely and smaller than the OSM Lakes/Parks/All Nodes path. It is therefore the highest-priority non-graphics target, but not yet ready for RTDL execution.

Before running comparisons, the project must resolve:

```text
product/year/layer
coordinate convention
WKT conversion path
full-size vs bounded fixture feasibility
exact-vs-Level-B claim boundary
```

Classification:

```text
family_id: census_tiger_geo
priority: highest_non_graphics_next
recommended next: Goal5302 Census/TIGER public-source resolution plan
```

### 4. OSM Is Public But Deferred

OSM Lakes / Parks / All Nodes are public in principle but require snapshot date, extract filters, conversion rules, and large-data handling. They should not be the immediate next target unless an accepted OSM snapshot plan exists.

Classification:

```text
family_id: osm_geospatial
priority: defer_until_census_tiger_resolved
```

### 5. Current POD Is Not The Blocker

Goal5295 already showed that `/local/storage/shared/HDDatasets` is absent on the current POD. The missing author HDDatasets root blocks author figure-matrix regeneration for figures 7/8/10. Running more POD commands cannot solve missing dataset provenance.

POD should be used again only after:

```text
exact datasets are mounted, or
a bounded public candidate dataset has been prepared and accepted
```

## Claim Boundary

Allowed summary:

```text
Non-graphics X-HD full-paper inputs remain unresolved; Census/TIGER public-source provenance is the best next target, while BraTS requires access and OSM requires snapshot/filter decisions.
```

Forbidden summaries:

```text
Full X-HD paper reproduction is complete.
Exact non-graphics datasets were recovered.
Count/Gini matching proves exact paper inputs.
Performance ratios are available before input and denominator alignment.
```

## Validation

Added:

```text
tests/goal5301_xhd_non_graphics_dataset_provenance_test.py
```

The test verifies:

- statistics are not accepted as exact dataset identity;
- BraTS / Census-TIGER / OSM priorities and blockers are explicit;
- POD is not the current blocker;
- claim boundaries reject full reproduction and ratios.

## Next Recommended Goal

`Goal5302_census_tiger_public_source_resolution_plan`

Scope:

```text
Resolve the concrete Census/TIGER product/year/layer/conversion plan for USCounty, USZipcode, USWater, and USCensus.
Do not run RTDL or author comparisons until a bounded or full public input artifact exists.
Keep any reconstructed public data at Level-B unless file/hash provenance proves exact paper identity.
```
