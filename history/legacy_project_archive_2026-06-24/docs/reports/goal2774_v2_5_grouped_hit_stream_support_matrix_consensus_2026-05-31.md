# Goal2774 Consensus - v2.5 Grouped Hit-Stream Support Matrix

Date: 2026-05-31

## Verdict

`accept`

Goal2774 is accepted as a contract/support-matrix declaration for the
event-ordered grouped hit-stream reducer added in Goals2771-2772.

This consensus does not promote the path to release readiness, public speedup
claims, true zero-copy claims, or a Triton/Numba implementation.

## Evidence

Codex implementation/test evidence:

- added generic operation `hit_stream_grouped_ray_id_primitive_i64`
- added Python reference semantics with row-order first/last and `-1` empty
  group sentinels
- made the support matrix operation-specific:
  - `python_reference`: `reference_contract`
  - `cupy_conformance`: `preview_not_promoted`
  - `triton`: `unsupported_fail_closed`
  - `numba`: `unsupported_fail_closed`
- tightened the generic planner so unsupported Triton/Numba cells do not win
  over the explicit CuPy preview
- updated the hit-stream transfer planner so the CuPy preview operation reports
  `cuda_descriptor_preview`, not descriptor-only
- refreshed older gate tests that had stale "all operations have Triton
  preview" wording

Independent Gemini review:

- `docs/reviews/goal2774_gemini_review_v2_5_grouped_hit_stream_support_matrix_2026-05-31.md`
- verdict: `accept`
- Gemini confirmed the operation and field names are generic, the matrix
  statuses are honest, claim boundaries remain blocked, reference semantics
  match Goal2772, and Triton/Numba are not falsely treated as implementations
  for the new CuPy-preview operation.
- Gemini could not run shell commands in its environment; execution evidence is
  therefore supplied by the Codex local validation below.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test \
  tests.goal2676_v2_5_triton_partner_pivot_test \
  tests.goal2677_v2_5_triton_segmented_minmax_preview_test \
  tests.goal2678_v2_5_triton_compact_mask_preview_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2680_v2_5_triton_bounded_collect_preview_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2740_hit_stream_cross_partner_transfer_plan_test \
  tests.goal2774_v2_5_grouped_hit_stream_support_matrix_test

Ran 62 tests in 0.048s
OK (skipped=4)
```

Continuity check:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test \
  tests.goal2772_hit_stream_event_ordered_grouped_richer_reductions_test

Ran 13 tests in 0.041s
OK (skipped=2)
```

Compile check:

```text
py -3 -m py_compile \
  src\rtdsl\partner_continuation_protocol.py \
  src\rtdsl\v2_5_partner_support_matrix.py \
  src\rtdsl\hit_stream_handoff.py \
  src\rtdsl\__init__.py \
  tests\goal2662_v2_5_partner_continuation_contract_test.py \
  tests\goal2671_v2_5_preview_gate_test.py \
  tests\goal2680_v2_5_triton_bounded_collect_preview_test.py \
  tests\goal2696_v2_5_partner_support_matrix_test.py \
  tests\goal2740_hit_stream_cross_partner_transfer_plan_test.py \
  tests\goal2774_v2_5_grouped_hit_stream_support_matrix_test.py

OK
```

## Boundary

Still blocked:

- no v2.5 public release authorization
- no public speedup claim
- no true zero-copy claim
- no RT traversal replacement claim
- no Triton/Numba executable kernel for
  `hit_stream_grouped_ray_id_primitive_i64`

Recommended next goal remains Goal2775: reconcile the neutral-buffer seam and
old torch-carrier path before adding more app-facing primitives.
