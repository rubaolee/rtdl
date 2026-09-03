# Goal5838 first-pod execution and verifier repair log

Date: 2026-09-03

Status: `DIAGNOSTIC_GPU_PASS_PRESERVED__FINAL_SINGLE_COMMIT_RERUN_REQUIRED`

## Pod intake

The owner supplied only `ssh root@213.173.108.100 -p 12943`. The RTDL agent
used the established project key and owned all environment adaptation. The pod
exposed one NVIDIA RTX 2000 Ada Generation GPU with 16,380 MiB, compute
capability 8.9, driver 580.159.04, CUDA 12.8, and host
`libnvoptix.so.1`. Python 3.12.3, NumPy 2.4.4, and Numba 0.65.1 were installed
in a task-owned environment outside the repository.

## SDK negotiation

NVIDIA `optix-dev` 9.1.0 at exact commit
`f1f6dd803f3159992d248178f6e09421c6eb8b6d` compiled all four selected
Callback-IR roles through real Numba/NVVM and NVRTC, but its zero-launch
`optixInit()` probe returned 7801. This was an SDK/host ABI mismatch and was
classified only as repairable environment negotiation.

NVIDIA `optix-dev` 9.0.0 at exact commit
`fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd` passed `optixInit()`, callback
compilation, all local gates, and exact compiler-input custody. It became the
selected pod-local SDK without changing the preregistered topology or frozen
core.

## Mutable builder repair

The first exact-NVRTC builder passed the canonical versioned shared object
directly to CUDA 12.8 NVCC, which rejected the `.so.12.8.93` suffix before
compilation. An isolated `/tmp` probe established that
`-Xlinker <canonical-versioned-NVRTC-file>` produces a valid shared object and
preserves the expected dynamic dependency. Commit
`d3111ebe20d5e39c796d1d56beb08fc17b912de2` contains that mutable builder and
command-rederivation repair. It changes no frozen-core file.

## Diagnostic true-GPU result

From a clean detached checkout of `d3111ebe20d5e39c796d1d56beb08fc17b912de2`:

- preflight status was
  `PASS__GOAL5838_POD_READY_FOR_FROZEN_GPU_EXAM__NO_GPU_EXECUTION_CLAIM`;
- the provider DSO SHA-256 was
  `242aa97574c37ce969842dd3efb12906f6f6ccae1ca0df25388b1d58765f26d0`;
- the sealed build result SHA-256 was
  `3cd7152049f1d44527e222c23cf7903d50072a408849236f6e94d6064909f411`;
- two true OptiX launches matched all 12 independently prescribed U64 oracle
  rows;
- the GPU result SHA-256 was
  `feac0413bc385eb73355b9b8afcfd537986ab4602af4c38338cfbf7a50255c41`;
- the GPU artifact file SHA-256 was
  `76338049e3b350caea38e815a4fa33e1c6f4b641f1adfaf794077159f75b5c52`;
  and
- the artifact reported zero frozen-core byte changes.

All remote files were copied to the Mac before further work. Local and remote
SHA-256 inventories agree exactly.

## Verifier defects found after the diagnostic run

The independently invoked RTDL-free verifier exposed three mutable verifier
assumption defects in sequence:

1. it applied a 64-character SHA-256 validator to the 40-character Git commit
   identity;
2. it rejected the empty branch string produced by the deliberately detached
   exact-commit checkout; and
3. it expected the provider lifecycle receipt directly, while the frozen
   generic family lifecycle correctly wraps it in a generic receipt with a
   nested `provider_receipt`.

The verifier was repaired to validate a full lowercase 40-hex Git object ID,
accept a detached checkout when exact commit and clean-tree custody hold, and
independently validate both the generic outer lifecycle and provider-owned
inner lifecycle. New negative tests cover malformed Git IDs, nested execution
count drift, and detached native-build custody.

With only those verifier repairs in the local working tree, the RTDL-free
verifier fully rederived the immutable diagnostic artifact: 33 source files,
two true OptiX launches, 12 exact oracle matches, zero frozen-core changes, and
the copied native DSO bytes. The resulting diagnostic verification SHA-256 was
`7c6beb544aa981de4b8af5904cfe0c0d1a9b345782dbbfb8f674db815223e2db`.

## Final evidence rule

The diagnostic GPU artifact is preserved and must not be rewritten. It proves
that the selected path can execute, but it is not used as the final Goal5838
single-commit closure because its committed verifier contained the defects
above. The repaired verifier, tests, and this log must first be committed and
pushed. The pod must then rerun fresh preflight, native build, primary and
reverse true-OptiX executions, and RTDL-free verification from that one clean
commit into new exclusive paths.

No event in this log required or made a change to
`src/rtdsl/v4_family_schema.py`,
`src/rtdsl/v4_generic_family_lifecycle.py`, or `src/rtdsl/v4_family.py`.
Nothing here authorizes a performance, broad arbitrary-callback, Paper App,
external-review, or consensus claim.
