# Phoenix V3 Spatial Count-Only/No-Diagnostics No-Go

Status: `spatial_relation_status_count_only_no_diagnostics_no_go_not_m7`.

This packet closes a focused follow-up to the Spatial relation-status
prefilter-zero near-miss. Removing diagnostic atomics from the exact
scalar-count hot path preserved the count but did not improve the stable
prepared-query median, so the code path was removed.

```text
release_authorized: false
public_speedup_claim_authorized: false
rtdl_beats_rayjoin_claim_authorized: false
m7_promotion_authorized: false
M7 rows added: 0
```

## Result

- Diagnostic prefilter-zero median: `1.897592 ms`
- Count-only/no-diagnostics median: `1.903873 ms`
- Delta count-only minus diagnostic: `0.006281 ms`
- Count-only faster: `false`
- Count-only preserved exact count: `true`
- Count-only gap to author Query: `0.038213 ms`
- Count-only source retained: `false`

## Evidence

- Diagnostic packet: `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_count_only_no_diag_20260621/diagnostic_prefilter_zero_repeat50_sample7.json`
- Count-only packet: `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_count_only_no_diag_20260621/count_only_prefilter_zero_repeat50_sample7.json`
- Dataset: `data/rayjoin_public_cdb/br_county.cdb`

## Provenance Limitation

- POD evidence git commit: `None`
- Reason: The POD measurement source copy at /root/rtdl_v3_rebuild_20260620/current was not a git checkout, so the runner recorded git_commit as null.
- Mitigation: The no-go packet records the exact copied evidence files, GPU identity, remote source path, live current-source absence of the failed flag, and tests that rebuild the packet from those evidence files.
- Future requirement: Future POD evidence packets should include a git commit or explicit source_manifest.sha256 for the measured source tree.

## Required Next Actions

- Do not reintroduce the count-only/no-diagnostics flag without new evidence.
- Do not promote Spatial topology-stream to M7 from this packet.
- Continue only with correctness-preserving generic optimizations that can beat the 1.865660 ms author Query bar with stable margin.

## Goal-Level Decision Audit

Decision: Reject and remove the count-only/no-diagnostics Spatial hot-path candidate.

1. Was I foolish? No in the final decision: the evidence shows the candidate is slower, so rejecting it is the responsible move.
2. If yes, what actions made the decision foolish? The foolish action would be to keep a default-off code path just because it sounded plausible, or to rerun it repeatedly after a clean paired test showed no benefit.
3. Was there another path? Leave it in source as an experimental flag. That would increase surface area without helping V3 performance.
4. Can I now try a different path? Record the no-go, keep the correct prefilter-zero near-miss, and move to another generic topology-stream bottleneck.
