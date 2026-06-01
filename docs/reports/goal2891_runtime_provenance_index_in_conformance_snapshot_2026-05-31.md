# Goal2891 Runtime Provenance Index in Conformance Snapshot

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

Claude's Goal2886 review suggested emitting observed pointer-equality and seam
lease evidence into the canonical conformance snapshot, so reviewers can see
runtime provenance and partner conformance in one surface. Goal2891 adds that
indexing layer.

## Implementation

Updated:

- `src/rtdsl/v2_5_internal_readiness.py`

Added:

- `tests/goal2891_runtime_provenance_index_in_conformance_snapshot_test.py`

The readiness packet's `partner_conformance_snapshot` now includes:

- `runtime_provenance_record_count`
- `runtime_provenance_records`

The current record is:

- `path`: `bounded_triton_torch_carrier_typed_payload_gather`
- `partner`: `triton`
- `carrier`: `torch`
- `operation`: `hit_stream_typed_payload_gather`
- `status`: `pod_runtime_copy_decision_seam_wrapped`
- `evidence_goal`: `Goal2889`
- `goal2883_same_pointer_evidence_indexed`: true
- `goal2889_copy_decision_seam_wrap_indexed`: true
- `goal2889_executed_conversion_seam_lease_indexed`: true

These are index fields over already-recorded pod evidence, not a fresh runtime
measurement performed by the readiness packet itself.

## Boundary

This is a readiness indexing improvement. It links Goal2883/Goal2889 runtime
provenance to the conformance snapshot but does not promote Triton, does not
remove the torch carrier, does not prove true zero-copy, does not prove speedup,
and does not authorize release.

Goal2891 is not a v2.5 release authorization, not a public speedup claim, not a
broad RT-core claim, not a whole-app speedup claim, not true-zero-copy wording,
not Triton preview auto-selection wording, and not package-install wording.

## Validation

Focused local validation:

```text
py -3 -m unittest \
  tests.goal2891_runtime_provenance_index_in_conformance_snapshot_test \
  tests.goal2889_torch_carrier_copy_decision_seam_lease_wrap_test \
  tests.goal2885_v2_5_partner_conformance_readiness_snapshot_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 19 tests in 1.071s

OK (skipped=1)
```

## Codex Verdict

`accept-with-boundary`
