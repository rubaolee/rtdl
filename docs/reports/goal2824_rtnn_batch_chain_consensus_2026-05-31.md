# Goal2824 RTNN Batch Chain Consensus

Date: 2026-05-31

Verdict: Codex + Gemini consensus accepts Goal2821-Goal2823 with boundary.

## Scope

Goal2824 records consensus for the RTNN v2.5 batch-optimization chain:

- Goal2821: heterogeneous prepared-aggregate batch requests.
- Goal2822: fused 2D-grid block-partial batch kernel.
- Goal2823: device-side partial-reduce negative probe, reverted as default.

## Independent Review

Gemini independently reviewed the chain in:

`docs/reviews/goal2824_gemini_review_rtnn_batch_chain_2821_2823_2026-05-31.md`

Gemini verdict: `accept-with-boundary`.

The review confirms:

- Goal2821/Goal2822 are valid generic v2.5 runtime hardening steps.
- Goal2823's `reject-as-default` decision is correct given mixed evidence.
- Current main keeps the Goal2822 fused batch path, not the Goal2823
  device-side reducer.
- Performance comparisons are narrowly stated as internal amortization evidence.
- Public speedup, paper reproduction, whole-app speedup, and release claims
  remain unauthorized.

## Consensus Position

Codex and Gemini agree:

| Goal | Consensus | Reason |
| --- | --- | --- |
| Goal2821 | accept-with-boundary | Heterogeneous radius/`k_max` sweeps over resident prepared data are generic and measured cleanly. |
| Goal2822 | accept-with-boundary | Fused request/query block kernel gives a modest 8-11% batch improvement while preserving exact aggregate results. |
| Goal2823 | reject-as-default | Device-side partial reduction was correct but mixed: slower at 32K and only marginally faster at 65K, so it stays as a negative probe. |

## Current Implementation Choice

The accepted current implementation is Goal2822:

- one fused 2D-grid block-partial batch kernel;
- host reduction of the compact partial array;
- no device-side partial-reduce kernel in current main.

Goal2823 artifacts are retained for auditability, but the implementation was
reverted.

## Claim Boundary

This consensus does not authorize:

- public RTDL-beats-CuPy wording;
- public RTDL-beats-RTNN-paper wording;
- paper reproduction wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- v2.5 release wording;
- single-request speedup wording from batch evidence.

The accepted claim is narrower: RTDL v2.5 now has a generic, internally
validated batched fixed-radius ranked-summary aggregate path that amortizes
heterogeneous prepared sweeps, and the best current default is the Goal2822
fused batch path.
