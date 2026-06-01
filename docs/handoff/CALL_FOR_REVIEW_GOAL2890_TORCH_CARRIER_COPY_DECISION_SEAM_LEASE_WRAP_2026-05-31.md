# Call For Review: Goal2890 Torch Carrier Copy Decision Seam Lease Wrap

Date: 2026-05-31

Repository: `rubaolee/rtdl`

Current main commit to review: `b12ffac6`

## One-Sentence Reviewer Prompt

Please review Goal2889 at commit `b12ffac6` and determine whether wrapping the actual bounded Triton torch-carrier `_torch_as(...)` conversions in neutral-buffer seam leases materially narrows Goal2886's "parallel attestation" caveat while preserving the no-release, no-speedup, no-true-zero-copy, no-auto-Triton, and no-app-specific-engine boundaries.

## Context

Goal2886 accepted Goal2883/2885 with boundary and noted that the runtime seam
trace was still a parallel attestation beside the actual torch carrier copy
decision. Goal2887 renamed the hardcoded authority field to avoid implying an
observed runtime fact. Goal2889 then moved from parallel-only attestation toward
runtime governance by wrapping the actual `_torch_as(...)` conversions in seam
leases.

## Files To Inspect

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2883_torch_carrier_runtime_seam_trace_test.py`
- `tests/goal2889_torch_carrier_copy_decision_seam_lease_wrap_test.py`
- `docs/reports/goal2889_torch_carrier_copy_decision_seam_lease_wrap_2026-05-31.md`
- `docs/reviews/goal2886_claude_review_runtime_trace_and_conformance_snapshot_2026-05-31.md`

## Questions For Review

1. Does the executed bounded Triton torch-carrier gather path now wrap the actual
   `_torch_as(...)` conversions under neutral-buffer seam leases?
2. Is the static trace still clearly an attestation path, not proof that an
   executed copy decision was wrapped?
3. Does `copy_decision_wrapped_by_seam_lease` truthfully distinguish executed
   torch paths from static traces?
4. Are the boundaries still intact: no v2.5 release authorization, no true
   zero-copy claim, no public speedup claim, no broad RT-core claim, no automatic
   Triton selection claim, and no app-specific native-engine behavior?
5. What residual risks remain before a final v2.5 release packet could be
   considered?

## Validation Already Run

Local Windows focused validation:

```text
py -3 -m unittest \
  tests.goal2889_torch_carrier_copy_decision_seam_lease_wrap_test \
  tests.goal2887_goal2886_review_intake_and_carrier_authority_field_rename_test \
  tests.goal2883_torch_carrier_runtime_seam_trace_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 20 tests in 0.780s

OK (skipped=2)
```

Pod focused validation on `root@69.30.85.171:22167` after fast-forwarding
`/root/rtdl_goal2785_work` to `86cbcaae`:

```text
python3 -m unittest \
  tests.goal2889_torch_carrier_copy_decision_seam_lease_wrap_test \
  tests.goal2887_goal2886_review_intake_and_carrier_authority_field_rename_test \
  tests.goal2883_torch_carrier_runtime_seam_trace_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 20 tests in 1.804s

OK
```

## Expected Review Output

Write the review to:

- `docs/reviews/goal2890_<reviewer>_review_goal2889_torch_carrier_copy_decision_seam_lease_wrap_2026-05-31.md`

Use one of the established verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This review must not authorize a v2.5 release by itself. Any v2.5 release still
requires an explicit user-requested release packet and fresh 3-AI consensus.
