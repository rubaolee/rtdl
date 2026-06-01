# Handoff: Gemini Review Request for Goals2936-2939

Date: 2026-06-01
Requested reviewer: Gemini / Antigravity, distinct from Codex
Expected output: `docs/reviews/goal2940_gemini_review_goal2936_2939_partner_selection_row_columns_2026-06-01.md`

## Context

This review covers the v2.5 work after the Goal2934 current packet:

- Goal2936 adds a reusable measured partner-selection helper for generic
  grouped 2D vector sums.
- Goal2937 validates that helper on the RTX pod with Torch, Triton, and CuPy.
- Goal2938 adds a generic `OptixRowView` to typed partner-column bridge.
- Goal2939 validates that bridge on Spatial RayJoin PIP, LSI, and overlay-seed
  row views with CuPy columns.

The strategic purpose is to make RTDL easier for users who want Python +
RTDL + their chosen partner libraries, without hiding dispatch in the native
engine and without app-specific native logic.

## Files to Inspect

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `docs/reports/goal2936_measured_vector_partner_selection_helper_2026-06-01.md`
- `docs/reports/goal2937_measured_vector_partner_selection_pod_smoke_2026-06-01.md`
- `docs/reports/goal2937_measured_partner_selection_pod/goal2937_measured_partner_selection.json`
- `docs/reports/goal2938_optix_row_view_typed_partner_columns_2026-06-01.md`
- `docs/reports/goal2939_rayjoin_row_view_partner_columns_pod_smoke_2026-06-01.md`
- `docs/reports/goal2939_rayjoin_row_view_partner_columns_pod/goal2939_rayjoin_row_view_partner_columns.json`
- `tests/goal2936_measured_vector_partner_selection_helper_test.py`
- `tests/goal2937_measured_vector_partner_selection_pod_smoke_test.py`
- `tests/goal2938_optix_row_view_typed_partner_columns_test.py`
- `tests/goal2939_rayjoin_row_view_partner_columns_pod_smoke_test.py`

## Review Questions

Please answer explicitly:

1. Does Goal2936 keep partner selection explicit and measurement-backed, rather
   than adding an invisible smart dispatcher?
2. Does Goal2937 provide valid pod evidence for the measured-selection helper
   while preserving the boundary that CuPy is not globally preferred?
3. Does Goal2938 keep the row-view bridge generic and app-agnostic, or does it
   leak RayJoin/Barnes-Hut semantics into RTDL?
4. Does Goal2939 correctly frame the Spatial RayJoin result as a typed
   payload-column stepping stone, not a finished device-resident row-stream or
   full RayJoin reproduction?
5. Are any release, public speedup, broad RT-core, whole-app speedup, true
   zero-copy, automatic partner-selection, package-install, or paper
   reproduction claims accidentally authorized?

## Expected Verdict Vocabulary

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Recommended boundary if accepted: this is internal v2.5 engineering evidence,
not release authorization. The row-view bridge is host-staged typed-column
handoff, not true device-resident zero-copy.

## Suggested Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2936_measured_vector_partner_selection_helper_test tests.goal2937_measured_vector_partner_selection_pod_smoke_test tests.goal2938_optix_row_view_typed_partner_columns_test tests.goal2939_rayjoin_row_view_partner_columns_pod_smoke_test tests.goal2806_v2_5_internal_readiness_packet_test
```
