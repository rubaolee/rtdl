# Goal2850 Consensus: Goal2849 v2.5 Readiness Indexes Current Canonical Harness

Date: 2026-05-31

Consensus verdict: **accept-with-boundary**

Participants:

- Codex: implemented Goal2849 readiness-index refresh.
- Gemini: independent external review in
  `docs/reviews/goal2850_gemini_review_goal2849_v2_5_readiness_current_canonical_harness_2026-05-31.md`.

## Accepted Scope

Goal2849 is accepted as an internal readiness-index refresh. It adds the
Goal2847 current canonical harness packet and the Goal2848 review/consensus
artifacts to `rt.v2_5_internal_readiness_packet(...)`.

The accepted evidence is limited to:

- confirming the Goal2847 report and Goal2848 consensus/review paths exist,
- indexing the Goal2847 summary JSON,
- indexing the seven canonical v2.5 harness JSON artifacts,
- validating that those artifacts passed on the RTX A5000 pod with
  `source_dirty: []`.

## Boundary

This consensus does not authorize:

- v2.5 release,
- release tag action,
- public speedup wording,
- broad RT-core wording,
- whole-app speedup wording,
- true-zero-copy wording,
- package-install wording,
- Triton preview auto-selection.

Both Codex and Gemini agree the packet remains bounded by the Goal2847 weak
spots: RTNN distribution dependence, Hausdorff slower than the optimized CuPy
grid baseline, Barnes-Hut Triton vector sum not promoted, and Barnes-Hut long
CPU-heavy comparison windows needing better progress logging.

## Final Position

Goal2849 can be used as machine-readable readiness tracking for the latest
canonical pod harness packet. It is not final v2.5 release consensus.
