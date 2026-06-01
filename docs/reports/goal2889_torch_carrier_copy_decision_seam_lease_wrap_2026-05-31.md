# Goal2889 Torch Carrier Copy Decision Seam Lease Wrap

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

Claude's Goal2886 review accepted the Goal2883 runtime trace but noted that the
lease lifecycle was still a parallel attestation beside the actual `_torch_as`
conversion. Goal2889 wraps the actual Triton torch-carrier conversions in the
neutral-seam lease lifecycle.

## Implementation

Updated:

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2883_torch_carrier_runtime_seam_trace_test.py`

Added:

- `tests/goal2889_torch_carrier_copy_decision_seam_lease_wrap_test.py`

The execution path now uses `_torch_as_under_neutral_seam_lease(...)` for:

- `primitive_ids`
- `primitive_group_ids`
- `primitive_values`

Each conversion begins a neutral-buffer lease, executes `_torch_as(...)`, then
completes the lease. The runtime trace records:

- `copy_decision_wrapped_by_seam_lease: true` for executed paths;
- per-column `conversion_executed_under_seam_lease: true`;
- the existing observed pointer evidence remains separate.

## Boundary

This is a runtime governance hardening for the bounded Triton torch-carrier
gather path. It does not remove the carrier, does not prove true zero-copy, does
not prove speedup, does not authorize Triton auto-selection, and does not
authorize release.

Future promoted partner paths still need their own runtime seam-lease wrapping.

Goal2889 is not a v2.5 release authorization, not a public speedup claim, not a
broad RT-core claim, not a whole-app speedup claim, not true-zero-copy wording,
and not package-install wording.

## Validation

Focused local validation:

```text
py -3 -m unittest \
  tests.goal2889_torch_carrier_copy_decision_seam_lease_wrap_test \
  tests.goal2887_goal2886_review_intake_and_carrier_authority_field_rename_test \
  tests.goal2883_torch_carrier_runtime_seam_trace_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 20 tests in 0.804s

OK (skipped=2)
```

Focused pod validation on `root@69.30.85.171:22167`, after fast-forwarding
`/root/rtdl_goal2785_work` to `86cbcaae`, with torch execution active:

```text
python3 -m unittest \
  tests.goal2889_torch_carrier_copy_decision_seam_lease_wrap_test \
  tests.goal2887_goal2886_review_intake_and_carrier_authority_field_rename_test \
  tests.goal2883_torch_carrier_runtime_seam_trace_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 20 tests in 1.804s

OK
```

## Codex Verdict

`accept-with-boundary`
