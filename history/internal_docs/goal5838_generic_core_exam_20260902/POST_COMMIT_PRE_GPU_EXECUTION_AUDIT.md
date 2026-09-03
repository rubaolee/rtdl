# Goal5838 post-commit pre-GPU execution audit

Date: 2026-09-03

Status: `READY_FOR_EXACT_COMMIT_TRUE_GPU_EXAM__PENDING_NOT_FAILURE`

## Exact checkpoint

The selected-topology implementation is committed and pushed at
`affbc8b8bd25416e6fd3be44a5b77210e2e59a03` on
`codex/cgo-goal5836-handoff`. Local `HEAD`, the remote-tracking branch, and the
working tree agreed at this audit checkpoint.

The three frozen generic-core files still have the exact preselection hashes:

| File | SHA-256 |
| --- | --- |
| `src/rtdsl/v4_family_schema.py` | `2d118697d10cb2bc2a8672700ae5a991eaf94e66834bb3e08fd898323720f224` |
| `src/rtdsl/v4_generic_family_lifecycle.py` | `7ac68832de9d1e04fdd6f0f11bfa0de7d6109d892ab22e42c9aeb2825d28228c` |
| `src/rtdsl/v4_family.py` | `d25c487823e966a8e9083092811c9a1a2b6aa0fef6ce8f3a0a5b8919c5b809e8` |

The stored core-seal verifier and independent-selection verifier both pass.
The selected candidate remains
`builtin_sphere::any_hit_count_continue_u64_per_query`; frozen-core byte
changes remain zero.

## Repeated local checks

The complete 69-test Goal5838 set passed under Python optimization level 2,
warnings-as-errors, the debug allocator, and each of these fixed hash seeds:
`0`, `1`, `2`, `3`, `7`, `11`, `97`, and `65537`. This is 552 passing test
executions with no seed-dependent result. Selected-source `compileall`, Ruff
`E,F,I,UP` with only line length excluded, `git diff --check`, the core-seal
verifier, and the selection verifier also pass. The worktree remained clean.

These are local source, contract, oracle, lifecycle-mock, and evidence-tool
checks. They are not OptiX execution.

A depth-one GitHub clone initially passed 64 tests and failed five
preregistration tests because it lacked the frozen baseline commit object
`0f5c9d4297f73e412732e5a8ab133423fe4cfd21`. Fetching that one object, without
changing `HEAD`, made all 69 tests and both stored verifiers pass while the
clone remained clean. This is now documented in the case-study procedure. It
is a repository-history prerequisite, not an implementation or scientific
failure.

## Native ancestry evidence and its exact limit

The current native provider source is byte-identical to commit
`7ec6b673b1da3dbe63ff2915e82d61f5302bf85c`. In particular:

| File | SHA-256 |
| --- | --- |
| `src/native/rtdl_optix.cpp` | `8f670db5adf2cf880921f954ea00829bc424f8cdef065ea1e03d52323947e6bc` |
| `src/native/optix/rtdl_optix_cuda_helpers.cu` | `b31f323e1ac33e7d60e0c4443e1763ac8ef31d1ad1d2ef486d10c29d95b042f2` |
| `src/native/optix/rtdl_optix_v4_callback_poc.cpp` | `75b6ecbc69c7331f3c88024e9feeb4aab40c109df1a4b802f87365709ef523b0` |
| `src/native/optix/rtdl_optix_api.cpp` | `c5398c636175bbb922900391cdce51944b0ee43635c4fe5594ebfec568a1077e` |

At that exact native-source checkpoint, a fresh full provider built on an RTX
4000 Ada and completed 30 true OptiX 8 launches with matching independent
oracles. Separately, Goal5833 executed the built-in-sphere provider ABI against
OptiX 9 on a GTX 1070. The latter GPU has no RT cores and its controlling
repository binding is a source archive rather than a valid Git commit.

Therefore the inherited evidence establishes only the following risk
reductions:

- the exact current full-provider native source has built and executed on a
  modern RTX under OptiX 8;
- the built-in-sphere provider design and ABI have executed under OptiX 9; and
- neither result validates Goal5838's newly selected U64 any-hit-count callback
  composition.

It does not establish an OptiX 9 build of the exact current commit, an RTX
execution of this selected topology, its expected counts, or a prospective
success. Those facts must come from the Goal5838 runner and independent
verifier.

## Required target and one-pass procedure

The next target must expose exactly one NVIDIA GPU and use an R570-or-newer
driver, because the prior R550 pod rejected OptiX 9 during ABI initialization.
It must provide exact OptiX SDK 9.0.0 headers, a compatible CUDA toolkit, `nm`,
`ldd`, and a supported `g++`. The run must start from a clean clone of the exact
remote commit selected for execution.

The case-study README contains the three controlling commands:

1. Build the existing full generic provider and seal source, toolchain,
   headers, GPU identity, build log, exported symbols, and DSO bytes.
2. Execute the public generic family lifecycle twice against the independent
   fixture and preserve the result outside the Git tree.
3. Run the RTDL-free verifier against the result and exact DSO, also writing
   outside the Git tree.

An environment, driver, SDK, compiler, build, or mutable extension defect is
repairable engineering and remains `PENDING`; it is not the preregistered
scientific-failure condition. A success claim remains forbidden until the
true-GPU artifact exists, all twelve expected rows match, both traversal
receipts verify, and the independent verifier passes.

## Claim boundary

This audit adds no GPU result, performance result, Paper App claim,
arbitrary-callback claim, external review, or consensus. It records that the
exact committed implementation is locally exhausted and ready for the one
remaining mandatory experimental gate.
