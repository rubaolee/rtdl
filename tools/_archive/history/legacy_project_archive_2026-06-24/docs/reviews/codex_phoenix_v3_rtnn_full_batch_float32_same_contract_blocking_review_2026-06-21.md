# Codex Blocking Review: Phoenix V3 RTNN Full-Batch Float32 Same-Contract Evidence

Reviewer: Codex  
Date: 2026-06-21  
Scope: V3 only

## Verdict

`approve-as-prepared-hot-query-intake`

The RTNN full-batch float32 same-contract packet is useful generic
`ranked_summary` evidence, but it must remain not-M7. It is not an end-to-end
RTNN win and not a public V3 speedup claim.

## Findings

### P0 - External review is blocked

The required external AI side of 2-AI consensus is absent for the full-batch
float32 packet. Gemini failed authentication, Claude Code was unavailable in
the checked environments, and no external review verdict exists.

### P0 - Wall and runner comparisons regress

The main 1,048,576-point repeat5 packet shows a real prepared-hot-query
advantage, but the user-visible walls regress:

- prepared hot-query: `7.790x` RTDL OptiX over CuPy grid;
- cold-plus-query wall: `0.393x`;
- runner wall: `0.627x`.

This blocks end-to-end, whole-app, and broad V3-over-V2 wording.

### P1 - Prepared-hot-query M7 scope is not yet reviewed

The row may be reviewable only as a narrow prepared-hot-query candidate after
data are loaded, packed, and the OptiX plan is prepared. That scope still needs
external review, Codex consensus, and wording that prevents users from reading
it as an RTNN product win.

### P1 - Exactness and precision boundary must stay visible

The OptiX route is float32 and `exact=false`; the CuPy grid is the
same-contract reference but is exact. Integer signatures match and
sum-distance relative error is small, but this cannot become a universal
nearest-neighbor claim.

## What Is Approved

- Keep the packet as serious RTNN `ranked_summary` intake evidence.
- Preserve the `7.790x` prepared-hot-query result as an internal V3 engine
  signal.
- Keep the next work focused on pack/prepare amortization or a stricter
  exact/tie-stable route.

## What Is Not Approved

- M7 promotion.
- End-to-end or wall-clock RTNN speedup wording.
- Whole-app RTNN wording.
- Paper reproduction wording.
- Broad V3-over-V2 wording.
- Universal nearest-neighbor wording.

## Recommended Next Action

Add a machine-readable review gate that records RTNN full-batch float32 as
`review_blocked_not_m7`, updates the queue to show this as blocked rather than
pending, and directs future work toward pack/prepare amortization or exact
tie-stable parity before any future M7 review.

## Goal-Level Decision Self-Audit

Decision: approve the RTNN full-batch float32 packet as prepared-hot-query
intake only, and block M7 reopening until external review and wall/scope gates
are handled.

1. Was I foolish?
   No. The packet has a real hot-query signal, but the wall regression and
   missing external review make promotion unsafe.
2. If yes, what actions made the decision foolish?
   The foolish action would be to market `7.790x` while hiding `0.393x` and
   `0.627x`.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. I could reject RTNN completely because wall loses, but that would erase
   useful generic `ranked_summary` evidence.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep this row review-blocked/not-M7 and work on pack/prepare
   amortization or exact/tie-stable parity instead of promoting a hot-only row.
