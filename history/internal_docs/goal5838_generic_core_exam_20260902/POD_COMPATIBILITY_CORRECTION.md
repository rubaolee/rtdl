# Goal5838 pod compatibility correction

Date: 2026-09-03

Status: `ENVIRONMENT_POLICY_CORRECTED__FROZEN_CORE_UNCHANGED`

## Correction

The R570-or-newer plus OptiX 9.0 wording in the earlier pre-GPU audit and the
first clean-pod README was too restrictive. It described one desired execution
profile as though it were a preregistered scientific requirement. The Goal5838
preregistration requires a true-GPU OptiX receipt, exact target identity, and
zero changes to the frozen generic core. It does not select one OptiX SDK or
driver branch.

This document supersedes only that environment requirement. It changes no
challenge, callback topology, fixture, oracle, success condition, or frozen
core byte.

## Correct pod policy

Any accessible NVIDIA pod is first treated as an unknown environment. RTDL
records its GPU, UUID, driver, compute capability, CUDA toolkit, Python stack,
compiler, and exact OptiX headers. It then compiles and runs a temporary
zero-launch `optixInit()` probe for a candidate SDK. The newest candidate whose
headers negotiate successfully with the host driver is used for the full
provider build and exam.

An SDK/driver ABI mismatch, missing toolkit component, dependency error, build
error, or provider-extension defect is repairable engineering. The team may
change SDK candidates or repair any preregistered mutable extension layer. None
of these events is scientific failure and none permits a frozen-core change.
Multi-GPU pods are accepted: the formal command selects container GPU 0 with
`CUDA_VISIBLE_DEVICES=0`, and both `nvidia-smi --id=0` and the native runtime
descriptor record the selected target.

The zero-launch ABI probe is required twice by construction: the pod preflight
uses it before authorizing the commands, and the native builder reruns it and
seals its source, compile command, executable, return code, and exact output in
the build manifest. The RTDL-free verifier rejects a missing, altered, failed,
or resealed probe record.

The final build manifest and GPU artifact must agree exactly on:

- selected OptiX SDK and encoded header version;
- hashes of all consumed CUDA and OptiX headers;
- GPU name, UUID, driver, and compute capability;
- compiler, NVCC, source commit, native DSO, and required symbols; and
- the compiled native descriptor observed after real execution.

The independent verifier derives the encoded OptiX version from the recorded
three-component SDK string. It no longer accepts only `9.0.0`, but it still
rejects any mismatch among the target profile, build manifest, loaded DSO, and
native runtime descriptor.

## Candidate acquisition identities

The current NVIDIA `optix-dev` release commits recorded for reproducible pod
acquisition are:

| SDK | Commit |
| --- | --- |
| 9.1.0 | `f1f6dd803f3159992d248178f6e09421c6eb8b6d` |
| 9.0.0 | `fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd` |
| 8.1.0 | `50021ea0af6d41609a97777ceebbdf1e1d34efe7` |
| 8.0.0 | `f60c1e44f18426f426a2ed948f28515b3cf67b8a` |
| 7.7.0 | `7b5c4e8608b8b4b601729f6240fc3fd53cb36d23` |

These are acquisition candidates, not predeclared successful provider
profiles. Only the runtime ABI probe and subsequent full build/execution on the
actual pod establish compatibility.

## Claim boundary

This correction and its local tests are environment/tooling work only. They do
not constitute a native build, GPU execution, prospective success,
performance result, Paper App, arbitrary Callback-IR support, external review,
consensus, or Goal5838 completion.
