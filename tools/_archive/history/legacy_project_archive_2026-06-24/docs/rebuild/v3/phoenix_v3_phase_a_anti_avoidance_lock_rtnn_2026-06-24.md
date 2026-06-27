# Phoenix V3 Phase A Anti-Avoidance Lock: RTNN

Date: 2026-06-24
Status: `phase_a_candidate_lock_before_second_family_execution`

This file is not a review packet, release packet, or new milestone. It is the
mandatory lock required by Claude's Goal 0 verdict before any second-family
execution. If this lock fails in measurement, Phase A exits to Phase H
capability/quality release rather than searching for a third winner.

## Goal-Level Decision Audit

Decision: select RTNN fixed-radius ranked-summary as the only remaining Phase A
performance-source candidate after Barnes-Hut was locked as trunk proof/control.

1. Was I foolish? Not yet. The decision rejects more Barnes-Hut tuning and does
   not treat RTNN's old repeat50 wall win as proof.
2. If yes, what actions made the decision foolish? It would be foolish to run
   RTNN without measuring per-distribution phase dominance, or to count
   input-load/packing consolidation as a V3 runtime speedup.
3. Was there another path? RayJoin and RTDBSCAN already have no-go/near-parity
   focused evidence; RayDB is Set-B/control; Triangle is already a closed
   focused win, not the current blocker-moving experiment.
4. Can I now try a different path that actually solves the problem? Yes: run a
   focused RTNN phase-bound experiment, then either execute the single
   reselected-family performance test or enter Phase H.

## Claude Lock (a)-(d)

(a) Family name:

- `fixed_radius_ranked_summary_3d_prepared_session`
- Pressure app: `rtnn`
- Productized route: `prepared_execution_ranked_summary`
- Same-contract incumbent route: `prepared_optix_ranked_summary`

(b) Dominant end-to-end phase by measured fraction of wall time:

- Existing measured evidence is uniform-only repeat50:
  - input load/pack share of delta: `0.323`
  - runner-after-input-pack share of delta: `0.677`
  - execution prepare delta: `0.357405s`
  - hot-query boundary: `0.988781x`
- This is insufficient for clustered/shell. The next allowed action is a
  focused per-distribution phase-bound run for the frozen scorecard shapes.

(c) Concrete >=1.20x runtime-sourced hypothesis:

- The hypothesis is not hot-query acceleration. It is that the V3 prepared
  execution/session runner removes repeated prepare/session and runner-after-pack
  overhead for full-batch self-query ranked-summary shapes while preserving
  correctness parity and avoiding hot-path host materialization.
- To remain valid, the per-distribution phase-bound run must show a dominant
  removable phase outside input-load/packing alone, and the focused result must
  project at least one frozen RTNN OptiX scorecard row to `>=1.20x` with
  `parity_pass: true`.

(d) Why V2.14 lacks it:

- V2.14 exposes the legacy app-front-door prepared OptiX ranked-summary route.
  It does not have the Phoenix V3 productized prepared-session runner metadata,
  fail-closed residency accounting, repeat-session execution contract, or the
  single runtime path now used by `run_fixed_radius_ranked_summary_3d_prepared_session`.

## Kill Conditions

- If per-distribution phase rows show the candidate is hot-query/backend-bound,
  stop and enter Phase H.
- If the positive delta is only input-load/packing consolidation, stop and enter
  Phase H.
- If the focused scorecard-bound RTNN run misses `>=1.20x` runtime-sourced
  movement with parity, stop and enter Phase H.
- No third search is authorized by this lock.

## Non-Authorization

No V3 release, no all-app benchmark, no public speedup wording, no broad
V3-over-V2 wording, no V4, no embedding, no C ABI, no external zero-copy claim.
