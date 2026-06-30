# Goal4028 Partition Convergence Preview Metadata

Date: 2026-06-08

## Purpose

Goal4028 records the Goal4027 CuPy partition-summary preview in the `partition_convergence_hybrid` candidate metadata.

The front-door description now includes:

- `cupy_preview_producer_same_contract_pod_execution`
- `Goal4027`
- `cupy_partition_summary_preview_passes_same_contract_but_uses_host_pair_enumeration`

## Boundary

This does not promote the preview route. The candidate plan still returns `candidate_requires_native_implementation`, keeps `runtime_executable` false at the strategy level, and does not authorize speedup, release, broad RT-core, whole-app, or true-zero-copy wording.

