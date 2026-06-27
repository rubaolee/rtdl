# Goal2794 - v2.5 Continuation Determinism Policy

Date: 2026-05-31

## Purpose

Goal2794 turns the v2.5 continuation determinism discussion into a checked
policy surface. This directly addresses the Goal2773 Claude review concern that
witness, tie-break, and determinism risks were named in planning but not hooked
to an acceptance bar.

The policy is deliberately generic. It describes the comparison contract for
partner continuations such as grouped reductions, bounded collection, and
event-ordered hit-stream summaries. It does not add app-specific semantics and
does not authorize public speedup, whole-app, release, or RT-replacement claims.

## Implementation

New module:

- `src/rtdsl/v2_5_determinism_policy.py`

Public import surface through `rtdsl`:

- `V25ContinuationDeterminismPolicy`
- `V2_5_DETERMINISM_POLICY_VERSION`
- `plan_v2_5_continuation_determinism(operation)`
- `v2_5_continuation_determinism_policies()`
- `validate_v2_5_continuation_determinism_policies(...)`

These are importable for inspection and tests, but intentionally not added to
`rtdsl.__all__` or the contract-first `dir(rtdsl)` learning surface.

## Covered Operations

The policy covers all 12 current v2.5 partner-continuation operations exactly
once.

| Operation | Determinism / Tie-Break Contract |
| --- | --- |
| `segmented_count_i64` | Exact integer count, dense group-id order. |
| `segmented_sum_f64` | Floating reduction must publish reduction order or absolute/relative tolerance. |
| `grouped_vector_sum_f64x2` | Floating vector reduction must publish order/tolerance per component. |
| `segmented_min_f64` | Value extremum; no item witness returned; missing groups explicit. |
| `segmented_max_f64` | Value extremum; no item witness returned; missing groups explicit. |
| `compact_mask_i64` | Stable filter preserving input row order. |
| `edge_list_components_i64` | Canonical component label is the smallest node id. |
| `bounded_collect_finalize_i64` | Stable bounded collection; overflow fails closed with no silent truncation. |
| `grouped_argmin_f64` | Lowest score, then lowest `item_id`. |
| `grouped_argmax_f64` | Highest score, then lowest `item_id`. |
| `grouped_topk_f64` | Per rank: lowest score, then lowest `item_id`; duplicate items keep the lowest score. |
| `hit_stream_grouped_ray_id_primitive_i64` | Event-ordered hit stream; first/last use producer event-row order; producer overflow fails closed. |

## Acceptance Hooks

New test:

- `tests/goal2794_v2_5_determinism_policy_test.py`

The test enforces:

- every `V2_5_PARTNER_CONTINUATION_OPERATION_NAMES` entry has exactly one
  determinism policy row;
- top-level and per-row claim flags are false;
- score-witness operations publish `item_id` tie-breaks;
- floating reductions publish tolerance/order policy;
- bounded collection and hit-stream grouping fail closed on overflow;
- unknown app-specific operations fail closed;
- report, review, and consensus artifacts exist before the goal closes.

## Claim Boundary

Still blocked:

- public speedup claims;
- whole-app speedup claims;
- release readiness;
- replacing RT traversal with partner continuations;
- hidden dispatch or automatic partner selection.

This goal only defines deterministic comparison contracts for existing v2.5
generic continuation operations.

## Validation

Local syntax/import probe:

- `py -3 -m py_compile src\rtdsl\v2_5_determinism_policy.py src\rtdsl\__init__.py tests\goal2794_v2_5_determinism_policy_test.py` passed.
- `validate_v2_5_continuation_determinism_policies(...)` returned `accept`
  with 12 operations.
- `py -3 -m unittest tests.goal2794_v2_5_determinism_policy_test tests.goal2696_v2_5_partner_support_matrix_test tests.goal2782_v2_5_partner_selection_guidance_test tests.goal2792_partner_selection_explain_plan_test` passed:
  25 tests.

Pod clean-check validation:

- Host: `root@69.30.85.171`, port `22167`, key:
  `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`.
- Checkout: `/root/rtdl_goal2785_work`.
- Commit: `ba5d99cedc9b56b6770aab07723546577364bc21`.
- Command:
  `PYTHONPATH=src:. python3 -m unittest tests.goal2794_v2_5_determinism_policy_test tests.goal2696_v2_5_partner_support_matrix_test tests.goal2782_v2_5_partner_selection_guidance_test tests.goal2792_partner_selection_explain_plan_test`.
- Result: 25 tests passed on Python 3.12.3.
