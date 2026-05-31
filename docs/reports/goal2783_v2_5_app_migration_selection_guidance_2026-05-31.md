# Goal2783 - v2.5 App Migration Selection Guidance

Date: 2026-05-31

## Purpose

Goal2782 made the planner lesson machine-readable:

**preview kernel available is not the same as selected partner.**

Goal2783 wires that lesson into the v2.5 benchmark-app migration planner so
the plan no longer treats dense top-k and dense vector-sum Triton previews as
automatic performance choices.

## What Changed

Updated:

`src/rtdsl/v2_5_triton_app_migration.py`

The migration plan now carries:

- `partner_selection_guidance_version`
- `partner_selection_guidance_integrated: True`
- `auto_select_preview_partner_allowed: False`
- per-app `partner_selection_guidance`
- per-app `measured_negative_preview_guidance_count`

Two benchmark app rows now consume Goal2782 guidance:

| App | Operation | Workload shape | Evidence | Planner result |
| --- | --- | --- | --- | --- |
| RTNN | `grouped_topk_f64` | dense exact top-k candidate ranking | Goal2780 | do not auto-select Triton |
| Barnes-Hut | `grouped_vector_sum_f64x2` | dense grouped vector sum 2D | Goal2781 | do not auto-select Triton |

The generic Triton preview kernels still exist. This goal only prevents a
planner or benchmark harness from mistaking preview availability for a selected
performance path.

## Boundary

This goal authorizes:

- app-migration planner metadata that consumes measured negative guidance;
- explicit same-contract partner choice for dense top-k and dense vector-sum
  paths;
- continued Triton preview coverage without automatic selection.

This goal does not authorize:

- public speedup claims;
- RT-core speedup claims;
- true zero-copy claims;
- whole-app speedup claims;
- v2.5 release readiness;
- replacing RTDL/OptiX traversal with partner code;
- auto-selecting Triton just because a preview kernel exists.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2783_v2_5_app_migration_selection_guidance_test \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2676_v2_5_triton_partner_pivot_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test \
  tests.goal2723_v2_5_tiered_benchmark_manifest_test

Ran 33 tests in 0.048s
OK (skipped=3)

py_compile with `PYTHONPYCACHEPREFIX=scratch\pycache_goal2783`

OK
```

Pod validation is useful but not required for new timing because this goal
consumes the Goal2780 and Goal2781 pod artifacts rather than collecting new
kernel timing.

Independent review:

- `docs/reviews/goal2783_claude_review_app_migration_selection_guidance_2026-05-31.md`
- verdict: `accept`

## Decision

`accept`

Consensus:

`docs/reports/goal2783_v2_5_app_migration_selection_guidance_consensus_2026-05-31.md`
