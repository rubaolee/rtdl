# Codex Provisional Review: Phoenix V3 M43 Grouped Reduction CuPy Warp

Date: 2026-06-23

Provisional Codex verdict: `accept_m43_hot_gate_cleared_but_external_review_pending`

This is not a 2-AI consensus record. External review is blocked by current Claude/Gemini/Antigravity availability and must be retried before M43 can close under the project rule.

## Findings

P0: No release, all-app, or paid-POD action is authorized. M43 is local evidence only.

P1: The original M41 CPU-hot inversion is cleared for the explicit CuPy partner route:

- evidence: `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_original_262144x1024_20260623_153707/summary.json`
- failed checks: `0`
- runtime trunk executes end-to-end: `true`
- internal device residency between RTDL phases: `true`
- hot-path host materialization: `false`
- productized runner hot: `0.00004867999814450741 s`
- CPU hot: `0.00016815285198390484 s`
- runner vs CPU hot: `3.454249350723889x`

P1: Inclusive wall initially needed follow-up before broader interpretation:

- runner vs legacy wall: `0.8786019925331072x`
- follow-up evidence with explicit trusted row offsets:
  `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_trust_offsets_262144x1024_20260623_154342/summary.json`
- trusted-offset follow-up runner vs legacy wall:
  `15.409127696720203x`
- interpretation: the first wall regression was prepare validation overhead, not hot-path failure

P2: The Numba tiled attempts should remain recorded as negative/insufficient evidence, not erased:

- block-per-group tiled runner vs CPU hot: `0.6216966017370773x`
- warp-per-group tiled runner vs CPU hot: `0.6777200472439239x`
- CuPy RawKernel prepared route is the path that clears the gate

## Next Local Work While External Review Is Blocked

Allowed:

- further local wall-followup for the same CuPy prepared route if needed by review
- reduce avoidable prepare/warmup overhead if it is generic runtime work
- document repeat/amortization behavior without public claims

Not allowed:

- paid POD
- all-app
- release decision
- public speedup wording
- broad V3-over-V2 claim
- V4 / embedding / C ABI / true zero-copy

## Goal-Level Decision Audit

Decision: continue local follow-up while external M43 review is blocked; do not close M43 as 2-AI consensus.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? It would be foolish to wait idly for Claude's reset or to pretend Gemini/Antigravity failures count as review.
3. Was there another path that would avoid being stuck? Yes. Record the blocked review state and continue bounded local work that does not require external authorization.
4. Can I now try a different path that actually solves the problem? Yes. The local wall caveat now has trusted-offset evidence; retry Claude when the session limit resets.

## Non-Authorization

This provisional review does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- public speedup wording
- broad V3-over-V2 claim
- V4 work
- embedding
- C ABI
- true zero-copy claim
