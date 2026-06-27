# Goal2784 Consensus - Dense Point Top-K Triton Adapter Kernel

Date: 2026-05-31

## Verdict

`accept-with-boundary`

Goal2784 is accepted as a real implementation improvement, not as a promoted
performance path. The dense point top-k Triton adapter now avoids dense score
materialization and reduces the old Goal2780 slowdown from 47x-151x to
4.91x-10.04x versus Torch on the measured RTX A5000 shapes. Torch remains
faster, so the partner-selection guidance still says not to auto-select Triton
for dense exact top-k ranking.

## Evidence

Codex implementation and validation:

- added `run_triton_dense_point_topk_2d(...)`
- added `_triton_dense_point_topk_2d_kernel(...)`
- routed `top_k_nearest_points_2d_partner_columns(..., partner="triton")`
  through the direct dense adapter kernel
- recorded `v2_5_triton_adapter_kernel: dense_point_topk_2d_adapter_kernel`
- recorded `v2_5_triton_score_materialization: none`
- refreshed Goal2782/Goal2783 guidance from Goal2780 to Goal2784 for dense
  exact top-k
- recorded the deferred future work in `docs/research/future_version_to_do_list.md`

Local Windows validation:

```text
tests.goal2784_dense_point_topk_triton_adapter_kernel_test
tests.goal2780_topk_adapter_triton_grouped_topk_test
tests.goal2782_v2_5_partner_selection_guidance_test
tests.goal2783_v2_5_app_migration_selection_guidance_test

Ran 18 tests in 0.013s
OK (skipped=2)
```

Pod validation:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000
Driver: 570.211.01
Work clone: /root/rtdl_goal2784_work

Ran 18 tests in 2.617s
OK
```

Pod timing artifact:

- `docs/reports/goal2784_pod_artifacts/goal2784_dense_point_topk_triton_adapter_pod_69_30_85_171_2026-05-31.json`

| Query count | Candidate count | k | Triton dense adapter median sec | Torch median sec | Triton / Torch |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 3 | 2 | 0.003875519 | 0.000400161 | 9.685x |
| 256 | 512 | 8 | 0.003959540 | 0.000402057 | 9.848x |
| 512 | 1024 | 8 | 0.004068004 | 0.000405289 | 10.037x |
| 1024 | 2048 | 8 | 0.004248493 | 0.000865655 | 4.908x |

Independent Claude review:

- `docs/reviews/goal2784_claude_review_dense_point_topk_triton_adapter_2026-05-31.md`
- verdict: `accept-with-boundary`
- confirms same-contract output, no dense score materialization, honest
  performance evidence, advisory-only planner guidance, and blocked RT-core /
  true-zero-copy / whole-app / public speedup / release claims

Independent Gemini review:

- `docs/reviews/goal2784_gemini_review_dense_point_topk_triton_adapter_2026-05-31.md`
- verdict: `accept-with-boundary`
- confirms functional parity with Torch, no dense score materialization,
  slower-than-Torch evidence, refreshed planner guidance, and blocked claims

## Boundary

This consensus does not authorize:

- public speedup claims
- RT-core speedup claims
- true zero-copy wording
- whole-app speedup claims
- v2.5 release readiness
- replacing RTDL/OptiX traversal with partner code
- auto-selecting Triton for dense exact top-k ranking

The next top-k performance step is a stronger block/warp-level selection design,
multi-block candidate tiling for larger candidate sets, or continued explicit
Torch/CuPy selection for dense exact ranking.
