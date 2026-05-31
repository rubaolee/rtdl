# Goal2842 Consensus: Goal2841 RTNN Same-Stream Scale Probe

Date: 2026-05-31

## Participants

- Codex pod probe and local report.
- Gemini independent read-only review:
  `docs/reviews/goal2842_gemini_review_goal2841_rtnn_same_stream_scale_probe_2026-05-31.md`

## Consensus Verdict

Codex + Gemini consensus accepts Goal2841 with boundary.

Verdict: `accept-with-boundary`

## Consensus Table

| Decision Point | Consensus |
| --- | --- |
| Direct and same-stream summaries match | accept |
| Same-stream metadata preserves `accepted_preview` / `cupy_conformance` / no fallback | accept |
| No host scalar read before same-stream consumer | accept |
| Same-stream slower than direct graph replay on 65K fixture | accept, measured boundary |
| Direct native graph replay remains preferred when no partner continuation is needed | accept |
| Public performance claim | not authorized |
| Paper reproduction claim | not authorized |
| Broad true-zero-copy claim | not authorized |
| Arbitrary partner continuation claim | not authorized |
| v2.5 release readiness | not authorized |

## Evidence

- Summary artifact:
  `docs/reports/goal2841_rtnn_same_stream_scale_pod/goal2841_summary.json`
- Direct graph artifact:
  `docs/reports/goal2841_rtnn_same_stream_scale_pod/direct_graph_65536.json`
- Same-stream graph artifact:
  `docs/reports/goal2841_rtnn_same_stream_scale_pod/same_stream_graph_65536.json`

## Boundary

Goal2841 records a cost boundary: the same-stream path is correct and traceable, but slower than direct native graph replay on this fixture. It is useful when a partner continuation is required; it is not the default fastest path for pure native aggregate replay.
