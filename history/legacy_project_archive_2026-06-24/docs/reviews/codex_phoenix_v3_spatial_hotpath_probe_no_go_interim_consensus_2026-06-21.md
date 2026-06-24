# Codex Interim Consensus: Phoenix V3 Spatial Hotpath Probe No-Go

Status: `codex_interim_consensus_spatial_hotpath_no_go_external_ai_blocked`.

This is not a completed 2-AI consensus. Claude and Gemini attempts are recorded
but did not produce a valid external verdict:

- `docs/reviews/claude_phoenix_v3_spatial_hotpath_probe_no_go_review_2026-06-21.md`
- `docs/reviews/gemini_phoenix_v3_spatial_hotpath_probe_no_go_review_attempt_2026-06-21.md`
- `docs/reviews/external_ai_blocked_phoenix_v3_spatial_hotpath_probe_no_go_2026-06-21.md`

## Codex Verdict

`approve-no-go-interim`

The current Spatial RayJoin point-location topology-stream route should remain
out of Phoenix V3 M7 release coverage.

## Basis

- Fresh POD sweep was run on `NVIDIA RTX 4000 Ada Generation, 550.127.05`.
- Dataset was `data/rayjoin_public_cdb/br_county.cdb`.
- Exact authority count was `47,262`.
- Best legal RTDL route was
  `relation_status_corrected_executor_validated` with point order `y_then_x`.
- Best legal RTDL hot query was `5.406518 ms`.
- Same-dataset RayJoin author Query timer remains `1.865660 ms`.
- RayJoin author is therefore `2.898x` faster than the best legal RTDL route in
  this packet.
- `device_filtered_prepared_points_validated` is excluded because it reports
  `47,570` instead of exact `47,262`.

## Consequence

The V3 release-surface breadth gate should continue to treat
`point_location_topology_stream` as missing. This packet improves honesty and
prevents repeated Spatial retesting, but it adds zero M7 rows and authorizes no
public speedup claim.

## Required Follow-Up

Re-run Claude after its stated reset time or use another external AI. Until then,
this packet is Codex-reviewed but not 2-AI complete.

## Goal-Level Decision Self-Audit

Decision: keep Spatial RayJoin point-location topology stream as no-go after
fresh same-POD hotpath probe.

1. Was I foolish?
   No. The decision is based on same-dataset POD evidence, exact row-count
   authority, and explicit failure fencing.
2. If yes, what actions made the decision foolish?
   The foolish action would have been to call `5.406518 ms` good enough against
   `1.865660 ms`, or to hide the `47,570 != 47,262` mismatch.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. We could have skipped Spatial immediately and moved to another generic
   engine family, but this gap had a concrete reopen bar and deserved one
   bounded probe.
4. Can I now try a different path that actually solves the problem?
   Yes. Treat Spatial as future research unless a real generic traversal
   optimization is designed; for Phoenix V3, move to the next generic engine
   target rather than app-specific Spatial tuning.
