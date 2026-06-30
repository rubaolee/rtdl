# Call For Review: Goal2892 Runtime Provenance Conformance Index

Date: 2026-05-31

Repository: `rubaolee/rtdl`

Current main commit to review: `bf2103f8`

## One-Sentence Reviewer Prompt

Please review Goals2889-2891 at commit `bf2103f8` and determine whether the readiness packet now honestly links the bounded Triton torch-carrier runtime provenance evidence to the partner conformance snapshot without turning indexed pod evidence into a release, speedup, true-zero-copy, auto-Triton, or app-specific-engine claim.

## Context

Goal2889 wrapped the actual bounded Triton torch-carrier `_torch_as(...)`
conversions under neutral-buffer seam leases. Goal2891 then indexed that runtime
provenance inside `partner_conformance_snapshot` using explicitly named
`*_indexed` fields so the readiness packet remains an evidence index, not a live
runtime proof or release authorization.

## Files To Inspect

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2889_torch_carrier_copy_decision_seam_lease_wrap_test.py`
- `tests/goal2891_runtime_provenance_index_in_conformance_snapshot_test.py`
- `docs/reports/goal2889_torch_carrier_copy_decision_seam_lease_wrap_2026-05-31.md`
- `docs/reports/goal2891_runtime_provenance_index_in_conformance_snapshot_2026-05-31.md`
- `docs/reviews/goal2886_claude_review_runtime_trace_and_conformance_snapshot_2026-05-31.md`

## Questions For Review

1. Does Goal2889 materially address Goal2886's "parallel attestation" concern by
   wrapping the actual bounded torch-carrier copy decision in seam leases?
2. Does Goal2891 correctly expose runtime provenance through
   `partner_conformance_snapshot` without pretending that the readiness packet
   itself performed a fresh runtime measurement?
3. Are the `*_indexed` field names precise enough to avoid overclaiming?
4. Are all boundaries intact: no v2.5 release authorization, no public speedup
   claim, no true-zero-copy claim, no automatic Triton selection, and no
   app-specific native-engine behavior?
5. What residual release-watch items remain?

## Validation Already Run

Local Windows focused validation for Goal2891:

```text
py -3 -m unittest \
  tests.goal2891_runtime_provenance_index_in_conformance_snapshot_test \
  tests.goal2889_torch_carrier_copy_decision_seam_lease_wrap_test \
  tests.goal2885_v2_5_partner_conformance_readiness_snapshot_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 19 tests in 1.071s

OK (skipped=1)
```

Pod focused validation on `root@69.30.85.171:22167` after fast-forwarding
`/root/rtdl_goal2785_work` to `be5b7020`:

```text
python3 -m unittest \
  tests.goal2891_runtime_provenance_index_in_conformance_snapshot_test \
  tests.goal2889_torch_carrier_copy_decision_seam_lease_wrap_test \
  tests.goal2885_v2_5_partner_conformance_readiness_snapshot_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 19 tests in 1.829s

OK
```

## Expected Review Output

Write the review to:

- `docs/reviews/goal2892_<reviewer>_review_runtime_provenance_conformance_index_2026-05-31.md`

Use one of the established verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This review must not authorize a v2.5 release by itself. Any v2.5 release still
requires an explicit user-requested release packet and fresh 3-AI consensus.
