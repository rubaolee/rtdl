# Codex 2-AI Consensus: Phoenix V3 M4 Grouped-Continuation Evidence

Date: 2026-06-20

Status: bounded M4 grouped-continuation evidence closed as internal Phoenix V3
evidence only.

This is not V3 release authorization, not M7 row qualification, and not public
speedup or zero-copy wording.

## Inputs

External review:

```text
docs/reviews/claude_phoenix_v3_m4_final_evidence_review_2026-06-20.md
verdict: ACCEPT_WITH_REQUIRED_AMENDMENTS
```

Primary evidence:

```text
docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_pod_evidence_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/phoenix_v3_m4_evidence_index_2026-06-20.json
docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/m23_dbscan_component_signature_524288.json
```

Supporting tests:

```text
tests/v3_phoenix_m4_grouped_continuation_evidence_test.py
tests/v3_phoenix_m4_grouped_continuation_packet_test.py
tests/goal4420_v3_0_m23_dbscan_component_bridge_test.py
```

## Claude Required Amendments

Claude required five amendments before closure:

1. Label M10 as a non-clean pass with `accounting_warning_count=1` and
   `true_zero_copy_ready=false`.
2. Record system `python3` missing CuPy/Numba as an open packaging gap with
   owner and target milestone.
3. Confirm all M9/M10/M11/M18/M23/M28 rows carry false public/release claim
   flags in machine-readable metadata.
4. Attach `source_manifest.sha256` and `no_git_worktree` source identity to
   each module result record.
5. State that M28 same-contract ratios are internal CPU-reference comparisons
   only and must not be cited as cross-backend speedup until M7 qualification.

Codex verified these amendments are present in the evidence report, evidence
index, and tests.

## M23 RTDBSCAN Component-Union Evidence

The M23 RTDBSCAN row is accepted as internal evidence for the generic
component-union / component-signature capability:

```text
artifact: m23_dbscan_component_signature_524288.json
copies: 65536
point_count: 524288
partners: cupy, numba
output_mode: component_signature
native_continuation_active: true
rt_core_accelerated: true
all_match_oracle: true
cluster_size_signatures_match: true
public_claim_authorized: false
```

The accepted interpretation is narrow:

```text
RTDL can produce a compact device-side component signature for this generated
DBSCAN-shaped workload through the generic prepared fixed-radius grouped-union
contract, with CuPy and Numba partner aggregation agreeing with the oracle.
```

Forbidden interpretations:

```text
V3 is release-ready.
V3 has a public RTDBSCAN speedup claim.
V3 has true zero-copy product authorization.
RTDL provides a DBSCAN-specific native engine ABI.
Automatic partner selection is authorized.
```

## Codex Consensus

Codex agrees with Claude's post-amendment verdict.

M4 may be closed as internal grouped-continuation evidence because:

- M9 proves grouped-stream partner viability at 65,536 points;
- M10 proves same-stream evidence only as a non-clean internal pass with an
  accounting warning;
- M11 proves a measured no-hidden-column-copy window, without public zero-copy
  wording;
- M18 proves a device-side grouped contract at 65,536 rays / 1,024 groups;
- M23 proves RTDBSCAN-style component-signature reuse at 524,288 points;
- M28 proves non-DBSCAN grouped-reduction reuse, with a separate focused
  RayDB M28 closure now saved;
- all rows keep release/public/M7 flags false;
- the system-Python packaging gap is explicit and remains open before M7.

## Closure Boundary

This bounded M4 goal is closed only at this level:

```text
internal grouped-continuation evidence: accepted
internal RTDBSCAN component-signature evidence: accepted
M10 clean pass: no
M7-qualified release row: no
V3 release authorization: no
public speedup wording: no
public zero-copy wording: no
whole-app DBSCAN claim: no
Phoenix M7-qualified release rows: 0
```

Future work may promote selected M4 rows into a Phoenix M7 packet only after
M7 supplies exact row selection, dataset, phase accounting, packaging closure or
waiver, and fresh row-level release review.

## Verified Commands

Current verification after RayDB/M4 documentation updates:

```text
py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []
release_authorized: false
public_speedup_claim_authorized: false
```

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 20
Ran 71 tests
OK
```

The local Python installation prints `Could not find platform independent
libraries <prefix>` before these runs, but the commands return success and the
test bodies pass.

## Goal-Level Decision Audit

Decision: close M4 as internal grouped-continuation evidence and use M23 as the
RTDBSCAN/component-union internal evidence point.

1. Was I foolish?

   The corrected decision is not foolish. It uses the existing Claude final
   review and closes the missing Codex side without relabeling internal data as
   release evidence.

2. If yes, what actions made the decision foolish?

   The foolish risk would be treating the M4 Claude review as full closure
   without writing this Codex consensus, or treating M23 as a public RTDBSCAN
   speedup result.

3. Was there another path?

   Yes. I could have rerun M23 on the pod immediately, but the existing
   524,288-point artifact is already serious and the missing item was closure
   discipline.

4. Can I now try a different path that actually solves the problem?

   Yes. The path is to close internal M4 honestly, keep M7/release blocked, and
   then move to the next generic capability gap instead of repeating an already
   valid M23 pod run.
