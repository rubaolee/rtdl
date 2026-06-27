# Handoff: Gemini Review For Goal2787

Date: 2026-05-31

Please perform an independent read-only review of Goal2787 and write your
review to:

`docs/reviews/goal2787_gemini_review_hausdorff_generic_argmin_argmax_triton_adapter_2026-05-31.md`

## Scope

Goal2787 wires the Python-side Hausdorff/X-HD wrapper through generic v2.5
continuation primitives instead of adding any Hausdorff-shaped native or Triton
continuation code.

The main report is:

`docs/reports/goal2787_hausdorff_generic_argmin_argmax_triton_adapter_2026-05-31.md`

The pod timing artifact is:

`docs/reports/goal2787_pod_artifacts/goal2787_hausdorff_generic_argmin_argmax_pod_69_30_85_171_2026-05-31.json`

## Files To Inspect

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/triton_partner_continuation.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/adapters/reductions.py`
- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2787_hausdorff_generic_argmin_argmax_triton_adapter_test.py`
- `tests/goal2782_v2_5_partner_selection_guidance_test.py`
- `tests/goal2783_v2_5_app_migration_selection_guidance_test.py`
- `docs/reports/goal2782_v2_5_partner_selection_guidance_2026-05-31.md`
- `docs/reports/goal2783_v2_5_app_migration_selection_guidance_2026-05-31.md`

## Review Questions

1. Does Goal2787 keep the reusable continuation substrate generic, with no
   Hausdorff/X-HD/app vocabulary in `src/rtdsl/triton_partner_continuation.py`?
2. Does the Python adapter correctly compose `grouped_argmin_f64` followed by
   `grouped_argmax_f64` and preserve deterministic witness/tie behavior?
3. Does the Hausdorff wrapper use the generic adapter without claiming RT-core
   acceleration, true zero-copy, whole-app speedup, or v2.5 release readiness?
4. Does the pod timing evidence correctly support a negative guidance row for
   dense exact Hausdorff-style reductions, with Triton measured 31.880x to
   45.145x slower than Torch on the tested shapes?
5. Do the partner-selection and app-migration guidance files block blind
   automatic Triton selection for this dense witness-reduction shape?

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please include the exact verdict in the review. If you accept with a boundary,
state the boundary precisely.
