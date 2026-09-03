# Goal5838 unknown-pod readiness hostile self-review

Date: 2026-09-03

Review class: strict internal self-review; external review owner-deferred

Verdict: `READY_FOR_UNKNOWN_NVIDIA_POD_INTAKE__GPU_EXAM_STILL_REQUIRED`

Unresolved severity count: `P0=0`, `P1=0`, `P2=2`, `P3=1`

## Reviewed scope

This review covers the responsibility correction and local engineering needed
to accept an unknown NVIDIA pod without asking the owner to provision a driver
or SDK profile. It reviews the Goal5838 preflight, generated command plan,
selected Callback-IR compiler path, current case-study instructions, unknown-
pod completion plan, and source inventories consumed by the GPU runner and
RTDL-free verifier.

It does not alter or reinterpret the preregistration, challenge table,
independent selection, fixture, exact-rational oracle, selected topology, or
the three frozen generic-core files.

## Findings repaired

### R1, P1: pod software selection was incorrectly delegated to the owner

The earlier pre-GPU audit described R570 or newer plus OptiX 9 as a target
requirement. That profile was never preregistered. Requiring the owner to find
such a pod conflated one failed OptiX 9/R550 ABI pairing with a scientific or
hardware requirement.

Repair: `UNKNOWN_POD_COMPLETION_PLAN.md` now makes the input contract explicit:
the owner supplies only a reachable SSH endpoint. Driver, CUDA, OptiX, Python,
compiler, path, and multi-GPU adaptation belong to the RTDL agent. Exact SDK
candidates are negotiated by a zero-launch `optixInit()` probe, with no driver
major floor.

### R2, P1: the preflight could authorize a build without compiling the selected callbacks

The prior preflight checked CUDA/NVRTC file presence, the host-driver OptiX ABI,
local tests, and repository custody. It did not actually compile the selected
`make_ray`, `any_hit`, `miss`, and `finalize` leaves through Numba/NVVM, compile
the wrapper through NVRTC, compose PTX, or traverse the generic family public
materialization front door. A pod could therefore pass readiness and fail
immediately during the expensive execution stage.

Repair: preflight schema v2 resolves and hashes exact NVRTC, NVVM, and libdevice
inputs, clears ambient compiler/cache overrides, and launches a fresh child
under an explicit CUDA environment. The child materializes the independently
selected route through the generic family front door using a deterministic
never-loaded native identity file. It must produce a complete family
executable identity while remaining before `prepare`, native DSO loading, and
all GPU/OptiX launches.

### R3, P1: the passing command plan did not preserve the tested compiler environment

The earlier build/run commands carried only `CUDA_VISIBLE_DEVICES` and
`PYTHONPATH`. Even if an interactive preflight found the correct libraries,
the actual run could silently use a different NVVM, libdevice, NVRTC, CUDA
prefix, loader path, or formal-leaf cache.

Repair: the generated build and run argv now carry the same exact
`NUMBA_CUDA_NVVM`, `NUMBA_CUDA_LIBDEVICE`, `CUDA_HOME`, `CUDA_PATH`, CUDA/OptiX
prefix, `PATH`, `LD_LIBRARY_PATH`, GPU selector, and source-tree Python path
that passed callback compilation. Ambient simulator, compiler override,
native-library, preload, and formal cache variables are removed before the
compiler child starts.

### R4, P1: compiler identity was not closed across probe, build, and execution

The preflight hashed one NVRTC input, but the target compiler loaded NVRTC by
soname and the provider DSO linked with `-lnvrtc`. A passing probe therefore did
not prove that native build and selected callback materialization used the same
bytes. The command plan also inherited ambient variables unless the caller had
already removed them.

Repair: the target compiler now loads `RTDL_V4_NVRTC_LIBRARY` by exact canonical
path. The native builder links that exact file, records its bytes and SHA-256,
and rejects an `ldd` resolution to any other file. Generated commands use
explicit `env -u` guards. The GPU runner rejects compiler-path, prefix,
simulator, cache, or native-library contamination; hashes exact NVRTC, NVVM,
and libdevice files before materialization; rechecks them after both launches;
and stores a sealed compiler-environment identity. The RTDL-free verifier
independently rederives the schema and binds the NVRTC row back to the native
build manifest.

