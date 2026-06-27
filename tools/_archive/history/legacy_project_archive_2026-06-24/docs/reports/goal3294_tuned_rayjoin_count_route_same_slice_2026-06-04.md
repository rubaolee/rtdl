# Goal3294 Tuned RayJoin Count Route Same-Slice Evidence

Date: 2026-06-04

Status: complete with RTX A5000 pod evidence; still an optimization gap.

## Purpose

Goal3293 removed the old external-CDB loader and segment-packing bottleneck.
After that fix, the same-slice comparison showed the remaining gap was in the
query/count route itself:

- LSI: RTDL prepared query 0.362 ms versus RayJoin query 0.233 ms, or 1.55x.
- PIP: RTDL prepared query 0.666 ms versus RayJoin query 0.221 ms, or 3.01x.

Goal3294 does not add a native ABI or app-specific engine path. It makes the
same-slice runner able to measure two existing generic RTDL route choices
explicitly:

- LSI `left_id_dense_count`: existing generic segment-pair left-id count
  device-column primitive.
- PIP `device_filtered_validated + inclusive + z_point + scalar_count_pipeline`:
  existing generic closed-shape membership count path, validated against the
  exact prepared count before timing the selected device-side lane.

## Implementation

- Added `--rtdl-lsi-count-route exact|left_id_dense_count` to
  `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`.
- Added `--rtdl-pip-scalar-count-pipeline` to scope
  `RTDL_OPTIX_POINT_PRIMITIVE_USE_SCALAR_COUNT_PIPELINE` around RTDL PIP calls.
- Kept `--rtdl-pip-query-axis z_point` and
  `--rtdl-pip-boundary-mode inclusive` as explicit artifact-visible generic
  knobs.
- Preserved default runner behavior: exact LSI and exact PIP remain the default
  unless the tuned flags are supplied.

No native ABI changed. The native engine still sees generic segment-pair and
point/closed-shape membership primitives; RayJoin interpretation stays in the
benchmark runner and example layer.

## Pod Evidence

Artifact:

- `docs/reports/goal3294_rayjoin_same_slice_tuned_current_pod_2026-06-04.json`

Pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- RTDL commit: `60009b58d8ad7616be7c666d664443da8cdd2cb2`
- Status: `pass_with_optimization_gap`

Inputs:

- LSI: `br_county_start256_count512.cdb + br_soil_start256_count512.cdb`
- PIP: `br_county_start0_count512.cdb`

Median same-slice query/count timings:

| workload | RTDL route | RayJoin query median | RTDL prepared query median | RTDL / RayJoin | count contract |
| --- | --- | ---: | ---: | ---: | --- |
| LSI | `left_id_dense_count` | 0.236 ms | 0.333 ms | 1.41x | matching visible count, 269 |
| PIP | `device_filtered_validated`, `inclusive`, `z_point`, scalar count pipeline on | 0.225 ms | 0.361 ms | 1.61x | RayJoin PIP positive assignment count not exposed |

Comparison to the immediate Goal3293 same-slice packet:

| workload | Goal3293 RTDL / RayJoin | Goal3294 RTDL / RayJoin | improvement |
| --- | ---: | ---: | ---: |
| LSI | 1.55x | 1.41x | 1.10x closer |
| PIP | 3.01x | 1.61x | 1.88x closer |

## Interpretation

The existing generic route choices help, especially for PIP:

- LSI moves to a route that counts by left id on device without requiring
  pair-row materialization.
- PIP moves from exact host-refined candidate output to a validated device-side
  count lane; `z_point` reduces traversal work while preserving the inclusive
  exact count on this dataset.

The remaining gap is now narrower and more specific:

- LSI still trails RayJoin query timing by about 41 percent on this small slice.
- PIP still trails RayJoin query timing by about 61 percent, even after removing
  candidate write/download/refine from the timed lane.
- RayJoin's unpatched PIP binary does not expose its positive assignment count,
  so PIP remains timing-plus-RTDL-self-count evidence, not a full cross-system
  count contract.

## Boundary

This packet does not authorize:

- release
- public speedup claims
- RayJoin paper reproduction claims
- RT-core speedup claims
- RTDL-beats-RayJoin claims
- true-zero-copy claims

The next real performance target is not another app-specific trick. It is a
generic prepared closed-shape count route with resident point columns and less
per-call upload/launch overhead, plus continued segment-pair count tuning.
