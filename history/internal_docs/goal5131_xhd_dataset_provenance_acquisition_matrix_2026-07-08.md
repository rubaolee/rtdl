# Goal5131 - X-HD Dataset Provenance And Acquisition Matrix

## Verdict

`same_source_sources_identified__exact_xhd_paper_inputs_not_available`

## Purpose

Goal5131 answers the question that blocks full X-HD reproduction:

```text
Do we have the exact paper inputs, or only public same-source candidates?
```

The output artifact is:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_dataset_provenance_matrix_2026-07-08.json
```

## Exact Dataset Rule

This goal adopts the Goal5129 review amendment as a hard rule:

Level C exact paper dataset reproduction requires file-level provenance. Any one
of the following can qualify:

- author-provided input files;
- retained hashes for converted point sets;
- byte-identical converted point sets;
- a documented author script that deterministically regenerates the same point
  sets from pinned public source files.

The following are **not sufficient** for exact reproduction:

- point count;
- dimension;
- Gini index;
- bounding box;
- dataset name;
- visually similar public source;
- a reconstructed public dataset with matching summary statistics.

Those can support Level B same-source representative reproduction, not Level C
exact paper dataset reproduction.

## Current Dataset Status

| Dataset | Exact input? | Same-source candidate? | Constraint / blocker |
| --- | --- | --- | --- |
| BraTS | no | yes | license/registration; exact image list and conversion absent |
| USCounty | no | yes | likely public Census/TIGER; exact converted files absent |
| USZipcode | no | yes | likely public Census/TIGER/ZCTA; exact converted files absent |
| USWater | no | yes | likely public geospatial source; citation/source path must be resolved |
| USCensus | no | yes | likely public Census source; exact conversion absent |
| Lakes | no | yes | OSM snapshot and extraction path unknown; very large |
| Parks | no | yes | OSM snapshot and extraction path unknown; very large |
| All Nodes | no | yes | paper says partially used; subset unknown; too large for first target |
| Dragon | no | yes | public Stanford mesh likely accessible; exact mesh/conversion hash absent |
| HappyBuddha | no | yes | public Stanford mesh likely accessible; exact mesh/conversion hash absent |
| AsianDragon | no | yes | public Stanford mesh likely accessible; larger; exact hash absent |
| ThaiStatuette | no | yes | public Stanford mesh likely accessible; larger; exact hash absent |

## Recommended First Real Gate

The first Level B gate should be:

```text
Dragon-HappyBuddha same-source representative gate
```

Reasons:

- both are graphics 3D datasets named by the paper;
- they are smaller than AsianDragon / ThaiStatuette and far smaller than
  OSMLakes / OSMParks;
- they avoid BraTS license friction;
- the author binary already supports `ply` and `off`, which is the natural route
  for Stanford graphics meshes;
- the gate can produce useful evidence without pretending to be Level C exact.

Required evidence for Goal5132:

- source URLs and downloaded file hashes;
- converted input hashes if conversion is performed;
- author `hd_exec` JSON;
- RTDL exact route JSON;
- directed input1-to-input2 comparison under the established contract;
- phase fields kept separate;
- explicit label: Level B same-source representative, not Level C exact.

## Claim Boundary

This goal does not claim:

- exact paper dataset reproduction;
- representative correctness result;
- figure reproduction;
- performance ratio;
- X-HD algorithmic route reproduction.

It only decides the dataset/provenance state.

## Consequence

The X-HD project may now proceed to Goal5132, but only under the Level B label
unless exact files/hashes are discovered. If exact files are never found, the
full paper line can still produce a high-quality representative reproduction,
but it must not call that result exact paper reproduction.
