# Goal3260: RayJoin Runner Explicit Query-Axis Evidence

**Date:** 2026-06-03  
**Status:** engineering evidence, not a release claim  
**Scope:** RayJoin bounded same-slice PIP count runner metadata after the Goal3256-3258 z-point tuning chain

## Purpose

Goal3256-3258 made the generic closed-shape PIP path faster by adding an opt-in z-point probe mode, fusing the closed-shape predicate into one pass, and replacing the boundary-distance square root with a squared comparison. The remaining reproducibility weakness was that the RayJoin comparison runner selected the fast mode through `RTDL_OPTIX_POINT_PRIMITIVE_QUERY_AXIS`, but the runner artifact did not record that choice.

Goal3260 fixes that by adding an explicit runner option, `--rtdl-pip-query-axis`, and by recording the selected generic query-axis mode under the RTDL PIP artifact row.

## Pod Evidence

Artifact:

- `docs/reports/goal3260_rayjoin_explicit_z_point_same_slice_pod_2026-06-03.json`

Run shape:

- Pod GPU: NVIDIA A40, driver 570.211.01
- RTDL commit: `0a1aaeb85b67bef42fce43679329b46ce4c12e82`
- Source dirty list: `[]`
- Runner mode: `--rtdl-pip-count-mode device_filtered_validated`
- Runner query axis: `--rtdl-pip-query-axis z_point`
- RayJoin process repeats: 5
- RayJoin internal warmup/repeat: 3 / 15
- RTDL warmup/repeat: 3 / 9

| Workload | RayJoin query median ms | RTDL prepared query median ms | RTDL / RayJoin | RTDL count | Contract |
| --- | ---: | ---: | ---: | ---: | --- |
| LSI | 0.234318 | 0.457812 | 1.954x | 269 | matching visible LSI count |
| PIP | 0.195058 | 0.326799 | 1.675x | 1430 | RayJoin PIP count not visible |

The PIP row now records `query_axis: "z_point"` directly in the RTDL artifact, so later reviewers no longer need to infer the optimized path from ambient environment state.

## Boundary

This evidence does **not** authorize release, public speedup wording, broad RT-core claims, true zero-copy claims, RayJoin paper reproduction claims, or `RTDL beats RayJoin` claims. It only closes the runner provenance gap for the private z-point tuning evidence.

The pod command wrote the full artifact and then a local summarizer helper failed because it treated the runner `comparisons` list as a mapping. The artifact itself is complete, source-clean, and validates through the Goal3260 test.

## Next Engineering Target

Claude's Goal3259 review accepts the Goal3256-3258 chain with boundary and identifies the remaining performance bottleneck as the per-candidate edge predicate. The next useful engineering target is a generic prepared-edge layout for closed-shape predicates, followed by a warp-cooperative predicate only if the prepared layout does not close the remaining gap.
