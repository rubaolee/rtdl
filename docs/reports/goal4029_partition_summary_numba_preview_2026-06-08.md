# Goal4029 Partition Summary Numba Preview

Date: 2026-06-08

## Purpose

Goal4029 adds a Numba CUDA device-column preview for the partition-summary stream:

`build_v2_8_fixed_radius_partition_convergence_summary_numba_preview_3d(...)`.

This preview uses the Python reference to build the partition summary, then transfers the typed columns to Numba CUDA device arrays with `numba_cuda_array_interface` metadata. It is a partner-choice bridge for Numba and not the final fast native producer.

## Validation

The preview must pass the Goal4019 same-contract validator and the Goal4021 component-label oracle on deterministic small inputs. Overflow remains fail-closed.

## Boundary

This goal does not add a native ABI. It does not make `partition_convergence_hybrid` a promoted runtime route. It does not authorize public speedup wording, RT-core speedup wording, whole-app benchmark wording, release wording, or true zero-copy wording.

