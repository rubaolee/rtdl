# Goal2020 CuPy Extent Device AABB Payload Perf

Date: 2026-05-14

Status: implementation slice with pod timing

## Purpose

Goal1969 made the polygon overlap and Jaccard control rows useful again by
moving candidate discovery to a compact CuPy extent path. That still left one
avoidable cost in the v2 path: the CuPy backend computed candidate pairs on the
GPU, copied them back to Python as an ID `set`, rebuilt index arrays on the
host, and then uploaded those arrays again for the generic AABB pair summary.

Goal2020 keeps the same generic RTDL boundary and removes that round trip for
the `cupy_extent` + `cupy` path. The extent candidate indices and box columns
now stay as CuPy arrays and are passed directly into
`aabb_pair_overlap_summary_2d_partner_columns`.

## What Changed

- Added a device-resident `cupy_extent` payload builder for the control polygon
  rows.
- Preserved the older host `set` path for `cpu_fallback`, `embree`, `optix`,
  and compatibility tests.
- Kept the continuation on the generic `generic_aabb_pair_overlap_summary_2d`
  partner contract.
- Did not add polygon, Jaccard, or app semantics to the native RTDL engine.

## Pod Evidence

Pod:

- Host: `69.30.85.251`
- SSH port: `22085`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Checkout: `/root/rtdl_goal2000`
- Source label in artifacts: `local_goal2020_device_aabb_payload`

Artifacts:

- `docs/reports/goal2020_pod_cupy_extent_device_aabb_payload_2048.json`
- `docs/reports/goal2020_pod_cupy_extent_device_aabb_payload_4096.json`
- `docs/reports/goal2020_pod_cupy_extent_device_aabb_payload_8192.json`

| App | Copies | v1.8 median s | v2 median s | v2/v1.8 | Correct |
| --- | ---: | ---: | ---: | ---: | --- |
| `polygon_pair_overlap_area_rows` | 2048 | 0.312494 | 0.047627 | 0.152x | yes |
| `polygon_set_jaccard` | 2048 | 0.228634 | 0.043597 | 0.191x | yes |
| `polygon_pair_overlap_area_rows` | 4096 | 0.581360 | 0.117988 | 0.203x | yes |
| `polygon_set_jaccard` | 4096 | 0.483057 | 0.091977 | 0.190x | yes |
| `polygon_pair_overlap_area_rows` | 8192 | 1.167572 | 0.249963 | 0.214x | yes |
| `polygon_set_jaccard` | 8192 | 0.797587 | 0.160240 | 0.201x | yes |

Compared with Goal1969 at the 2048 scale:

| App | Goal1969 v2/v1.8 | Goal2020 v2/v1.8 |
| --- | ---: | ---: |
| `polygon_pair_overlap_area_rows` | 0.292x | 0.152x |
| `polygon_set_jaccard` | 0.281x | 0.191x |

## Interpretation

This is a real v2.0 perf improvement for the bounded polygon control rows. The
main win is not a new geometric kernel; it is keeping the reusable candidate
payload in the partner's device memory instead of routing it through Python
objects between two GPU steps.

The result is still bounded:

- This is the authored axis-aligned extent control contract, not arbitrary
  polygon overlay; in short, it is not arbitrary polygon overlay evidence.
- This is a Python+CuPy+RTDL v2 app version under the user-approved fairness
  rule; it is not an absolutely fair comparison against a hypothetical v1.8 app
  that also writes C/C++ or RawKernel continuation code.
- This is not an OptiX RT-core polygon candidate-discovery claim.
- v2.0 release authorization still depends on the final release audit and
  required external consensus.
