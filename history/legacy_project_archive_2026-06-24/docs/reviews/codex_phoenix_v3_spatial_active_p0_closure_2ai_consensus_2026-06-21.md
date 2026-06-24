# Codex Consensus: Phoenix V3 Spatial Active-P0 Closure

Date: 2026-06-21

Status: `claude_codex_consensus_complete_close_active_p0_future_research`

External review:

- `docs/reviews/claude_phoenix_v3_spatial_active_p0_closure_review_2026-06-21.md`
- Claude verdict: `close-active-p0`

## Consensus Decision

Codex agrees with Claude: close
`spatial_rayjoin_topology_stream_author_gap` as an active Phoenix V3 P0 item and
move it to future research / no-current-M7 status.

This is not a release approval. It does not authorize M7 promotion, RTDL-beats-
RayJoin wording, true zero-copy wording, RayJoin-paper wording, whole Spatial
RayJoin wording, broad V3-over-V2 wording, or a V3 release declaration.

## Why Closure Is Correct

The exact-f64 device scalar-count repair is real generic-engine progress, but it
does not produce a user-responsible V3 performance row.

The accepted record is:

- RTDL exact-f64 prepared-query median: `6.309319 ms`.
- Prior RTDL exact executor median: `23.217812 ms`.
- RTDL-vs-prior-RTDL prepared-query improvement: `3.680x`.
- Same-dataset RayJoin author Query timer: `1.865660 ms`.
- RayJoin author Query is `3.382x` faster than current RTDL exact-f64.
- Same-dataset RayJoin author result count was not printed, so author count
  parity remains unverified.
- Exact public-county RTDL count is stable at `47,262`.
- Adverse-subset parity passes only at row_count `6`; it closes a blocker but
  does not prove M7.
- The relation-status corrected route remains a no-go at `47,259 != 47,262`.
- The remaining bottleneck is the exact/topology device predicate over AABB
  candidates, accounting for `99.663%` of exact-f64 prepared-query median.

Keeping this row active P0 would keep V3 chasing an unbounded Spatial route while
the current evidence still says no M7 row and no RTDL-over-RayJoin claim. Closing
it as future research is more honest for users and lets Phoenix V3 focus on the
bounded eleven-row release surface and the remaining release blockers.

## Machine-Recorded Reopen Conditions

Spatial may be reopened for current V3 only if one of these happens:

- A fresh same-dataset POD packet on `br_county.cdb` proves RTDL prepared-query
  median below `1.865660 ms` with stable margin, stable exact count `47,262`,
  full M3 phase table, and same-packet author timing/count evidence.
- Or a real external AI reviewer explicitly accepts a weaker scoped claim, with
  rationale, followed by Codex consensus.

Any reopened path must keep all release, M7, RTDL-beats-RayJoin, external
zero-copy interop, RayJoin-paper, whole-app, and broad V3-over-V2 claim flags
false until a new reviewed packet says otherwise.

## Goal-Level Decision Self-Audit

Decision: close Spatial active P0 for current Phoenix V3 and move it to future
research.

1. Was I foolish? No. The closure follows a real Claude external verdict plus a
   current evidence record that does not support M7 or RTDL-beats-RayJoin.
2. If yes, what actions made the decision foolish? The foolish action would be
   to hide the 3.382x RayJoin author gap, treat the RTDL-vs-RTDL 3.680x repair
   as public victory, or keep an unbounded P0 open because the internal work is
   interesting.
3. Was there another path? Yes. Continue optimizing Spatial first. That path is
   technically possible, but it would not be user-responsible for the current V3
   release surface without a numeric route to beat the author timer.
4. Can I now try a different path that actually solves the problem? Yes. Close
   Spatial as future research, make the no-claim boundary machine-readable, and
   move Phoenix V3 to remaining release-readiness blockers: package/setup
   reproducibility, second RTX confirmation or scoped waiver, and final public
   docs/release review.
