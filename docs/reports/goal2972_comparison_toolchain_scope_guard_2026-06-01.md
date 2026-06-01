# Goal2972: Comparison Toolchain Scope Guard

Date: 2026-06-01
Status: implemented locally; current packet rerun still required

## Purpose

The current v2.5 packet already records source cleanliness, GPU identity, CUDA,
OptiX, compiler, and partner-library versions. External reviews still treated
compiler flag alignment as a release-watch item because provenance alone did not
make the comparison scope explicit enough.

Goal2972 adds a machine-readable comparison-toolchain scope guard to the
canonical packet runner. The guard clarifies what a packet proves and, just as
importantly, what it does not prove.

## Change

`scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py` now emits
`runner_metadata.toolchain.comparison_toolchain_scope` with:

- `scope_version: rtdl.goal2972.comparison_toolchain_scope.v1`;
- required comparison shape: same source commit, same GPU, same packet runner;
- native OptiX stack observations: nvcc/PTX compiler, PTX arch, OptiX header,
  and `librtdl_optix.so` reachability;
- partner-version observations for Triton, Torch, CuPy, and Numba;
- a boolean `observed_stack_complete_for_current_packet`;
- explicit non-equivalence notes for nvcc/PTX, Triton/LLVM JIT, CuPy/NVRTC or
  library paths, Torch/ATen paths, and Numba CUDA JIT paths;
- false authorization flags for cross-compiler fairness, public speedup wording,
  paper reproduction, and release.

## What This Solves

This does not prove that all compared programs were compiled with identical
optimization flags. It does make the comparison boundary auditable in every
future packet:

- reviewers no longer have to infer whether the native and partner stacks were
  visible;
- packet tests can fail if a current packet silently loses the scope guard;
- public-claim wording remains blocked even when the observed stack is complete;
- the v2.5 evidence story can say "same commit/GPU/runner with visible stacks"
  instead of vaguely saying "toolchain provenance recorded."

## Boundary

This is not a compiler fairness proof. It is a comparison-scope guard.

This is not a second-architecture or multivendor result.

This is not a v2.5 release authorization, public speedup claim, broad RT-core
claim, whole-app speedup claim, true-zero-copy claim, package-install claim,
automatic Triton-selection claim, or paper-reproduction claim.

## Next Step

Rerun the seven-app packet on the RTX pod and refresh the 10-app triage. The
follow-up packet should show
`comparison_toolchain_scope.scope_version:
rtdl.goal2972.comparison_toolchain_scope.v1` and
`compiler_flag_alignment_proven: false`.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2972_comparison_toolchain_scope_guard_test

Ran 3 tests
OK
```
