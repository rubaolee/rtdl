# Call For Review - Goal5297 X-HD Dataset Acquisition Manifest

Date: 2026-07-09

Please strictly review Goal5297.

## Review Scope

Goal5297 consolidates the current X-HD dataset acquisition state after
Goals5292-5296.

It asks whether the project has correctly identified:

```text
1. exact HDDatasets remain missing on the current POD;
2. local public Stanford graphics candidates are complete enough for a Level-B
   POD transfer/run;
3. non-graphics families remain blocked by license/snapshot/conversion
   provenance;
4. the next actionable step should be a Level-B graphics author matrix precheck,
   not a full-paper or exact-dataset claim.
```

## Files Under Review

```text
history/internal_docs/goal5297_xhd_dataset_acquisition_manifest_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5297_dataset_acquisition_manifest_2026-07-09.json
tests/goal5297_xhd_dataset_acquisition_manifest_test.py
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford/README.md
Paper-reproduction-apps/x-hd-paper/results/xhd_stanford_graphics_acquisition_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_dataset_provenance_matrix_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5295_figures7_8_10_pod_dataset_availability_2026-07-09.json
```

## Evidence Summary

Current POD:

```text
POD wrapper preflight = POD_OK
author hd_exec exists
/local/storage/shared/HDDatasets = missing
```

Local public Stanford graphics candidates:

```text
Dragon full:
  vertices = 437645
  sha256 = FEA87FF48F2ABA22FB53E7B67C3FF3F7B8C2A3B3A0653AF62C48BBA67C6D5744

HappyBuddha full:
  vertices = 543652
  sha256 = 2283371216D748A08376A3C88698E283CC8F18D10CED348D6D133051BCF217AB

AsianDragon full:
  vertices = 3609600
  sha256 = 4A31C6B8951B0F9F4B351D183CB5D5D27E2D1A5916B27E6516ACFB9A91AD7F85

AsianDragon scaled 1e-3:
  vertices = 3609600
  sha256 = 4F98D1F809CFB6DCB448E469FDD94A606DE17B45CCB160F5CD1A5423508F01FE

ThaiStatuette full:
  vertices = 4999996
  sha256 = 01470DA9FC1241DCB4B075CC057FF6BF88D8DC721CE24B5847B9EFDFBB8C0345

ThaiStatuette scaled 1e-3:
  vertices = 4999996
  sha256 = 047024CF12FC541634D02612F0D72EA03EF9BABB8239F4CA6A1A6A9422DA272E
```

Current POD only has partial graphics:

```text
present:
  /tmp/xhd_goal5234/data/dragon.ply
  /tmp/xhd_goal5234/data/asian_dragon.ply
  /tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply

missing:
  /tmp/xhd_goal5234/data/happy_buddha.ply
  /tmp/xhd_goal5234/data/thai_statuette.ply
  /tmp/xhd_goal5234/data/thai_statuette_scaled_1e-3.ply
```

Non-graphics:

```text
BraTS: registration/license and exact author image-list/conversion hashes absent.
Census/TIGER: public candidate, but year/snapshot/conversion/hash absent.
OSM: public but large; snapshot/filter/conversion/hash absent.
```

Interpretation under review:

```text
The local graphics data make a Level-B graphics POD transfer/run feasible, but
they do not solve exact paper dataset identity. The next actionable goal should
upload public Stanford graphics assets and run author-only Level-B prechecks
before any RTDL comparison or figure claim.
```

## Review Questions

1. Does the manifest correctly preserve the exact dataset rule that public
   same-source assets are not exact paper inputs without file/hash provenance?
2. Does the evidence correctly show that the current POD is usable but lacks
   `/local/storage/shared/HDDatasets`?
3. Does the local Stanford graphics inventory look sufficient for a Level-B
   graphics transfer/run?
4. Is it correct that this local graphics inventory still does not prove exact
   paper dataset identity?
5. Are BraTS, Census/TIGER, and OSM blockers correctly classified?
6. Is the Figure unblock matrix accurate: graphics can advance as Level B,
   while exact Figure 7/8/10 and non-graphics remain blocked?
7. Is the recommended Goal5298 correct: upload local public Stanford graphics
   assets to POD and run author-only Level-B graphics prechecks before RTDL
   comparison?
8. Does the result avoid full reproduction, exact dataset, figure reproduction,
   author matrix, and performance-ratio overclaims?
9. Can Goal5297 be marked externally reviewed and approved, or are amendments
   required?

## Expected Answer Shape

Please answer with:

```text
verdict_label: ...
blocking_findings:
required_amendments:
non_blocking_notes:
answers:
  Q1: ...
  Q2: ...
  ...
  Q9: ...
recommended_next_action:
```

Possible verdict labels:

```text
approve_goal5297_dataset_acquisition_manifest__graphics_level_b_transfer_possible_exact_hddatasets_missing
revise_goal5297_dataset_inventory_or_claim_boundary
block_goal5297_due_to_incorrect_dataset_or_pod_evidence
```
