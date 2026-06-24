# Codex 2-AI Consensus: Phoenix V3 Spatial Count-Only/No-Diagnostics No-Go

Status: `codex_claude_consensus_accept_no_go_not_release`.

This consensus closes only the bounded count-only/no-diagnostics follow-up to
the Spatial relation-status prefilter-zero near-miss.

## Inputs

- Call for review:
  `docs/reviews/call_for_review_phoenix_v3_spatial_count_only_no_diagnostics_no_go_2026-06-21.md`
- Claude review:
  `docs/reviews/claude_phoenix_v3_spatial_count_only_no_diagnostics_no_go_review_2026-06-21.md`
- No-go packet:
  `docs/rebuild/v3/phoenix_v3_spatial_relation_status_count_only_no_diagnostics_no_go_2026-06-21.md`
- Evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_count_only_no_diag_20260621/`

## Verdict

Accept the no-go decision.

Claude's verdict is `accept`: the count-only/no-diagnostics variant preserved
the exact public-county count `47,262`, but it was slower in all seven paired
samples and had worse median timing than the diagnostic prefilter-zero route.

```text
diagnostic prefilter-zero median: 1.8975920975208282 ms
count-only/no-diagnostics median: 1.903872936964035 ms
delta count-only minus diagnostic: +0.006280839443206787 ms
RayJoin author Query bar: 1.865660 ms
```

Codex agrees. The experimental flag was removed from
`src/native/optix/rtdl_optix_workloads.cpp`; the no-go packet and tests now
verify that the failed flag is absent and that the surviving
`RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO` near-miss remains the
only related source flag.

## P1 Handling

Claude's only P1 finding was that the two raw POD evidence packets record
`git_commit: null`. Codex accepts the finding. The measured remote source copy
was `/root/rtdl_v3_rebuild_20260620/current`, which is not a git checkout, so a
commit hash cannot be reconstructed honestly.

The no-go packet now records this explicitly under `provenance_limitations`,
including:

- `pod_evidence_git_commit: null`;
- reason: the POD measurement source copy was not a git checkout;
- mitigation: exact copied evidence files, GPU identity, remote source path,
  live current-source flag absence, and rebuild tests;
- future requirement: include a git commit or `source_manifest.sha256` for
  measured source trees.

This resolves the P1 for closure of this no-go record. It does not upgrade the
candidate to M7.

## Claim Boundary

```text
release_authorized: false
public_speedup_claim_authorized: false
row_scoped_public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
rtdl_beats_rayjoin_claim_authorized: false
true_zero_copy_claim_authorized: false
v4_embedding_claim_authorized: false
m7_promotion_authorized: false
M7 rows added: 0
```

## Decision Audit

1. Was I foolish?
   No for the final decision. The candidate was tested on the same serious
   public-county route, rejected because it was consistently slower, and removed
   from source.
2. If yes, what actions made the decision foolish?
   The risky action would have been to keep a dead default-off flag or to keep
   rerunning a consistently slower route because it sounded plausible.
3. Was there another path?
   Yes. Leaving the candidate undocumented would have saved time but invited a
   future repeat of the same experiment.
4. Can I now try a different path?
   Yes. Keep this no-go closed, retain the correct prefilter-zero near-miss as
   future research, and only reopen Spatial when a generic topology-stream
   route beats the `1.865660 ms` author bar with stable margin or receives a
   new scoped external-review decision.
