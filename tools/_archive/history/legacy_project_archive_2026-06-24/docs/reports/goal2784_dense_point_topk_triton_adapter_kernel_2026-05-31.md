# Goal2784 - Dense Point Top-K Triton Adapter Kernel

Date: 2026-05-31

## Purpose

Goal2780 proved that the first Triton top-k route was correct but slow: the
adapter materialized a dense query-by-candidate score matrix, flattened it into
generic grouped rows, and then ran the generic `grouped_topk_f64` continuation.

Goal2784 adds a bounded dense point top-k adapter kernel that computes exact
top-k per query without dense score materialization. The kernel is still a
partner-side adapter path, not native RTDL/OptiX traversal.

## What Changed

Updated:

- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/partner_adapters.py`

Added:

- `run_triton_dense_point_topk_2d(...)`
- `_triton_dense_point_topk_2d_kernel(...)`
- adapter metadata fields:
  - `v2_5_triton_adapter_kernel`
  - `v2_5_triton_score_materialization`

The kernel launches one Triton program per query, scans the candidate point
column in one bounded block, and emits the exact ranked nearest-neighbor rows
with the same tie-break as the Torch same-contract branch: distance, then
candidate id.

Updated `src/rtdsl/v2_5_partner_selection_guidance.py` so dense top-k guidance
now points at Goal2784 rather than the older Goal2780 timings. The planner
message remains negative: the new kernel is much better than the old path, but
Torch remains faster on the measured dense shapes.

## Boundary

This goal authorizes:

- a bounded Triton adapter kernel for exact dense 2D point top-k;
- avoiding dense score materialization in the Triton adapter path;
- same-contract comparison against the Torch branch.

This goal does not authorize:

- public speedup claims before pod timing evidence is recorded and reviewed;
- RT-core speedup claims;
- true zero-copy claims;
- whole-app speedup claims;
- v2.5 release readiness;
- replacing RTDL/OptiX traversal with partner code.

This is not an RT-core speedup claim. The measured path is partner-side Triton
post-processing over caller-supplied point columns.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2784_dense_point_topk_triton_adapter_kernel_test \
  tests.goal2780_topk_adapter_triton_grouped_topk_test \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2783_v2_5_app_migration_selection_guidance_test

Ran 18 tests in 0.013s
OK (skipped=2)

py_compile with `PYTHONPYCACHEPREFIX=scratch\pycache_goal2784_final`

OK
```

Pod timing validation:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000
Driver: 570.211.01
Work clone: /root/rtdl_goal2784_work
Base commit: 00098d5b plus Goal2784 patch

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2784_dense_point_topk_triton_adapter_kernel_test \
  tests.goal2780_topk_adapter_triton_grouped_topk_test \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2783_v2_5_app_migration_selection_guidance_test

Ran 18 tests in 2.617s
OK
```

Timing artifact:

`docs/reports/goal2784_pod_artifacts/goal2784_dense_point_topk_triton_adapter_pod_69_30_85_171_2026-05-31.json`

| Query count | Candidate count | k | Triton dense adapter median sec | Torch median sec | Triton / Torch |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 3 | 2 | 0.003875519 | 0.000400161 | 9.685x |
| 256 | 512 | 8 | 0.003959540 | 0.000402057 | 9.848x |
| 512 | 1024 | 8 | 0.004068004 | 0.000405289 | 10.037x |
| 1024 | 2048 | 8 | 0.004248493 | 0.000865655 | 4.908x |

Correctness matched Torch on query ids, neighbor ids, neighbor ranks, and
distances for all rows.

## Decision

`accept-with-boundary`

The dense Triton adapter kernel is accepted as an implementation improvement:
it removes dense score materialization and cuts the old Goal2780 slowdown from
47x-151x to 4.9x-10.0x on the measured RTX A5000 shapes. It is not promoted as
the selected dense top-k performance path because Torch remains faster.

Independent reviews:

- `docs/reviews/goal2784_claude_review_dense_point_topk_triton_adapter_2026-05-31.md`
- `docs/reviews/goal2784_gemini_review_dense_point_topk_triton_adapter_2026-05-31.md`

Consensus:

`docs/reports/goal2784_dense_point_topk_triton_adapter_kernel_consensus_2026-05-31.md`
