# 3-AI Consensus: Goal 1429 v1.5.1 COLLECT_K_BOUNDED Adapter Parity OptiX Closure

## Verdict

Codex, Claude, and Gemini agree that the RTX A5000 pod required-OptiX parity
evidence closes the post-adapter OptiX parity blocker recorded in Goal 1428.

Adapter-routed polygon-pair parity is now accepted for both Embree and OptiX.

## Consensus Basis

Codex ran the pod build/parity package and updated the contract boundary.

Claude review:

- `docs/reports/claude_goal1429_v1_5_1_collect_k_adapter_parity_optix_closure_review_2026-05-06.md`
- Verdict: `ACCEPT`
- Blocking issues: none

Gemini review:

- `docs/reports/gemini_goal1429_v1_5_1_collect_k_adapter_parity_optix_closure_review_2026-05-06.md`
- Verdict: `ACCEPT`
- Blocking issues: none

Closure report:

- `docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_optix_closure_2026-05-06.md`

External review request:

- `docs/handoff/goal1429_external_review_request_2026-05-06.md`

## Evidence

RTX A5000 pod:

- SSH: `root@69.30.85.196 -p 22030 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_pod_69_30_85_196`
- GPU: NVIDIA RTX A5000
- Driver: 580.126.09
- CUDA: 13.0, `nvcc` V13.0.88
- OptiX headers: `/root/vendor/optix-dev/include/optix.h`
- Git HEAD: `da7664f88c54aefdbe4d6f6069f26e5c4eb2e8da`

Build artifact:

- `docs/reports/goal1429_v1_5_1_collect_k_build_optix_2026-05-06.txt`

Required OptiX parity artifact:

- `docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_pod_optix_required_2026-05-06.md`
- Result: accepted
- OptiX: pass=4, fail=0, skipped=0
- Required backend skips: none

## Boundary

This consensus does not authorize built generic i64 symbol validation, stable
primitive promotion, speedup wording, zero-copy wording, whole-app claims, broad
workload coverage, release action, or release-tag movement.

Still pending:

- validate `rtdl_embree_collect_k_bounded_i64` and
  `rtdl_optix_collect_k_bounded_i64` in built libraries
- add Embree/OptiX generic ABI parity tests against the built generic i64
  symbols
- rerun stable-promotion review only after those gates pass
