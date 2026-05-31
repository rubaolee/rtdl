# Goal2879 Torch Carrier Seam Authority Provenance

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

Goal2868's strongest remaining release-watch item was the legacy torch carrier:
it was bounded and labeled, but not removed. Goal2871 made the neutral buffer
seam authoritative, and Goal2878 mapped that residual to newer evidence. Goal2879
tightens the live metadata so the torch carrier can no longer look like it
originates transfer/copy/lifetime authority.

## Implementation

Updated:

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/v2_5_internal_readiness.py`

Added:

- `tests/goal2879_torch_carrier_seam_authority_provenance_test.py`

Changes:

- added `transfer_copy_lifetime_authority` to the recursive forbidden authority
  fields for torch-carrier metadata;
- removed the authority-looking `transfer_copy_lifetime_authority` field from
  `describe_v2_5_hit_stream_torch_carrier_adapter(...)`;
- added explicit carrier-only provenance:
  - `carrier_metadata_scope: triton_launch_carrier_only`
  - `authoritative_metadata_origin: neutral_buffer_seam_only`
- extended `validate_v2_5_hit_stream_neutral_seam_authority(...)` so the
  adapter must remain carrier-scoped and must identify the neutral seam as the
  only source of authoritative transfer/copy/lifetime metadata.

## Boundary

This does not remove the Triton torch carrier. It makes the boundary clearer and
more machine-checkable: torch remains a bounded Triton launch carrier, not a
neutral protocol, not a partner-selection shortcut, not a zero-copy proof, and
not an origin of transfer/copy/lifetime metadata.

Goal2879 is not a v2.5 release authorization, not a public speedup claim, not a
broad RT-core claim, not a whole-app speedup claim, not true-zero-copy wording,
and not package-install wording.

## Validation

Focused local validation:

```text
py -3 -m unittest \
  tests.goal2879_torch_carrier_seam_authority_provenance_test \
  tests.goal2878_goal2868_residual_closure_mapping_test \
  tests.goal2871_hit_stream_torch_carrier_seam_authority_guard_test \
  tests.goal2789_neutral_buffer_torch_carrier_reconciliation_test \
  tests.goal2775_hit_stream_neutral_seam_reconciliation_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 29 tests in 0.429s
OK
```

Expanded local residual/conformance slice:

```text
py -3 -m unittest \
  tests.goal2879_torch_carrier_seam_authority_provenance_test \
  tests.goal2878_goal2868_residual_closure_mapping_test \
  tests.goal2876_current_packet_after_partner_conformance_closure_test \
  tests.goal2875_numba_runtime_conformance_smoke_test \
  tests.goal2874_triton_preview_current_pod_conformance_backfill_test \
  tests.goal2873_v2_5_partner_conformance_matrix_test \
  tests.goal2872_triton_tie_break_conformance_smoke_test \
  tests.goal2871_hit_stream_torch_carrier_seam_authority_guard_test \
  tests.goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_test \
  tests.goal2806_v2_5_internal_readiness_packet_test \
  tests.goal2789_neutral_buffer_torch_carrier_reconciliation_test \
  tests.goal2775_hit_stream_neutral_seam_reconciliation_test

Ran 61 tests in 1.419s
OK (skipped=6)
```

Pod validation from pushed `main`:

```text
commit: 3b116a53
scope:
  tests.goal2879_torch_carrier_seam_authority_provenance_test
  tests.goal2878_goal2868_residual_closure_mapping_test
  tests.goal2876_current_packet_after_partner_conformance_closure_test
  tests.goal2875_numba_runtime_conformance_smoke_test
  tests.goal2874_triton_preview_current_pod_conformance_backfill_test
  tests.goal2873_v2_5_partner_conformance_matrix_test
  tests.goal2872_triton_tie_break_conformance_smoke_test
  tests.goal2871_hit_stream_torch_carrier_seam_authority_guard_test
  tests.goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_test
  tests.goal2806_v2_5_internal_readiness_packet_test
  tests.goal2789_neutral_buffer_torch_carrier_reconciliation_test
  tests.goal2775_hit_stream_neutral_seam_reconciliation_test

Ran 61 tests in 1.938s
OK
```

## Codex Verdict

`accept-with-boundary`
