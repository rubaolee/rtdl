# Handoff: Gemini Review Request for Goals2932-2934

Date: 2026-06-01
Requested reviewer: Gemini / Antigravity, distinct from Codex
Expected output: `docs/reviews/goal2935_gemini_review_goal2932_2934_cupy_vector_selection_2026-06-01.md`

## Context

The v2.5 direction is Python + user-selected partner(s) + RTDL. The native
engine must stay app-agnostic; RTDL/OptiX handles generic RT traversal and
hit-stream-style work, while partners handle generic continuation work when
they win timing.

Recent work:

- Goal2932 added a CuPy grouped vector-sum preview for the generic
  `grouped_vector_sum_f64x2` continuation contract.
- Goal2933 wired Barnes-Hut to measure Torch, Triton, and CuPy for the
  same-contract vector-sum continuation and select the fastest measured
  partner for that shape.
- Goal2934 refreshed the full seven-app current packet after Goal2933, with
  complete Goal2916 toolchain metadata and zero current triage performance
  targets.

## Files to Inspect

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/v2_5_partner_support_matrix.py`
- `src/rtdsl/v2_5_partner_conformance_matrix.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `scripts/goal2803_barnes_hut_v25_consolidated_harness.py`
- `scripts/goal2932_cupy_presegmented_vector_sum_tuning.py`
- `docs/reports/goal2932_cupy_presegmented_vector_sum_partner_2026-06-01.md`
- `docs/reports/goal2933_barnes_hut_cupy_vector_selection_2026-06-01.md`
- `docs/reports/goal2934_current_packet_after_cupy_vector_2026-06-01.md`
- `docs/reports/goal2934_current_packet_after_cupy_vector_pod/goal2855_summary.json`
- `docs/reports/goal2934_current_packet_after_cupy_vector_pod/goal2934_triage.json`
- `tests/goal2932_cupy_presegmented_vector_sum_test.py`
- `tests/goal2933_barnes_hut_cupy_vector_selection_test.py`
- `tests/goal2934_current_packet_after_cupy_vector_test.py`

## Review Questions

Please answer these explicitly:

1. Does Goal2932 keep the CuPy implementation generic, or did it introduce
   Barnes-Hut/app-specific logic into the partner adapter or native engine?
2. Is it acceptable for Triton and CuPy to both preview the same generic
   operation (`grouped_vector_sum_f64x2`) when selection remains explicit and
   measurement-backed?
3. Does Goal2933 correctly preserve the boundary that CuPy is selected for
   the measured Barnes-Hut vector-continuation shape, without claiming
   automatic CuPy selection or global CuPy superiority?
4. Does Goal2934 correctly refresh the current seven-app packet with complete
   OptiX toolchain metadata, zero claim-boundary violations, and no current
   triage performance targets?
5. Are any public-release, broad speedup, true-zero-copy, automatic-partner,
   or paper-reproduction claims accidentally authorized?

## Expected Verdict Vocabulary

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Recommended boundary if accepted: this is internal v2.5 engineering evidence,
not release authorization. Release still requires a user-requested release
packet and fresh 3-AI release consensus.

## Suggested Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2932_cupy_presegmented_vector_sum_test tests.goal2933_barnes_hut_cupy_vector_selection_test tests.goal2934_current_packet_after_cupy_vector_test tests.goal2806_v2_5_internal_readiness_packet_test
```

Also inspect:

```text
docs/reports/goal2934_current_packet_after_cupy_vector_pod/goal2855_summary.json
docs/reports/goal2934_current_packet_after_cupy_vector_pod/goal2934_triage.json
```
