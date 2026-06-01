# Goal2973: Current Packet With Comparison Toolchain Scope

Date: 2026-06-01
Status: pod packet passed; readiness index refreshed

## Purpose

Goal2972 added a comparison-toolchain scope guard to the canonical v2.5 packet
runner. Goal2973 reruns the seven-app canonical packet on the RTX pod from a
clean git tree and refreshes the 10-app triage so the current evidence packet
actually contains that guard.

## Pod Evidence

Pod target: `root@69.30.85.171 -p 22167`

Source commit executed on the pod:

`63158f6db0a2248d203476633ea9f5171a0b596b`

Artifact directory:

`docs/reports/goal2973_current_packet_with_toolchain_scope_pod/`

Packet summary:

| Field | Value |
| --- | --- |
| Status | `pass` |
| Artifacts | `7 / 7` |
| Source dirty | `[]` for runner and child artifacts |
| Claim-boundary violations | `{}` |
| Elapsed | `461.601s` |

10-app triage summary:

| Field | Value |
| --- | --- |
| Status | `pass` |
| Goal label | `Goal2973 current packet performance triage` |
| Triage schema | `Goal2902 v2.5 current packet performance triage` |
| App rows | `10` |
| Performance targets | `0` |
| Top priority | `null` |

## Comparison Toolchain Scope

The packet now records:

| Field | Value |
| --- | --- |
| Scope version | `rtdl.goal2972.comparison_toolchain_scope.v1` |
| Native OptiX stack observed | `true` |
| Current packet stack observed | `true` |
| Partner versions recorded | Triton, Torch, CuPy, Numba all `true` |
| Compiler flag alignment proven | `false` |
| Cross-compiler fairness claim authorized | `false` |
| Public speedup wording authorized | `false` |
| Release authorized | `false` |

This turns the old compiler/toolchain caution into a packet-level invariant:
current comparisons are same-commit, same-GPU, same-runner comparisons with
visible toolchains. They are not a proof that nvcc/PTX, Triton/LLVM JIT,
CuPy/NVRTC or library paths, Torch/ATen, and Numba CUDA JIT are all compiler
equivalent.

## Boundary

Goal2973 is internal v2.5 engineering evidence. It does not authorize:

- v2.5 release or release tag action;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true zero-copy wording;
- package-install wording;
- Triton preview auto-selection;
- paper-reproduction wording;
- app-specific native engine customization.

The second-architecture or multivendor performance check is still not closed by
this A5000 pod packet.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2902_v2_5_current_packet_perf_triage_test tests.goal2973_current_packet_with_comparison_toolchain_scope_test tests.goal2972_comparison_toolchain_scope_guard_test tests.goal2806_v2_5_internal_readiness_packet_test

Ran 17 tests
OK
```
