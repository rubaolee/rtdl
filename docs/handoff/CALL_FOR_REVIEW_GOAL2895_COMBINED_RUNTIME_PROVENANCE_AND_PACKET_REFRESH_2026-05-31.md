# Call For Review: Goal2895 Combined Runtime Provenance and Packet Refresh

Date: 2026-05-31

Repository: `rubaolee/rtdl`

Current main commit to review: `f33e31cf`

## One-Sentence Reviewer Prompt

Please review Goals2889, 2891, and 2893 at commit `f33e31cf` and decide whether the bounded Triton torch-carrier copy-decision seam wrap, the runtime-provenance conformance index, and the refreshed clean seven-app packet materially harden v2.5 internal readiness while preserving every release, speedup, true-zero-copy, auto-Triton, paper-reproduction, and app-specific-engine boundary.

## Why This Review Exists

This is a consolidated external-review packet for the work done after Claude's
Goal2886 review. It combines the three smaller handoffs:

- `docs/handoff/CALL_FOR_REVIEW_GOAL2890_TORCH_CARRIER_COPY_DECISION_SEAM_LEASE_WRAP_2026-05-31.md`
- `docs/handoff/CALL_FOR_REVIEW_GOAL2892_RUNTIME_PROVENANCE_CONFORMANCE_INDEX_2026-05-31.md`
- `docs/handoff/CALL_FOR_REVIEW_GOAL2894_CURRENT_PACKET_AFTER_RUNTIME_PROVENANCE_INDEX_2026-05-31.md`

Reviewers may use this combined packet instead of reading those three handoffs
separately.

## Work Under Review

### Goal2889

Goal2889 addresses Claude Goal2886's "parallel attestation" concern. The actual
bounded Triton torch-carrier `_torch_as(...)` conversions for typed payload gather
are now wrapped under neutral-buffer seam leases.

Inspect:

- `src/rtdsl/hit_stream_handoff.py`
- `tests/goal2889_torch_carrier_copy_decision_seam_lease_wrap_test.py`
- `docs/reports/goal2889_torch_carrier_copy_decision_seam_lease_wrap_2026-05-31.md`

### Goal2891

Goal2891 indexes the Goal2883/Goal2889 runtime provenance inside
`partner_conformance_snapshot` using explicit `*_indexed` fields so the readiness
packet remains an evidence index, not a fresh runtime measurement or release
claim.

Inspect:

- `src/rtdsl/v2_5_internal_readiness.py`
- `tests/goal2891_runtime_provenance_index_in_conformance_snapshot_test.py`
- `docs/reports/goal2891_runtime_provenance_index_in_conformance_snapshot_2026-05-31.md`

### Goal2893

Goal2893 reruns the seven-app canonical packet on the RTX A5000 pod after the
runtime-provenance index work and updates readiness to point at the current clean
packet.

Inspect:

- `tests/goal2893_current_packet_after_runtime_provenance_index_test.py`
- `docs/reports/goal2893_current_packet_after_runtime_provenance_index_2026-05-31.md`
- `docs/reports/goal2893_current_packet_after_runtime_provenance_index_pod/goal2855_summary.json`
- `docs/reports/goal2893_current_packet_after_runtime_provenance_index_pod/*.json`

## Review Questions

1. Does Goal2889 route the actual bounded torch-carrier copy decision through
   neutral seam leases, or is any important part still merely parallel
   attestation?
2. Does Goal2891 correctly index runtime provenance without pretending the
   readiness packet itself performed a fresh runtime measurement?
3. Are the `*_indexed` fields precise enough to avoid zero-copy or release
   overclaiming?
4. Does Goal2893 prove the current seven-app canonical packet is clean:
   `all_pass: true`, 7/7 artifacts, empty `source_dirty`, empty
   `dirty_artifacts`, and empty `claim_boundary_violations`?
5. Does the entire chain preserve all blocked actions: no v2.5 release
   authorization, no public/whole-app/broad-RT-core speedup claim, no
   true-zero-copy claim, no automatic Triton preview selection, no
   paper-reproduction claim, and no app-specific native engine behavior?
6. What residual release-watch items remain before any explicit v2.5 release
   packet could be considered?

## Validation Already Run

Goal2889 local focused validation:

```text
Ran 20 tests in 0.780s

OK (skipped=2)
```

Goal2889 pod focused validation:

```text
Ran 20 tests in 1.804s

OK
```

Goal2891 local focused validation:

```text
Ran 19 tests in 1.071s

OK (skipped=1)
```

Goal2891 pod focused validation:

```text
Ran 19 tests in 1.829s

OK
```

Goal2893 local focused validation:

```text
Ran 13 tests in 0.728s

OK
```

Goal2893 pod focused validation:

```text
Ran 13 tests in 0.357s

OK
```

Goal2893 seven-app pod packet:

```text
status: pass
all_pass: true
artifact_count: 7
expected_artifact_count: 7
source_dirty: []
dirty_artifacts: {}
claim_boundary_violations: {}
source_commit: e6bf7f85cb8a32e5cd5c32210f192a15207e2184
gpu: NVIDIA RTX A5000, 570.211.01
```

## Important Non-Scope

This review is about v2.5 internal readiness hardening only. It should not
evaluate or admit the separate v3.0 exploratory vision unless explicitly asked.
The v3.0 vision currently has known wording hazards around "default Triton,"
"zero-cost," and "zero-copy boundary"; those must not leak into this v2.5 review.

## Expected Review Output

Write the review to:

- `docs/reviews/goal2895_<reviewer>_review_combined_runtime_provenance_and_packet_refresh_2026-05-31.md`

Use one of the established verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This review must not authorize a v2.5 release by itself. Any v2.5 release still
requires an explicit user-requested release packet and fresh 3-AI consensus.
