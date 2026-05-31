# Goal2844 Consensus: Goal2843 v2.5 Execution-Path Policy

Date: 2026-05-31

## Participants

- Codex implementation and report.
- Gemini independent read-only review:
  `docs/reviews/goal2844_gemini_review_goal2843_execution_path_policy_2026-05-31.md`

## Consensus Verdict

Codex + Gemini consensus accepts Goal2843 with boundary.

Verdict: `accept-with-boundary`

## Consensus Table

| Decision Point | Consensus |
| --- | --- |
| Direct graph without partner continuation | accept |
| Same-stream only when partner continuation is required | accept |
| Runner attaches `execution_path_plan` without semantic change | accept |
| Hidden smart dispatch remains blocked | accept |
| Explicit result-mode choice remains required | accept |
| Public performance/release claims | not authorized |
| RT-core speedup claims | not authorized |
| Whole-app speedup claims | not authorized |
| True zero-copy claims | not authorized |
| v2.5 release readiness | not authorized |

## Evidence

- Policy:
  `src/rtdsl/v2_5_execution_path_policy.py`
- Runner integration:
  `scripts/goal2348_rtnn_v2_2_external_runner.py`
- Goal2841 pod evidence:
  `docs/reports/goal2841_rtnn_same_stream_scale_pod/goal2841_summary.json`

## Boundary

Goal2843 is an explain/routing hardening step. It records that direct native graph replay remains preferred for pure aggregate replay, while same-stream is the correct explicit path for partner continuation and primitive-payload entrypoint metadata. It does not promote same-stream as a faster path.

