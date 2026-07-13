# Goal5297 - X-HD Dataset Acquisition Manifest

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5297 turns the current X-HD data blocker into an executable acquisition and
POD-transfer plan.

The important correction is:

```text
The current POD is usable but lacks /local/storage/shared/HDDatasets.
The local workspace already has public Stanford graphics candidates for all four
graphics meshes.
Those local files can support Level-B same-source graphics diagnostics after
upload, but they still do not prove exact paper dataset identity.
```

## Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5297_dataset_acquisition_manifest_2026-07-09.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.dataset_acquisition_manifest.v1
```

## Current POD State

```text
POD = 213.173.108.24:13502
wrapper = scripts/current_pod_ssh.py
last known preflight = POD_OK
GPU = NVIDIA RTX 4000 Ada Generation
author build = /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
author dataset root = /local/storage/shared/HDDatasets
author dataset root exists = false
```

Interpretation:

```text
The POD is usable. The blocker is missing exact author HDDatasets, not SSH/GPU.
```

## Local Graphics Assets

The local workspace has public Stanford same-source candidates:

```text
Dragon full:
  path = Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip.ply
  vertices = 437645
  sha256 = FEA87FF48F2ABA22FB53E7B67C3FF3F7B8C2A3B3A0653AF62C48BBA67C6D5744

HappyBuddha full:
  path = Paper-reproduction-apps/x-hd-paper/data/external/stanford/happy_recon/happy_vrip.ply
  vertices = 543652
  sha256 = 2283371216D748A08376A3C88698E283CC8F18D10CED348D6D133051BCF217AB

AsianDragon full:
  path = Paper-reproduction-apps/x-hd-paper/data/external/stanford/asian_dragon.ply
  vertices = 3609600
  sha256 = 4A31C6B8951B0F9F4B351D183CB5D5D27E2D1A5916B27E6516ACFB9A91AD7F85

AsianDragon scaled 1e-3:
  path = Paper-reproduction-apps/x-hd-paper/data/external/stanford/asian_dragon_scaled_1e-3.ply
  vertices = 3609600
  sha256 = 4F98D1F809CFB6DCB448E469FDD94A606DE17B45CCB160F5CD1A5423508F01FE

ThaiStatuette full:
  path = Paper-reproduction-apps/x-hd-paper/data/external/stanford/thai_statuette.ply
  vertices = 4999996
  sha256 = 01470DA9FC1241DCB4B075CC057FF6BF88D8DC721CE24B5847B9EFDFBB8C0345

ThaiStatuette scaled 1e-3:
  path = Paper-reproduction-apps/x-hd-paper/data/external/stanford/thai_statuette_scaled_1e-3.ply
  vertices = 4999996
  sha256 = 047024CF12FC541634D02612F0D72EA03EF9BABB8239F4CA6A1A6A9422DA272E
```

The public Stanford source page / archives are recorded in the manifest.

## Current POD Graphics Gap

The current POD has only:

```text
/tmp/xhd_goal5234/data/dragon.ply
/tmp/xhd_goal5234/data/asian_dragon.ply
/tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply
```

It does not have:

```text
/tmp/xhd_goal5234/data/thai_statuette.ply
/tmp/xhd_goal5234/data/thai_statuette_scaled_1e-3.ply
/tmp/xhd_goal5234/data/happy_buddha.ply
```

Therefore current POD graphics coverage is partial, but unlike geo/BraTS, the
missing public Stanford graphics files are present locally and can be uploaded.

## Non-Graphics Blockers

### BraTS

```text
source = BraTS 2020
status = registration/license required
local assets = absent
POD assets = absent
exact blocker = author image list and conversion hashes absent
```

### Census/TIGER geospatial

```text
source candidate = Census/TIGER shapefiles
status = public source likely available
local assets = absent
POD assets = absent
exact blocker = source year/snapshot, conversion, and hashes absent
```

### OSM geospatial

```text
source candidate = OpenStreetMap
status = public but large snapshot required
local assets = absent
POD assets = absent
exact blocker = snapshot date, filters, conversion, and hashes absent
```

## Figure Unblock Matrix

```text
Figure 5:
  graphics can advance as Level B after POD upload;
  BraTS and geo remain blocked by acquisition/provenance.

Figure 6:
  Level-B Dragon/Asian work exists;
  exact graphics input identity and phase/counter mapping remain blockers.

Figure 7:
  exact Figure 7 remains blocked;
  after graphics upload, a Level-B graphics lb=0/lb=256 author matrix is
  possible.

Figure 8:
  exact Figure 8 remains blocked;
  after graphics upload, a Level-B graphics radius-strategy diagnostic may be
  possible.

Figure 10:
  still blocked; current data has no all_nodes.wkt substitute.
```

## Recommended Next Goal

```text
Goal5298 - Upload local public Stanford graphics assets to POD and run an
author-only Level-B graphics matrix precheck.
```

Scope:

```text
Use scripts/current_pod_ssh.py upload, not naked scp.
Upload missing HappyBuddha and ThaiStatuette public/derived files.
Run author hd_exec value prechecks for graphics pairs present in paper-branch logs.
Keep output Level-B same-source only.
Do not run RTDL comparison until author-side values are recorded.
```

## Claim Boundary

Not authorized:

```text
full paper reproduction
exact paper dataset reproduction
figure reproduction
author matrix regenerated
performance ratio
partial temporary inputs promoted to paper inputs
```

## Validation

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5297_dataset_acquisition_manifest_2026-07-09.json
py -m unittest tests.goal5297_xhd_dataset_acquisition_manifest_test
```
