# Goal 43: OptiX GPU Validation Ladder

## Purpose

Validate the imported OptiX backend on the first available NVIDIA host,
`192.168.1.20`, after the initial bring-up slice succeeded on tiny `lsi` and
`pip` workloads.

This goal is intentionally correctness-first. It does not claim performance
readiness and does not attempt large inputs. The objective is to establish:

- which RTDL workloads execute on the GTX 1070 host through `run_optix(...)`
- which workloads match the C oracle on small representative cases
- what the first concrete correctness or lifecycle gaps are before broader
  OptiX development

## Host and runtime boundary

- Host: `192.168.1.20`
- GPU: `NVIDIA GeForce GTX 1070`
- Driver: `580.126.09`
- Effective OptiX runtime: `9.0`
- Effective SDK headers for bring-up: `v9.0.0`

Current known-good OptiX execution path on this host:

- `OPTIX_PREFIX=/home/lestat/vendor/optix-dev`
- `CUDA_PREFIX=/usr`
- `NVCC=/usr/bin/nvcc`
- `RTDL_OPTIX_PTX_COMPILER=nvcc`
- `RTDL_NVCC=/usr/bin/nvcc`

The default NVRTC-based PTX path is not yet considered reliable on this host.

## Validation ladder

Use the following targets through a single harness:

- authored `lsi`
- authored `pip`
- authored `overlay`
- authored `ray_tri_hitcount`
- authored `segment_polygon_hitcount`
- authored `point_nearest_segment`
- derived `lsi` (`br_county_subset_segments_tiled_x8`)
- derived `pip` (`br_county_subset_polygons_tiled_x8`)

For all targets:

- compare `run_cpu(...)` vs `run_optix(...)`
- record row counts, parity, and wall time

## Acceptance

This goal is successful if it produces:

- a reproducible remote GPU validation harness
- a recorded parity table for the target ladder
- an explicit classification of:
  - parity-clean workloads
  - parity-failing workloads
  - any runtime-lifecycle problems observed after successful execution

It does **not** require all workloads to pass. Honest boundary documentation is
acceptable and expected.
