# Goal 47: OptiX Large Checks Matching Goal 41

## Purpose

Extend the Goal 41 large-check pattern from:

- native C/C++ oracle vs Embree

to:

- native C/C++ oracle vs OptiX

on the same Linux host and the same two larger real-data families:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`

## Host and runtime boundary

- Host: `192.168.1.20`
- GPU: `NVIDIA GeForce GTX 1070`
- OptiX runtime: `9.0`
- PTX compiler path:
  - `RTDL_OPTIX_PTX_COMPILER=nvcc`
  - `RTDL_NVCC=/usr/bin/nvcc`

## Success condition

This goal is successful if:

- both larger families complete on the GPU host
- `run_cpu(...)` and `run_optix(...)` match exactly at the row level
- timing is recorded for both workloads:
  - `lsi`
  - `pip`
- the result is documented as the OptiX extension of Goal 41 rather than a new
  paper-scale reproduction claim
