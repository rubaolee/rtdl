# Gemini Review For Goal3527 v2.8 Performance Recovery Plan

Date: 2026-06-05

## Review Analysis

### 1. Does this plan answer the user's concern that the current same-runner result is too weak to be the v2.8 story?

Yes, the plan directly addresses this concern. Goal3527 explicitly states that Goal3524's same-runner results are a "diagnostic table" and "not the final promoted-v2.8 table." It proposes a clear path forward by establishing a separate "promoted-path performance table" and implementing a repair ladder for weak same-runner rows, starting with the most significant regressions.

### 2. Is the distinction between diagnostic same-runner rows and promoted v2.8 optimized rows clear?

Yes, the distinction is clear. The plan outlines a two-table strategy: retaining Goal3524 as the diagnostic baseline and creating a new table for "promoted-path performance" that measures optimized v2.8 paths. The detailed columns specified for the promoted-path table, including "v2.3 evidence baseline contract," "v2.8 promoted contract," and "whether the contract is same-contract, evolved-contract, or capability-new," further reinforce this distinction. It explicitly warns against collapsing evolved app contracts into fake ratios.

### 3. Are the priorities correct: Barnes-Hut P0, RayJoin promoted-path evidence P1, then DBSCAN/RTNN/LibRTS/flat rows?

Yes, the priorities are well-justified. The Barnes-Hut node coverage regression (0.401x/0.503x) is a significant slowdown and correctly assigned P0 for immediate investigation and recovery to at least parity. RayJoin and RT-DBSCAN are designated P1, which is appropriate for measuring their promoted v2.8 paths and ensuring these provide a stronger performance story. The remaining items, being either near parity or less severe regressions, are correctly assigned P2 for further investigation, scaling, or honest classification.

### 4. Does the plan keep the engine app-agnostic and partner choice explicit?

Yes, the plan strongly emphasizes maintaining the app-agnostic engine boundary and explicit partner choice. Design rules and acceptance gates explicitly state "no app-specific native-engine shortcuts are allowed" and that partners "remain explicit," with CuPy being the designated partner where needed and PyTorch explicitly excluded from silently entering v2.8 performance paths.

### 5. Does the plan avoid release/public speedup overclaiming?

Yes, the plan meticulously avoids overclaiming. Multiple design rules and acceptance gates strictly prohibit "public speedup wording," "release wording," "whole-app wording," and other forms of broad or premature claims. Goal3524 itself also includes similar disclaimers, reinforcing a cautious and evidence-based approach to external communication.

### 6. What must be changed before Codex starts implementation?

The plan explicitly states: "No implementation should start until Codex, Claude, and Gemini agree this is the right next move or revise it into an accepted plan." Therefore, the primary requirement before implementation is gaining consensus from all three AIs and a verdict of `accept` or `accept-with-boundary`. No specific changes are required from this Gemini review as the plan appears sound and robust.

## Verdict

`accept`
