# Codex + Antigravity 2-AI Consensus: Phoenix V3 M43 Grouped Reduction CuPy Warp Prepared Runner

Date: 2026-06-23

Status: `m43_step2_grouped_reduction_closed_continue_step2_scorecard_sync`

## Inputs

- Call for review:
  `docs/reviews/call_for_review_phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md`
- M43 report:
  `docs/reports/phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md`
- Antigravity external review, GUI-provided by the user:
  `docs/reviews/antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_review_2026-06-23.md`
- Main evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_original_262144x1024_20260623_153707/summary.json`
- Trusted-offset follow-up evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_trust_offsets_262144x1024_20260623_154342/summary.json`
- Full local rebuild evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m43_trust_offsets_followup_20260623_154700.json`

## External Verdict

Antigravity verdict:

```text
accept_m43_original_shape_hot_gate_cleared_continue_step2
```

Antigravity explicitly answered that M43 is generic runtime work rather than
application-specific tuning, preserves explicit partner choice, clears the
original `262144 x 1024` CPU-hot inversion with the productized CuPy prepared
runner, fairly identifies the inclusive-wall caveat as row-offset validation
overhead, accepts explicit `--trust-row-offsets` as a prevalidated-data mode,
and preserves all non-authorization boundaries.

## Codex Review

Codex agrees with the Antigravity verdict.

The critical facts are:

- The Numba tiled attempts were useful diagnostics but did not clear the
  original CPU-hot gate:
  - block-per-group tiled: `0.6216966017370773x` runner vs CPU hot
  - warp-per-group tiled: `0.6777200472439239x` runner vs CPU hot
- The productized CuPy RawKernel warp prepared-session route clears the
  original blocked shape:
  - failed checks: `0`
  - correctness: `allclose=true`
  - actual output partner: `cupy`
  - runtime trunk executes end-to-end: `true`
  - internal device residency between RTDL phases: `true`
  - hot-path host materialization: `false`
  - kernel strategy: `warp_per_group_tiled`
  - program count: `128`
  - runner vs CPU hot: `3.454249350723889x`
  - runner vs legacy hot: `6.670789510185146x`
- The trusted-offset follow-up clears the inclusive-wall caveat for explicit
  prevalidated/generated row offsets:
  - failed checks: `0`
  - runner vs CPU hot: `3.634392783864349x`
  - runner vs legacy hot: `3.3163301846618403x`
  - runner vs legacy wall: `15.409127696720203x`
- Full local V3 rebuild after M43 passed: `120` modules / `627` tests.

Codex also agrees that the CuPy path is acceptable as V3 runtime work because
it is routed through the prepared-session runner and explicit partner selection,
not as a one-off app route or hidden automatic backend claim.

## Consensus Verdict

Consensus verdict:

```text
accept_m43_original_shape_hot_gate_cleared_continue_step2
```

M43 closes grouped reduction as the second Step-2 family for local/runtime-trunk
evidence. The result is sufficient to move from M43 implementation into Step-2
scorecard synchronization and next-family planning.

## Authorized Next Work

Authorized:

- Mark M43 grouped-reduction Step-2 technical closure as accepted.
- Sync the Phoenix V3 Set-A/Set-B focused evidence ledger and scorecard with:
  - M40 component-union focused POD result
  - M42 grouped-reduction shape-positive diagnostic
  - M43 grouped-reduction original-shape CuPy prepared-runner result
- Decide the next Step-2 action from the synchronized scorecard:
  - either select a third family for the same runtime-trunk discipline; or
  - prepare a bounded review packet asking whether current Step-2 evidence is
    sufficient to consider the first serious all-app protocol gate.
- Continue only generic runtime-trunk work, not app-specific route polishing.

## Non-Authorization

This consensus does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- public speedup wording
- broad V3-over-V2 claim
- V4 work
- embedding
- C ABI
- true zero-copy claim

Any move to all-app POD or release-level wording still requires a separate
bounded review packet and explicit external authorization.

## Goal-Level Decision Audit

Decision: accept the user-provided Antigravity GUI review as the external-AI
side of bounded M43 technical closure, while preserving all release and spending
blocks.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish alternative
   would have been to ignore a substantive external review solely because the
   headless Antigravity API was unavailable, or to inflate this bounded review
   into release authorization.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Wait for Claude reset. That remains available as a later superseding
   check, but it is not necessary to keep local V3 Step-2 work moving after the
   user supplied a substantive external review.
4. Can I now try a different path that actually solves the problem? Yes. The
   next path is scorecard synchronization and next-family planning under the
   same runtime-trunk discipline, with no all-app or paid-POD move until a
   separate review authorizes it.
