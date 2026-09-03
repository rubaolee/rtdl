# Goal5838 unknown-pod completion plan

Date: 2026-09-03

Status: `CONTROLLING_POD_INTAKE_PLAN__OWNER_SUPPLIES_SSH_ONLY`

## Responsibility contract

The owner supplies one reachable SSH command for an already allocated Linux
pod. The owner is not required to select, know, or change its NVIDIA driver,
CUDA toolkit, OptiX SDK, Python image, host compiler, GPU count, or filesystem
layout. The RTDL agent owns discovery, user-space toolchain repair, compatible
SDK selection, execution, and evidence recovery.

There is no R570 driver floor and no mandatory OptiX 9 profile. The agent must
not reject a pod merely because its software profile differs from a preferred
image. Driver and SDK versions are observations used for compatibility
negotiation, not requirements delegated to the owner.

The only irreducible host condition is that the endpoint expose a usable
NVIDIA device and host OptiX implementation to its container. A missing CUDA
toolkit, compiler, Python version, SDK headers, NVVM, NVRTC, or libdevice is
repairable inside the pod. If `nvidia-smi` cannot see any NVIDIA device or the
host exposes no usable OptiX implementation after exact SDK negotiation, no
container-side package can manufacture that host capability. Only then may
the agent ask for another arbitrary NVIDIA pod, without prescribing a driver
branch.

## Phase 0: local release point

Before using paid GPU time, the agent must:

1. verify the stored generic-core seal and challenge selection;
2. prove that none of the three frozen core files changed;
3. run the focused Goal5838 tests under the exact local Python stack;
4. commit and push all mutable provider, runner, preflight, verifier, test, and
   documentation changes; and
5. record the resulting full 40-character commit as the only pod source.

The pod must never run uncommitted local source transferred ad hoc.

## Phase 1: unknown-pod intake

Immediately after SSH connects, the agent records, without making a scientific
classification:

- OS, architecture, shell, package manager, writable storage, and network;
- all visible GPUs, then deterministic container GPU 0;
- GPU name, UUID, driver, compute capability, and `libnvoptix.so.1` visibility;
- every installed CUDA prefix, `nvcc`, NVRTC, NVVM, libdevice, and header set;
- available Python interpreters, NumPy, Numba, Git, `g++`, `nm`, and `ldd`; and
- repository reachability and available disk space.

The agent clones the exact pushed branch and checks out the recorded commit.
For a shallow clone, it fetches the preregistered baseline commit object
separately. The checkout must be clean before any build or execution.

## Phase 2: agent-owned environment repair

The agent first reuses a complete compatible toolchain already present on the
pod. Missing pieces are installed side by side in a task-owned directory; the
host driver is never replaced from inside the container.

The repair order is:

1. obtain an exact Python 3.12 interpreter using the pod's package manager,
   Conda, or a user-space Python installer;
2. create an isolated environment with Numba 0.65.1 and NumPy 2.4.4;
3. install or select Git, a compatible `g++`, binutils, and libc tools;
4. locate a complete CUDA toolkit or install one side by side when only the
   host runtime is present; and
5. resolve and hash exact NVRTC, NVVM, libdevice, CUDA headers, and `nvcc`
   inputs.

The preflight clears ambient CUDA simulator, compiler override, native-library,
and formal-leaf-cache variables. It launches the compiler check in a fresh
child with explicit `CUDA_HOME`, `CUDA_PATH`, `NUMBA_CUDA_NVVM`,
`NUMBA_CUDA_LIBDEVICE`, `PATH`, and `LD_LIBRARY_PATH`. This prevents a passing
result from depending on an unknown image default or an old cached PTX leaf.

## Phase 3: OptiX compatibility negotiation

The agent acquires NVIDIA public `optix-dev` headers by exact commit and tries
the recorded candidates from newest to oldest: 9.1.0, 9.0.0, 8.1.0, 8.0.0,
and 7.7.0. Candidate order is an optimization, not a scientific constraint.

