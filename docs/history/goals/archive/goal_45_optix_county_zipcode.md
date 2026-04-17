# Goal 45: OptiX County/Zipcode Real-Data Validation

## Purpose

Move the OptiX backend from tiny/synthetic validation into the first real
exact-source RayJoin family already exercised on Embree:

- `County ⊲⊳ Zipcode`

This goal is still bounded. It should reuse the trusted exact-source co-located
slice ladder from Goal 34 rather than jumping directly to the much larger
state-filtered packages.

## Host and runtime boundary

- Host: `192.168.1.20`
- GPU: `NVIDIA GeForce GTX 1070`
- OptiX runtime: `9.0`
- Trusted PTX compiler path on this host:
  - `RTDL_OPTIX_PTX_COMPILER=nvcc`
  - `RTDL_NVCC=/usr/bin/nvcc`

## Planned ladder

Use bounded exact-source co-located slices:

- `1x4`
- `1x5`
- `1x6`
- `1x8`
- `1x10`
- `1x12`

Each point means:

- one selected county face
- `N` overlapping zipcode faces

Selection must reuse the existing Goal 28D / Goal 34 face-overlap rule so the
slice definition stays comparable across backends.

## Workloads

- `lsi`
- `pip`

## Backend comparison

Compare:

- `rt.run_cpu(...)` as the native C/C++ oracle
- `rt.run_optix(...)` as the GPU path

For each accepted point:

- require exact-row parity for `lsi`
- require exact-row parity for `pip`
- record CPU median time
- record OptiX JIT time
- record OptiX warm median time

## Acceptance

This goal is successful if it produces:

- a reproducible bounded real-data OptiX harness
- a parity-clean exact-source County/Zipcode GPU table on `192.168.1.20`
- timing evidence for both correctness and warm-path GPU performance
- an explicit boundary stating that this is still bounded family validation, not
  whole-dataset or paper-scale OptiX reproduction
