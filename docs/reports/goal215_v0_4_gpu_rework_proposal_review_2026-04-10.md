# Goal 215 Review Closure

Date: 2026-04-10
Status: closed under Codex + Gemini

## Review artifacts

- Proposal:
  - [/Users/rl2025/rtdl_python_only/docs/goal_215_v0_4_gpu_rework_proposal.md](/Users/rl2025/rtdl_python_only/docs/goal_215_v0_4_gpu_rework_proposal.md)
- Goal report:
  - [/Users/rl2025/rtdl_python_only/docs/reports/goal215_v0_4_gpu_rework_proposal_2026-04-10.md](/Users/rl2025/rtdl_python_only/docs/reports/goal215_v0_4_gpu_rework_proposal_2026-04-10.md)
- Codex consensus:
  - [/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-10-codex-consensus-goal215-v0_4-gpu-rework-proposal.md](/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-10-codex-consensus-goal215-v0_4-gpu-rework-proposal.md)
- Gemini review:
  - [/Users/rl2025/rtdl_python_only/docs/reports/gemini_goal215_v0_4_gpu_rework_proposal_review_2026-04-10.md](/Users/rl2025/rtdl_python_only/docs/reports/gemini_goal215_v0_4_gpu_rework_proposal_review_2026-04-10.md)

## Outcome

The proposal is accepted as the corrected `v0.4` working definition.

The nearest-neighbor line is reopened under this revised bar:

- OptiX is required for both new workloads
- Vulkan is required to run correctly for both new workloads
- CPU/oracle plus Embree alone are no longer sufficient final closure

## Next implementation order

1. Goal 216: OptiX `fixed_radius_neighbors`
2. Goal 217: OptiX `knn_rows`
3. Goal 218: Vulkan `fixed_radius_neighbors`
4. Goal 219: Vulkan `knn_rows`
5. Goal 220: GPU benchmark/support-matrix refresh
6. Goal 221: final re-audit
