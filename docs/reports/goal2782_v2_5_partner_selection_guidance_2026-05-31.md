# Goal2782 - v2.5 Partner-Selection Guidance

Date: 2026-05-31

## Purpose

Goal2780 and Goal2781 both produced the same design lesson:

**preview kernel available is not the same as selected partner.**

The `grouped_topk_f64` and `grouped_vector_sum_f64x2` Triton paths are correct
and useful as generic preview surfaces, but the measured RTX A5000 evidence says
they are slower than the same-contract Torch branches for the dense shapes that
were tested.

Goal2782 turns that lesson into a machine-readable guidance registry so future
planners, examples, and benchmark harnesses do not blindly choose Triton just
because a preview kernel exists.

## What Changed

Added:

`src/rtdsl/v2_5_partner_selection_guidance.py`

New public-but-experimental helpers:

- `v2_5_partner_selection_guidance()`
- `validate_v2_5_partner_selection_guidance(...)`
- `plan_v2_5_partner_selection(operation, workload_shape=None)`

The registry currently has two measured negative-guidance rows:

| Operation | Workload shape | Evidence | Finding | Recommendation |
| --- | --- | --- | --- | --- |
| `grouped_topk_f64` | dense exact top-k candidate ranking | Goal2780 | Triton 47.28x-150.90x slower than Torch | do not auto-select Triton |
| `grouped_vector_sum_f64x2` | dense grouped 2D vector sum | Goal2781 | Triton 4.09x-16.59x slower than Torch | do not auto-select Triton |

This does not demote the generic contracts. It separates **contract
availability** from **performance partner selection**.

## Boundary

This goal authorizes:

- advisory partner-selection metadata;
- explicit recognition of measured negative Triton preview evidence;
- fail-closed planner behavior when no measured guidance exists.

This goal does not authorize:

- no public speedup claim;
- no true zero-copy claim;
- no RT-core speedup claim;
- no whole-app claim;
- no v2.5 release readiness;
- no forced partner selection.

The policy remains: the app/user chooses the partner explicitly, and any planner
may advise only from measured, same-contract evidence.

Post-review hardening:

- Added first-class `rt_core_speedup_claim_authorized: False` and
  `whole_app_speedup_claim_authorized: False` fields to the guidance rows and
  top-level guidance after Claude noted that those claim blocks were previously
  implicit through `promoted_performance_path: False`.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2780_topk_adapter_triton_grouped_topk_test \
  tests.goal2781_grouped_vector_sum_adapter_test

Ran 18 tests in 0.046s
OK (skipped=2)

py -3 -m py_compile \
  src\rtdsl\v2_5_partner_selection_guidance.py \
  src\rtdsl\__init__.py \
  tests\goal2782_v2_5_partner_selection_guidance_test.py

OK

$env:PYTHONPATH='src;.'
py -3 -m unittest <v2.5 preview slice through Goal2782>

Ran 123 tests in 0.093s
OK (skipped=10)
```

No pod is required for this goal because it consumes the already-recorded
Goal2780 and Goal2781 pod artifacts instead of producing new timing evidence.

Pod no-new-timing validation:

```text
Host: 69.30.85.171
Port: 22167
GPU: NVIDIA RTX A5000
Driver: 570.211.01

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2780_topk_adapter_triton_grouped_topk_test \
  tests.goal2781_grouped_vector_sum_adapter_test

Ran 18 tests in 2.566s
OK

PYTHONPATH=src:. python3 -m unittest <v2.5 preview slice through Goal2782>

Ran 123 tests in 2.527s
OK
```

After the post-review claim-field hardening:

```text
tests.goal2782_v2_5_partner_selection_guidance_test
tests.goal2696_v2_5_partner_support_matrix_test
tests.goal2780_topk_adapter_triton_grouped_topk_test
tests.goal2781_grouped_vector_sum_adapter_test

Ran 18 tests in 0.041s
OK (skipped=2)

py_compile with `PYTHONPYCACHEPREFIX=scratch\pycache_goal2782`

OK
```

## Decision

`accept`

Consensus:

`docs/reports/goal2782_v2_5_partner_selection_guidance_consensus_2026-05-31.md`
