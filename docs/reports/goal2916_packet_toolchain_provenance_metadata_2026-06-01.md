# Goal2916: Packet Toolchain Provenance Metadata

Date: 2026-06-01
Status: implemented locally; pod packet rerun still required

## Purpose

Goal2916 addresses the compiler flag alignment caution raised by the Goal2897
RayDB review and repeated in the Goal2914 scaled-packet review. The current
v2.5 canonical packet already records source cleanliness, GPU identity, and
claim-boundary violations, but the packet summary did not make CUDA/OptiX/PTX
and partner-library provenance visible enough for a future release packet.

## Change

`scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py` now adds a
`runner_metadata.toolchain` object with:

- `cuda_home`, `optix_prefix`, `optix_header_exists`, and
  `rtdl_optix_library_exists`;
- `rtdl_optix_ptx_arch`, `rtdl_optix_ptx_compiler`, and `rtdl_nvcc`;
- `nvcc_version` and the selected C++ compiler version;
- visible partner versions for Triton, Torch, CuPy, and Numba when installed;
- NVIDIA driver/GPU topology as seen by `nvidia-smi`.

The metadata is intentionally observational. It does not make local smoke runs
fail when CUDA, OptiX, or a partner package is absent. A serious pod packet can
now be audited for the exact toolchain environment used for the timing run.

## Boundary

This is toolchain provenance, not a compiler fairness proof. It helps reviewers
see what was used, but it does not prove that Triton, CuPy, Torch, CUDA C++,
and the native OptiX build have identical optimization settings.

This is not a multivendor result. It does not address the second-architecture
or AMD/ROCm check.

This is not a v2.5 release authorization, public speedup claim, broad RT-core
claim, true-zero-copy claim, package-install claim, automatic Triton-selection
claim, or paper-reproduction claim.

## Next Step

Rerun the seven-app Goal2855 packet on the RTX pod after this commit lands.
The expected follow-up artifact should prove that the scaled v2.5 packet still
passes and now carries `runner_metadata.toolchain.metadata_version:
rtdl.goal2916.toolchain_provenance.v1`.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2855_v2_5_current_canonical_harness_packet_runner_test tests.goal2916_packet_toolchain_provenance_test

Ran 13 tests
OK
```
