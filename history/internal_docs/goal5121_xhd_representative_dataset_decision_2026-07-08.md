# Goal5121 - X-HD Representative Dataset Decision

Date: 2026-07-08

## Verdict

```text
paper_inputs_unavailable_bounded_fixtures_only
```

## Purpose

Decide whether the X-HD paper app can move beyond bounded synthetic fixtures to
same-source representative or exact paper inputs.

## Search Scope

Checked:

- author repository checkout on POD:
  `/tmp/xhd-goal5112/author`;
- author `expr/` scripts and logs;
- retained POD author build/run directory:
  `/tmp/xhd-goal5112`;
- expected external data root referenced by author logs:
  `/local/storage/shared/HDDatasets`.

## Findings

The author repository contains experiment scripts and logs, but not the paper
input datasets themselves. Logs reference external local paths such as:

```text
/local/storage/shared/HDDatasets/...
```

and dataset names including:

```text
dtl_cnty.wkt
uszipcode.wkt
USADetailedWaterBodies.wkt
USACensusBlockGroupBoundaries.wkt
lakes.bz2.wkt
parks.bz2.wkt
dragon.ply
asian_dragon.ply
thai_statuette.ply
happy_buddha.ply
BraTS MRI .nii files
```

On the current POD, the referenced data root is absent:

```text
/local/storage/shared/HDDatasets -> missing
```

The repository also contains third-party sample files, but these are not
proven paper inputs and are not a valid substitute for a same-source paper
fixture.

## Decision

No exact paper dataset and no usable same-source representative dataset is
available in the current workspace/POD evidence.

Therefore:

- Goal5122 representative correctness gate is skipped;
- X-HD closeout must remain bounded same-input only;
- exact paper dataset reproduction remains not claimed.

## Claim Boundary

Authorized:

- bounded tiny/2D/3D WKT fixtures;
- author JSON gates on those bounded fixtures;
- RTDL public column route gates on bounded 2D/3D fixtures.

Not authorized:

- exact paper dataset reproduction;
- representative same-source reproduction;
- paper figure reproduction;
- substituting third-party sample files as paper input.
