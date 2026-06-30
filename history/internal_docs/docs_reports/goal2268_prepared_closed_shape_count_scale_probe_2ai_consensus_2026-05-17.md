# Goal2268: Prepared Closed-Shape Count Scale Probe 2-AI Consensus

Status: accepted with boundary.

## Scope

This consensus covers Goal2266, a synthetic repeated-stream scale diagnostic for
prepared closed-shape row-return versus exact scalar count.

## Evidence

- Report:
  `docs/reports/goal2266_prepared_closed_shape_count_scale_probe_2026-05-17.md`
- Artifact:
  `docs/reports/goal2266_prepared_closed_shape_count_scale_probe_pod_2026-05-17.json`
- Gemini review:
  `docs/reviews/goal2267_gemini_review_goal2266_count_scale_probe_2026-05-17.md`

## Consensus

Codex verdict: `accept-with-boundary`.

Gemini independent review verdict: `accept`.

Consensus verdict: `accept-with-boundary`.

Accepted diagnostic table:

| Queries | Expected count | Row-return median sec | Exact count median sec | Count / row ratio |
| ---: | ---: | ---: | ---: | ---: |
| 100,000 | 8,686 | 0.06329208984971046 | 0.043399712070822716 | 0.6857051516844683 |
| 200,000 | 17,372 | 0.09712744504213333 | 0.07056158594787121 | 0.726484526770595 |
| 500,000 | 43,430 | 0.23066251166164875 | 0.17201292887330055 | 0.7457342228442421 |
| 1,000,000 | 86,860 | 0.4656780920922756 | 0.3518645130097866 | 0.7555960200508284 |

## Boundary

This is a synthetic repeated-stream diagnostic. It does not authorize a RayJoin
paper dataset claim, RTDL-beats-RayJoin claim, broad PIP speedup claim, v2.0
release-readiness claim, or true device-resident output-stream claim.
