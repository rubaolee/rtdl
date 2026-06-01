# Goal2976: v2.5 Release-Gap Position After Toolchain Scope

Date: 2026-06-01
Status: positioning report; no release authorization

## Purpose

Goal2972 and Goal2973 closed the hidden compiler/toolchain-scope gap by making
the current packet's comparison boundary machine-readable and fail-closed. This
report records where v2.5 stands after that change, so the next action is based
on the actual remaining gaps rather than on generic "run more pod tests" energy.

## Current Internal Evidence

| Area | Current status |
| --- | --- |
| Current packet | Goal2973 seven-app packet |
| Packet source commit | `63158f6db0a2248d203476633ea9f5171a0b596b` |
| Packet result | `pass`, `7 / 7`, clean source, empty claim violations |
| 10-app triage | `pass`, `10` rows, `0` performance targets, `top_priority: null` |
| Readiness validator | `accept` at commit `ef1acfd6` |
| External reviews | Goal2974 Gemini `accept`, Goal2975 Claude `accept` |
| Toolchain scope | Same source / same GPU / same runner with visible native and partner stacks |
| Compiler fairness wording | Still not authorized; compiler flag alignment is not proven |

## What Is Actually Solved

- The A5000 canonical packet is clean and current.
- RTDL's ten-benchmark v2.5 triage has no active performance target.
- The packet now proves that native OptiX, Triton, Torch, CuPy, and Numba stacks
  were visible in the current comparison.
- The readiness gate now rejects missing Goal2972 scope metadata and rejects any
  accidental compiler-fairness, public-speedup, or release authorization flip.
- The RayDB planner decision is preserved: use primitive-first fused reductions
  for exact fused count/sum, and use hit-stream/partner continuations for
  unfused richer continuations.

## What Is Not Solved

| Gap | Why the current A5000 pod cannot close it |
| --- | --- |
| Second-architecture or multivendor performance check | This pod is the same NVIDIA RTX A5000 architecture already used for the canonical packet. |
| Compiler equivalence proof | The packet records visible stacks, but nvcc/PTX, Triton/LLVM JIT, CuPy/NVRTC/library paths, Torch/ATen, and Numba CUDA JIT are not identical compilers. |
| Release authorization | Release needs an explicit user-triggered release packet and fresh 3-AI release consensus. |
| Public speedup wording | Public wording requires a separate scoped claim review after the release packet. |
| v3.0 user shader extension | Still future architecture work; v2.5 does not expose arbitrary user-defined RT shaders. |

## Current Best Next Actions

1. If the user wants to continue v2.5 internal hardening on this same A5000 pod:
   run only targeted repeat/stability checks for specific rows. Do not treat
   another same-GPU packet as closing the second-architecture gap.
2. If the user wants to move toward a real v2.5 release:
   request a fresh release packet explicitly, then obtain fresh 3-AI release
   consensus. This report does not start that process.
3. If the user wants to close the remaining performance-evidence gap:
   provide a different accepted performance platform, such as another NVIDIA
   architecture with RT cores and Triton support, or a separately scoped
   multivendor platform. The local GTX 1070 is useful for smoke only because it
   lacks RT cores and is below the Triton performance baseline required here.
4. If the user wants to continue toward v3.0:
   start the user-defined shader/extension design lane separately, with no
   backdoor app-specific native engine logic in v2.5.

## Boundary

Goal2976 is a positioning report only. It does not authorize v2.5 release,
release tags, public speedup wording, broad RT-core wording, whole-app speedup
wording, true-zero-copy wording, package-install wording, paper reproduction,
Triton preview auto-selection, or app-specific native engine customization.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2976_v2_5_release_gap_position_after_toolchain_scope_test

Ran 3 tests
OK
```
