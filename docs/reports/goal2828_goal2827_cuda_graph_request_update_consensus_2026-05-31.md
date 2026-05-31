# Goal2828 Consensus for Goal2827 CUDA Graph Request Update

Date: 2026-05-31

Verdict: Codex + Gemini consensus accepts Goal2827 with boundary.

## Scope

Goal2827 extends the Goal2825 static CUDA graph replay handle with an explicit
same-shape request-buffer update operation. The graph topology remains fixed;
only the compact device arrays for radius and `k_max` are updated before replay.

## Independent Review

Gemini independently reviewed Goal2827 in:

`docs/reviews/goal2828_gemini_review_goal2827_cuda_graph_request_update_2026-05-31.md`

Gemini verdict: `accept-with-boundary`.

Gemini accepts that:

- the native boundary remains app-agnostic;
- request updates are constrained to same-shape handles with unchanged request
  count;
- the Python API exposes the behavior explicitly through `update_requests(...)`;
- pod evidence supports exact parity for request set A and updated request set B;
- the measured performance claim remains narrow: 1.062x update+replay over
  rebuild+replay in the recorded 32K probe;
- no public RTDL-beats-CuPy, RTDL-beats-RTNN-paper, broad RT-core, whole-app
  speedup, or v2.5 release claim is authorized.

## Consensus Position

Codex and Gemini agree:

| Topic | Consensus |
| --- | --- |
| App-agnostic native boundary | accept |
| Same-shape request-update constraint | accept |
| Explicit opt-in Python API | accept |
| Pod evidence | accept-with-boundary |
| Default runtime change | not authorized |
| Public speedup / paper reproduction claims | not authorized |

## Accepted Evidence

The accepted pod artifact is:

`docs/reports/goal2827_rtnn_cuda_graph_request_update_pod/goal2827_summary.json`

Accepted narrow result:

| Points | Requests | Update+Replay Median (s) | Rebuild+Replay Median (s) | Rebuild / Update |
| ---: | ---: | ---: | ---: | ---: |
| 32,768 | 4 | 0.000373542 | 0.000396671 | 1.062x |

The parity fields are true:

- `direct_a_matches_graph_a`
- `direct_b_matches_updated_graph_b`

## Boundary

This consensus does not authorize:

- changing the default runtime path;
- public RTDL-beats-CuPy wording;
- public RTDL-beats-RTNN-paper wording;
- whole-app speedup wording;
- broad RT-core speedup wording;
- v2.5 release wording.

The accepted claim is only that RTDL has an opt-in, same-shape request-buffer
update operation for the static prepared CUDA graph aggregate-batch handle, with
the measured RTX A5000 pod evidence above.