Each candidate must pass all of these checks before it can be selected:

1. exact header version and file hashes;
2. a compiled, executed, zero-launch `optixInit()` host-driver ABI probe;
3. real Numba-to-NVVM compilation of the selected `make_ray`, `any_hit`,
   `miss`, and `finalize` leaves with the detected compute capability;
4. real NVRTC compilation and PTX composition through the generic family
   public materialization front door, without loading the native DSO; and
5. frozen-core, selection, repository-custody, and focused-test gates.

An ABI mismatch advances to another SDK. A callback compiler mismatch repairs
or changes the pod-local CUDA toolkit. Neither result is scientific failure,
and neither authorizes a frozen-core edit.

## Phase 4: exact GPU exam

The passing preflight emits the exact environment-bound commands. The agent
executes them without hand transcription:

1. build the existing generic OptiX provider DSO at `-O3` and repeat the
   zero-launch ABI probe inside the sealed build manifest;
2. verify required dynamic symbols and native-source identities;
3. materialize the independently selected family through the generic public
   lifecycle;
4. execute the primary query order and the independently prescribed reverse
   order on real OptiX traversal; and
5. require all 12 per-query U64 results to equal the RTDL-free exact-rational
   oracle while device role counters and physical receipts prove the selected
   built-in-sphere any-hit continuation path.

The runner must observe one GAS, one SBT record, built-in sphere intersection,
`OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL`, `optixTrace`, and
`optixIgnoreIntersection`. It must also recheck that all frozen bytes and the
Git worktree remain unchanged.

## Phase 5: independent verification and custody

The RTDL-free verifier receives only the GPU artifact and native DSO. It
rederives the fixture, oracle output, selection, family identities, source
inventory, ABI probe, GPU/native descriptor agreement, and traversal receipts.
It must not import `rtdsl`.

The agent then copies the preflight receipt, native DSO, native build manifest,
build log, GPU artifact, and verifier artifact off the pod before it can be
terminated. Hashes are checked after transfer. Evidence is documented against
the exact source commit and pod identity, then subjected to the final strict
internal audit, tests, commit, and push.

## Repair decision table

| Observation | Agent action | Classification |
| --- | --- | --- |
| Python/package mismatch | Build an isolated exact environment | Repairable engineering |
| CUDA headers or `nvcc` absent | Install/select a side-by-side toolkit | Repairable engineering |
| NVRTC/NVVM/libdevice absent | Install/locate them and bind exact paths | Repairable engineering |
| Host compiler incompatibility | Install/select a compatible `g++` | Repairable engineering |
| OptiX candidate fails `optixInit()` | Try the next exact SDK candidate | Repairable engineering |
| Callback PTX compile fails | Repair/change the local CUDA compiler stack | Repairable engineering |
| Native provider build fails | Repair mutable builder/provider code, retest, recommit | Repairable engineering |
| Oracle mismatch | Diagnose mutable provider/app/oracle evidence under the preregistered rules | Not automatically scientific failure |
| Frozen core appears necessary to change | Preserve a minimal witness and apply all preregistered failure conditions | Potential scientific negative only after full audit |
| No visible NVIDIA device or host OptiX implementation | Preserve intake evidence and request another arbitrary NVIDIA pod | Immutable host-capability blocker |

## Interaction policy

The agent reports the intake identity, each compatibility transition, the
selected SDK/toolchain, build completion, each real execution, and evidence
recovery. It does not remain silent through a long build or test. The owner is
asked to act only if SSH stops working or the immutable host capability is
absent; environment repair decisions do not return to the owner.

## Completion condition

Goal5838 is complete only after a clean exact commit produces two true OptiX
executions, all 12 outputs match the independent oracle, the RTDL-free verifier
passes, frozen-core hashes remain exact, evidence survives off-pod, and the
final internal audit and repository sync pass. This plan authorizes no
performance, Paper App, arbitrary-callback, external-review, or consensus
claim.
