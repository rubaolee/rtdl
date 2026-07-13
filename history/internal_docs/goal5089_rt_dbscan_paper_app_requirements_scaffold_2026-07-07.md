# Goal5089 RT-DBSCAN Paper-App Requirements Scaffold

Date: 2026-07-07

## Verdict Label

```text
completed_rt_dbscan_paper_app_requirements_scaffold
```

## Purpose

Goal5089 creates the third paper-app scaffold selected by Goal5088:

```text
Paper-reproduction-apps/rt-dbscan-paper/
```

The goal is to establish a paper-app boundary and requirements surface, not to
claim reproduction.

## Implementation

Added:

```text
Paper-reproduction-apps/rt-dbscan-paper/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
Paper-reproduction-apps/rt-dbscan-paper/results/README.md
Paper-reproduction-apps/rt-dbscan-paper/scripts/README.md
```

Updated:

```text
Paper-reproduction-apps/README.md
```

## Paper Metadata

The scaffold uses metadata already present in the existing RTDL benchmark app:

```text
Title: RT-DBSCAN: Accelerating DBSCAN using Ray Tracing Hardware
Venue: IPDPS 2023
Authors: Vani Nagarajan, Milind Kulkarni
DOI: 10.1109/IPDPS54959.2023.00100
```

The scaffold does not yet pin the author artifact repository, commit, or exact
paper inputs.

## RTDL System Surface

The scaffold identifies this expected RTDL surface:

```text
fixed_radius_neighbors
prepare_generic_fixed_radius_count_threshold_2d
run_generic_fixed_radius_count_threshold_2d
run_generic_prepared_fixed_radius_threshold_reached_count_2d
prepare_optix_fixed_radius_count_threshold_2d
prepare_optix_fixed_radius_count_threshold_3d
fixed_radius_count_threshold_2d_partner_columns
fixed_radius_count_threshold_3d_partner_columns
```

It also records that v2.8 fixed-radius graph/component continuation assets may
be relevant but must be audited before use as paper-app evidence.

## App-Owned Semantics

The scaffold marks these as app-owned:

- DBSCAN epsilon and min-points policy,
- paper workload selection,
- cluster expansion and label interpretation,
- component-signature comparator,
- route-choice policy,
- performance-regime selection.

These are not promoted to RTDL core by this goal.

## Current Reproduction Status

```text
not_started
```

Recommended first bounded target:

```text
prepared fixed-radius core-flag / core-count subpath
```

Optional follow-up after requirements review:

```text
bounded component-signature continuation
```

## Verification

The manifest is valid JSON:

```text
py -m json.tool Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
```

The public paper-app surface scan across:

```text
Paper-reproduction-apps/README.md
Paper-reproduction-apps/PAPER_APP_TEMPLATE.md
Paper-reproduction-apps/paper_app_manifest.schema.json
Paper-reproduction-apps/rt-dbscan-paper/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
Paper-reproduction-apps/rt-dbscan-paper/results/README.md
Paper-reproduction-apps/rt-dbscan-paper/scripts/README.md
```

for:

```text
Goal[0-9]+
call_for_review
Antigravity
Claude
Gemini
review debt
verdict
```

returned:

```text
0 matches
```

## Claim Boundary

This goal does not claim:

- RT-DBSCAN paper reproduction,
- exact paper input reproduction,
- author-performance parity,
- whole-program speedup,
- DBSCAN-native engine ABI,
- automatic route selection,
- arbitrary clustering acceleration.

## Next Recommended Goal

Goal5090 should audit RT-DBSCAN requirements:

1. locate or declare missing the author artifact,
2. locate or declare missing exact paper inputs,
3. choose the first bounded target,
4. choose the comparator,
5. classify which existing benchmark assets are reusable,
6. write the first executable paper-app gate only after those decisions.
