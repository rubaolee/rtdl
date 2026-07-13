# Goal5317 - X-HD Figure-5 Exact-Input Acquisition Gap Matrix

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5317 converts the remaining X-HD Figure-5 blocker from vague
"exact inputs missing" language into a row-level acquisition matrix.

It does not implement a new route, run POD, or claim Figure 5 reproduction.
It answers:

```text
For every Figure-5-relevant input family, what exact provenance is missing,
what Level-B evidence already exists, and which next action is highest leverage?
```

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5317.figure5_exact_input_acquisition_gap_matrix.v1
```

## Inputs Used

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5267_full_paper_coverage_gap_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5297_dataset_acquisition_manifest_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5316_figure5_level_b_status_matrix.json
```

## Exact Dataset Rule

Goal5317 restates the project rule:

```text
Level C exact paper input status requires one of:
  - author-provided input files or archives;
  - author-provided hashes for converted point files;
  - byte-identical regenerated point files from a documented author conversion
    pipeline;
  - external review accepting deterministic public-source regeneration as
    equivalent.
```

Not sufficient:

```text
matching point counts;
matching MBRs;
matching Gini / aggregate statistics;
matching HDResult alone;
matching author rerun on public same-source candidates;
paper-log path names without bytes or hashes.
```

## Rows

The matrix has five acquisition rows:

```text
brats2020_validation
graphics_stanford
geo_county_zcta
geo_waterbodies_blockgroups
geo_osm_lakes_parks_allnodes
```

## Key Findings

### 1. BraTS Is Access / Conversion Blocked

Paper logs cover:

```text
500 unique BraTS validation pairs
2500 Figure-5-like timing records
```

But the exact image files, exact author image list/order, and NIfTI-to-point-set
conversion provenance remain absent.

Goal5317 does not recommend BraTS as the immediate technical route target
because the first blocker is access and conversion provenance, not RTDL code.

### 2. Stanford Graphics Is Strong Level-B But Not Exact

Current graphics state:

```text
value-matched Level-B pairs:
  dragon.ply -> happy_buddha.ply
  thai_statuette_scaled_1e-3.ply -> happy_buddha.ply
  thai_statuette_scaled_1e-3.ply -> asian_dragon_scaled_1e-3.ply

no-go current mapping:
  dragon.ply -> asian_dragon_scaled_1e-3.ply
```

Missing for exact:

```text
author input file hashes or bytes;
proof that author used the same Stanford public archives and local transforms;
proof for scaling / translation conventions used by paper-log basenames;
paper-branch conversion or preprocessing script.
```

### 3. County -> ZCTA Is Blocked By County Point Count

Goal5309 full-public probe:

```text
County paper point count    = 9,438,045
County observed point count = 12,477,179
delta                       = +3,039,134 (+32.2009%)

ZCTA paper point count      = 43,952,878
ZCTA observed point count   = 43,984,131
delta                       = +31,253 (+0.0711%)
```

This row should not receive a full-public author/RTDL route until an alternate
County source, simplification, precision, or conversion rule is found.

### 4. WaterBodies -> BlockGroups Is The Best Geo Exact-Provenance Target

Goal5309 / 5313 / 5314 evidence:

```text
WaterBodies paper point count    = 22,818,694
WaterBodies observed point count = 22,824,823
delta                            = +6,129 (+0.0269%)

BlockGroups paper point count    = 52,271,340
BlockGroups observed point count = 52,271,467
delta                            = +127 (+0.000243%)

author paper-config n_points_cell=8 HDResult = 0.8964367508888245
RTDL exact-witness float64 HDResult           = 0.8964380566690101
same witness float32                          = 0.8964367508888245
```

This is the closest current geo candidate, but it still lacks exact author WKT
file/hash provenance or proof that the current ArcGIS service snapshots are
the exact author inputs.

### 5. OSM-Derived Workloads Are Snapshot / Filter Blocked

The large OSM-derived Lakes / Parks / AllNodes family remains blocked on:

```text
OSM snapshot date;
extract/filter rules;
conversion rules;
author files or hashes;
feasible large-input execution plan.
```

It is not the immediate next target unless author snapshots or converted files
appear.

## Ranked Next Actions

Goal5317 ranks the next work as:

1. **WaterBodies/BG exact-provenance search**
2. Stanford graphics preprocessing / hash search
3. County source / conversion investigation
4. BraTS access + conversion provenance
5. OSM snapshot / filter provenance

Recommended next goal:

```text
Goal5318 - WaterBodies/BG exact-provenance search before any new performance work
```

Goal5318 should search:

```text
author repository;
paper branch;
generated manifests;
result logs;
available ArcGIS service metadata;
local generated WKT metadata;
```

and should not rerun author/RTDL unless a concrete provenance lead appears.

Exit labels:

```text
water_bg_exact_provenance_found
water_bg_exact_provenance_not_found_keep_level_b
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json
py -m unittest tests.goal5317_xhd_figure5_exact_input_gap_matrix_test
py -m unittest tests.goal5316_xhd_figure5_level_b_status_matrix_test tests.goal5317_xhd_figure5_exact_input_gap_matrix_test
```

Observed:

```text
Ran 16 tests in 0.008s
OK
```

The local Python launcher printed:

```text
Could not find platform independent libraries <prefix>
```

This is known Windows environment noise and did not affect test success.

## Claim Boundary

Allowed:

```text
Goal5317 is a dataset acquisition and exact-input gap matrix.
It ranks WaterBodies/BG provenance as the next highest-leverage exact-input
search target.
```

Forbidden:

```text
Figure 5 reproduction complete;
exact paper dataset reproduction complete;
full paper reproduction complete;
author-vs-RTDL performance ratio;
claiming Level-B public candidates are exact paper inputs;
claiming new RTDL route progress from Goal5317.
```

## POD Use

Goal5317 did not use POD.

POD is not expected for the recommended Goal5318 unless the provenance search
finds a concrete lead that requires author `hd_exec` or RTDL reruns.
