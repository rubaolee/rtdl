# Goal 46: OptiX County/Zipcode Parity Repair

## Purpose

Close the real-data OptiX correctness gap exposed by Goal 45 on the first
exact-source RayJoin family:

- `County ⊲⊳ Zipcode`

Goal 45 proved the OptiX backend could run the bounded ladder on the GPU host,
but exact-row parity still failed on:

- `1x4`
- `1x5`
- `1x6`
- `1x12`

This goal restores exact-row parity across the full bounded ladder before any
broader real-data GPU expansion.

## Host and runtime boundary

- Host: `192.168.1.20`
- GPU: `NVIDIA GeForce GTX 1070`
- OptiX runtime: `9.0`
- PTX compiler path:
  - `RTDL_OPTIX_PTX_COMPILER=nvcc`
  - `RTDL_NVCC=/usr/bin/nvcc`

## Diagnosis target

Reproduce and explain the Goal 45 failures:

- `1x4`, `1x5`, `1x6`
  - `lsi` false positives
  - one `pip` containment mismatch
- `1x12`
  - one missing `lsi` row

## Repair strategy

Restore correctness conservatively:

- widen segment AABB padding slightly for the `lsi` trace path
- widen `lsi` ray `tmax` slightly
- treat OptiX `lsi` traversal as a candidate generator and apply exact native
  host-side segment intersection refine before emitting rows
- apply exact native host-side point-in-polygon recomputation before finalizing
  `pip` row values

This goal prioritizes trustworthiness over preserving the prior GPU-only refine
path.

## Acceptance

This goal is successful if:

- the full bounded County/Zipcode ladder is exact-row parity-clean:
  - `1x4`
  - `1x5`
  - `1x6`
  - `1x8`
  - `1x10`
  - `1x12`
- the result is rerun and verified on `192.168.1.20`
- the report explicitly states the new implementation boundary and its
  performance meaning
