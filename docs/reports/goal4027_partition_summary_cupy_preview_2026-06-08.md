# Goal4027 Partition Summary CuPy Preview

Date: 2026-06-08

## Purpose

Goal4027 adds an executable CuPy preview producer:

`build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(...)`.

It computes partition IDs, occupied partition keys, partition counts, offsets, and AABB columns with CuPy device arrays. It supports two preview pair-enumeration modes:

- `host`: bounded host pair enumeration for near-partition pair rows;
- `device_bounded_offsets`: a CuPy RawKernel over occupied partitions and bounded offsets, with device pair enumeration and sorted output rows.

The device_bounded_offsets mode is a stronger preview, but this is still not the final fast native producer.

## Validation

The preview must pass the Goal4019 same-contract validator and the Goal4021 component-label oracle on deterministic small inputs. It also preserves Goal4023 overflow/complete-coverage behavior.

## Boundary

This goal does not add a native ABI. It does not make `partition_convergence_hybrid` a promoted runtime route. It does not authorize public speedup wording, RT-core speedup wording, whole-app benchmark wording, release wording, or true zero-copy wording.

The point is to make the partition-summary producer executable through a supported partner while keeping the final performance path clearly separate.
