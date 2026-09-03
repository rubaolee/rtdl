# Goal5838 adaptive pod tooling hostile self-review

Date: 2026-09-03

Review class: strict internal self-review; external review owner-deferred

Verdict: `READY_TO_COMMIT_ADAPTIVE_POD_TOOLING__GPU_EXAM_STILL_REQUIRED`

Unresolved severity count: `P0=0`, `P1=0`, `P2=2`, `P3=2`

## Scope

This review covers the post-selection execution tooling correction that makes
the Goal5838 GPU exam target-profile-parametric rather than hard-coded to OptiX
9.0/R570. It covers the native builder, pod preflight, GPU runner, independent
verifier, selected-case README, and their focused tests. It does not alter or
reinterpret the preregistration, challenge selection, fixture, oracle, selected
callback topology, or the three frozen generic-core files.

## Findings repaired

### R1, P1: one desired SDK profile was incorrectly treated as scientific scope

The first clean-pod instructions and verifier required OptiX 9.0.0, and the
instructions therefore required R570 or newer. The preregistration contains no
such version constraint. This could reject a valid pod even though the same
provider source is compatible with an earlier SDK.

Repair: builder and runner now require an explicit three-component SDK string;
the build checks the selected `optix.h`; the target profile records the SDK;
and the independent verifier derives the expected native encoded version from
that recorded string. It still rejects every version mismatch among headers,
manifest, target, DSO descriptor, and execution receipt.

### R2, P1: compile-only readiness did not prove host-driver ABI compatibility

An R550 host previously compiled an OptiX 9 provider and then failed at
`optixInit()` with unsupported ABI. Repeating that pattern would waste pod time
and could be misreported as an implementation failure.

Repair: preflight compiles and runs a temporary zero-launch `optixInit()`
probe. The builder repeats the probe and seals its source hash, normalized
compile command, compiler-output hash, executable identity, return code, exact
output, and zero launch count into the build input. The RTDL-free verifier
independently rejects missing, altered, failed, or structurally inconsistent
probe records.

### R3, P2: exactly-one-GPU requirement was an unnecessary pod restriction

The first tooling queried all GPUs and rejected a multi-GPU pod. This was an
environment preference, not a semantic requirement.

Repair: generated build/run commands set `CUDA_VISIBLE_DEVICES=0`; builder and
runner require that setting and query `nvidia-smi --id=0`. The manifest and
result bind the selected UUID, driver, capability, environment selector, and
native runtime descriptor. Multi-GPU pods are therefore accepted without
weakening target identity.

### R4, P2: resolving the Python executable escaped the virtual environment

The first preflight used `Path(sys.executable).resolve()`. On macOS that
followed the virtual-environment symlink to the Homebrew base interpreter, so
child tests lost the installed NumPy/Numba packages.

Repair: commands and receipts preserve the absolute invoked executable path
without dereferencing the virtual-environment link. A negative local preflight
then ran every focused local gate successfully; its remaining failures were
only expected missing NVIDIA/Linux components and the intentionally dirty
pre-commit tree.

## Positive evidence

- The six Goal5838 test modules pass `81/81` under Python 3.12.14, Numba
  0.65.1, and NumPy 2.4.4.
- Focused syntax compilation passes.
- Ruff `E,F,I,UP` checks pass with only the repository-wide `E501` exclusion.
- `git diff --check` passes.
- Stored generic-core seal verification passes with zero changed frozen files.
- Stored independent challenge selection verification passes.
- A synthetic R550 + OptiX 8.0 profile passes the complete preflight decision
  path; no driver-major floor exists.
- A real subprocess unit test compiles through a controlled fake host compiler,
  executes the produced ABI probe, and observes exactly
  `optixInit_result=0` with zero OptiX launches.
- A verifier mutation test rejects an altered ABI-probe result.
- Every native source compiled by the Goal5838 builder is byte-identical to
  commit `7ec6b673b1da3dbe63ff2915e82d61f5302bf85c`, whose preserved evidence
  records 30/30 true OptiX 8 launches on RTX 4000 Ada/R550. This is inherited
  compatibility evidence only; it is not relabelled as Goal5838 execution.

## Residual findings

### O1, P2: exact current-commit GPU execution is absent

No NVIDIA GPU exists on this Mac. The corrected builder, selected callback,
and final artifact verifier have not yet executed together from the exact new
commit. This is the required next gate, not a scientific negative result.

### O2, P2: SDK candidates are prospective until probed on the actual pod

The documented NVIDIA `optix-dev` commits are reproducible acquisition
candidates. Their presence in the table does not claim that every candidate
runs on every driver or that every listed version has passed Goal5838. The
zero-launch probe and full build/run decide compatibility on the actual host.

### O3, P3: GPU index zero is the current deterministic selection policy

The tooling accepts multi-GPU pods but selects container ordinal zero rather
than offering arbitrary ordinal selection. This is sufficient for one-GPU
prospective evidence and prevents identity ambiguity. General multi-device
scheduling is outside Goal5838.

### O4, P3: external review remains deferred

The owner explicitly deferred external review while traveling. This document
is not Claude/Gemini review and creates no 2-AI/3-AI consensus claim. External
review remains a later CGO gate, not a substitute for the GPU exam.

## Claim boundary

This tooling correction authorizes no Goal5838 success, performance, speedup,
Paper App, arbitrary Callback-IR, universal OptiX-version portability,
external-review, or consensus wording. Goal5838 completes only after an exact
clean commit builds, executes primary and reverse order on a true OptiX GPU,
matches all 12 oracle cases, preserves the frozen core byte-for-byte, and
passes the RTDL-free artifact verifier and final hostile audit.
