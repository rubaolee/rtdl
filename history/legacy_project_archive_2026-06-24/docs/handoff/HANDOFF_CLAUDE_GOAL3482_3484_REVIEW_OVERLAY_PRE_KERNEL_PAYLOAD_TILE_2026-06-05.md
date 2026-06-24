# Handoff: Claude Review For Goal3482-3484 Overlay-Area Pre-Kernel Chain

Please perform an independent read-only review of the RTDL v2.8 spatial RayJoin
overlay-area chain after Goal3481.

## Scope

Review these commits/reports/code paths on `main`:

- Goal3482: `docs/reports/goal3482_overlay_area_pre_kernel_policy_2026-06-05.md`
- Goal3483: `docs/reports/goal3483_overlay_area_prepared_payload_2026-06-05.md`
- Goal3484: `docs/reports/goal3484_overlay_area_tiled_scalar_evaluator_2026-06-05.md`
- `src/rtdsl/v2_8_overlay_area_continuation_contract.py`
- `src/rtdsl/v2_8_overlay_area_prepared_payload.py`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`
- tests:
  - `tests/goal3482_overlay_area_pre_kernel_policy_test.py`
  - `tests/goal3483_overlay_area_prepared_payload_test.py`
  - `tests/goal3484_overlay_area_tiled_scalar_evaluator_test.py`
  - `tests/goal3105_v2_8_benchmark_runtime_gap_map_test.py`

## Review Questions

1. Does Goal3482 correctly close the policy risks you raised in Goal3480:
   explicit tolerance, topology boundary, scratch-capacity behavior, and
   claim-boundary discipline?
2. Does Goal3483 define a reusable, app-agnostic prepared simple polygon
   component payload, rather than smuggling RayJoin-specific behavior into the
   runtime?
3. Does Goal3484 correctly model bounded triangle-pair tiling and no silent
   truncation before a future GPU/native implementation?
4. Are the tests strong enough to guard the policy/payload/tile contracts, or
   are there missing acceptance bars before a device kernel should be attempted?
5. Does the v2.8 gap map now describe the remaining work honestly: actual
   bounded device continuation over the prepared payload, without release,
   RT-core, zero-copy, whole-app, or paper-reproduction authorization?

## Required Output

Write the review to:

`docs/reviews/goal3485_claude_review_overlay_pre_kernel_payload_tile_3482_3484_2026-06-05.md`

Use one of the accepted verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please lead with findings by severity, then answer the review questions. Keep
the review read-only unless you find a severe typo in the output file path.

