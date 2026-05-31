# Goal2792 - Partner-Selection Explain Plan

Date: 2026-05-31

## Purpose

Goal2791 made the mixed Hausdorff/X-HD tiled evidence machine-readable. Goal2792
adds the next layer: an explain-only planner that can look at shape, dtype, and
memory hints and tell the caller why a partner strategy is or is not a candidate.

This is deliberately not a dispatcher. It does not execute kernels and does not
choose a backend for the user; every path still requires explicit caller choice.

## What Changed

Updated:

- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/__init__.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `tests/goal2792_partner_selection_explain_plan_test.py`

New helper:

```python
rt.explain_v2_5_partner_selection(
    operation,
    workload_shape,
    source_count=None,
    target_count=None,
    row_count=None,
    dtype="float64",
    available_device_bytes=None,
    candidate_block_size=4096,
)
```

The helper returns metadata such as:

- guidance status;
- planner status;
- source/target/row shape;
- dtype;
- estimated dense score bytes;
- estimated tiled witness bytes;
- memory note;
- suggested explicit partner candidate;
- suggested explicit strategy candidate;
- reasons;
- claim-boundary flags.

It always returns:

- `execution_strategy_selected: False`
- `auto_select_partner_allowed: False`
- `requires_explicit_caller_choice: True`

## Behavior

| Scenario | Explain result |
| --- | --- |
| 32K x 32K float64 tiled Hausdorff/X-HD shape | `thresholded_triton_candidate_explicit_choice_required`; candidate is `triton` plus `dense_point_nearest_tiled`, but caller must explicitly choose it |
| 8K x 8K float64 tiled Hausdorff/X-HD shape | `comparison_partner_candidate_below_threshold_or_unmeasured_dtype`; candidate remains the same-contract Torch branch |
| dense top-k ranking with negative guidance | `comparison_partner_candidate_due_to_negative_preview` |
| unknown shape | `no_measured_guidance_explicit_choice_required` |

The 32K branch also reports that the estimated dense score matrix exceeds a
7 GiB available-memory hint, while the tiled witness estimate is far smaller.
That is an explanation, not a speedup claim.

## Boundary

Goal2792 authorizes:

- explainable partner-selection metadata;
- shape-aware threshold reasoning;
- memory-estimate reporting;
- explicit candidate suggestions.

Goal2792 does not authorize:

- automatic partner selection;
- hidden dispatch;
- public speedup claims;
- RT-core speedup claims;
- whole-app speedup claims;
- true zero-copy claims;
- v2.5 release readiness.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2792_partner_selection_explain_plan_test \
  tests.goal2791_thresholded_partner_selection_guidance_test \
  tests.goal2782_v2_5_partner_selection_guidance_test \
  tests.goal2783_v2_5_app_migration_selection_guidance_test

Ran 23 tests in 0.023s
OK

py_compile with PYTHONPYCACHEPREFIX=scratch\pycache_goal2792_local

OK
```

## Decision

`accept-with-boundary`

Consensus:

`docs/reports/goal2792_partner_selection_explain_plan_consensus_2026-05-31.md`
