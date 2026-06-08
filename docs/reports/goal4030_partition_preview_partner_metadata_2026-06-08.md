# Goal4030 Partition Preview Partner Metadata

Date: 2026-06-08

## Purpose

Goal4030 updates the `partition_convergence_hybrid` candidate metadata after both partner previews passed on the pod:

- Goal4027: CuPy partition-summary preview, later strengthened by Goal4032 with device-bounded pair enumeration;
- Goal4029: Numba CUDA device-column preview.

The candidate guidance now says:

`cupy_device_bounded_pair_preview_and_numba_device_column_preview_pass_same_contract_but_are_not_final_fast_native_producers`.

## Boundary

These previews are useful partner-choice bridges, not final fast native producers. This goal does not promote partition_convergence_hybrid. It does not add a native ABI, authorize public speedup wording, authorize broad RT-core wording, authorize whole-app benchmark wording, authorize release wording, or authorize true-zero-copy wording.
