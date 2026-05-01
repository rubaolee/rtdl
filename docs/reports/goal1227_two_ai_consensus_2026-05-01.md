# Goal1227 Two-AI Consensus

Date: 2026-05-01

## Scope

Goal1227 provides the formal architectural roadmap design for RTDL v1.0, v1.5, and v2.0.

## Inputs

- Codex Formal Design: `docs/reports/goal1227_formal_v1_0_v1_5_v2_0_roadmap_design_2026-05-01.md`
- Gemini Formal Review: `docs/reports/goal1227_gemini_formal_roadmap_design_review_2026-05-01.md`

## Consensus Verdict

`ACCEPT`

Codex and Gemini explicitly accept the Formal Roadmap Design.
- v1.0 remains the app-credibility and golden-reference baseline with strictly bounded public claims.
- v1.5 is the technical-debt reduction phase, relying on the refined minimal
  generic primitive set: `ANY_HIT`, `COUNT_HITS`,
  `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`, with
  `COLLECT_K_BOUNDED` experimental only after scalar primitives are stable.
- v1.5 migration rules correctly demand performance parity and exact integer bit-parity, but wisely allow explicit tolerances for floating-point reductions across heterogeneous accelerators.
- v2.0 strictly targets explicit compute partnership (via DLPack/zero-copy) and firmly rejects the "magic Python compiler" anti-pattern.
- No statement in the roadmap overclaims RT-core or whole-app acceleration.

## Boundary

This consensus formally locks in the architectural intent for the v1.0 -> v1.5
-> v2.0 transition. It is a planning consensus only. It does not authorize v1.5
native code refactoring yet; before implementation, RTDL still needs the
primitive ABI contract and per-app lowering matrix called for by Goal1042 and
Goal1227. The immediate work remains v1.0 stabilization first.