### R5, P1: NVCC rejected the canonical versioned NVRTC pathname

The first exact-identity builder passed
`libnvrtc.so.12.8.93` directly as an `nvcc` input. CUDA 12.8 rejected the
versioned shared-object suffix before compilation, even though the exact file
was valid and loadable.

Repair: an isolated Pod probe established that `-Xlinker <exact-file>` produces
a valid shared object and preserves the expected dynamic dependency. The
builder and RTDL-free command rederivation now require that exact argument
pair; tests reject any regression to `-lnvrtc` or an unqualified soname. This
was mutable build-driver repair and did not touch the frozen generic core.

### R6, P1: legal compute capabilities with minor zero were rejected

The first implementation of the internal compiler request required both
compute-capability components to be positive. That incorrectly rejected legal
profiles such as 9.0 and violated the unknown-pod objective.

Repair: the major component must be positive, while the minor component may be
zero. A dedicated regression test covers 9.0 and rejects a zero major.

## Negative-path review

- A missing Python package, CUDA header, NVCC, NVRTC, NVVM, libdevice, compiler,
  tool, SDK header, baseline object, clean checkout, or fresh artifact path
  keeps `ready_for_gpu_exam=false`.
- A failed or malformed callback child receipt keeps readiness false even when
  the child process exits zero.
- A callback receipt cannot pass if it crossed `prepare`, loaded the native
  library, performed GPU execution, changed the four-role topology, changed
  the selected provider, or lacks complete executable identity hashes.
- An SDK/header mismatch or failed `optixInit()` keeps readiness false and is
  classified as repairable engineering.
- Multi-GPU pods remain valid; container ordinal zero is selected and later
  bound to the native descriptor.
- No preflight result is described as GPU evidence or Goal5838 success.

## Local evidence

- Goal5838 focused tests pass `87/87`.
- Goal5838 plus inherited Goal5833 built-in-sphere tests pass `157/157`.
- Stored generic-core seal verification passes with zero frozen-file changes.
- Stored independent challenge selection verification passes.
- Python byte compilation passes for all changed Python files.
- Ruff passes for every modified Python file.
- `git diff --check` passes.
- The synthetic R550 plus OptiX 8 readiness path remains accepted; no minimum
  driver constant exists.
- Unit tests bind the exact CUDA compiler environment into generated build and
  run commands, require explicit ambient-variable removal, validate canonical
  `ldd` resolution, reject compiler contamination, and reject callback receipts
  that cross the no-launch boundary.
- A real full preflight invocation on this non-NVIDIA Mac exits one, preserves
  all three local gates as passing, writes schema v2 with
  `scientific_failure_claimed=false` and `gpu_execution_performed=false`, and
  classifies only the missing pod environment plus the intentionally dirty
  pre-commit tree as repair work.

## Residual findings

### O1, P2: current-commit callback compilation and GPU execution require a pod

This Mac has no NVIDIA CUDA/NVVM/NVRTC/OptiX environment. The new real compiler
probe is implemented and locally structurally tested, but it has not yet run
against an actual pod toolchain. The exact current commit also still lacks its
required two true OptiX executions and RTDL-free final verification.

### O2, P2: an endpoint with no host NVIDIA/OptiX capability is not repairable inside the container

The agent can install every user-space dependency and select older or newer
exact OptiX headers, but cannot create a missing physical NVIDIA device or
replace a provider-controlled host driver from inside the pod. This is the
only reason the completion plan may request another arbitrary NVIDIA pod. It
does not justify prescribing R570, OptiX 9, or another image to the owner.

### O3, P3: external review remains deferred

The owner directed strict internal self-review while traveling. No external
review or multi-AI consensus is claimed. This remains a later CGO submission
gate, not a prerequisite for using the next pod.

## Final internal decision

The mutable Goal5838 execution tooling is ready to commit and expose to an
unknown NVIDIA pod. The next owner action is only to provide a reachable SSH
command. The agent must then perform intake, environment repair, SDK
negotiation, exact build, two real executions, independent verification,
evidence recovery, final audit, and Git synchronization without returning
software-selection work to the owner.

This review authorizes no performance, speedup, Paper App, arbitrary Callback-
IR, external-review, consensus, or Goal5838 completion claim.
