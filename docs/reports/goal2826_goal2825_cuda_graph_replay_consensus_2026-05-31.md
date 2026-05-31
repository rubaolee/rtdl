# Goal2826 Consensus for Goal2825 CUDA Graph Replay

Date: 2026-05-31

Verdict: Codex + Gemini consensus accepts Goal2825 with boundary.

## Scope

Goal2825 adds an explicit CUDA graph replay handle for static prepared
fixed-radius ranked-summary aggregate batches. It is a narrow continuation of
the RTNN v2.5 batch chain:

- Goal2821: heterogeneous aggregate requests over prepared data;
- Goal2822: fused request/query block-partial batch kernel;
- Goal2823: rejected device-side partial reduction as default;
- Goal2824: Gemini consensus on Goals2821-2823;
- Goal2825: explicit graph replay for the accepted Goal2822 fused kernel.

## Independent Review

Gemini independently reviewed Goal2825 in:

`docs/reviews/goal2826_gemini_review_goal2825_cuda_graph_replay_2026-05-31.md`

Gemini verdict: `accept-with-boundary`.

The review accepts that:

- the native engine remains app-agnostic;
- CUDA graph replay is explicit opt-in behavior;
- the evidence is bounded to static prepared fixed-radius ranked-summary
  aggregate batches;
- pod results are interpreted as modest graph-vs-fused replay speedups with
  exact normalized aggregate parity;
- no public RTDL-beats-CuPy, RTDL-beats-RTNN-paper, broad RT-core, whole-app
  speedup, or v2.5 release claim is authorized.

## Consensus Position

Codex and Gemini agree:

| Topic | Consensus |
| --- | --- |
| App-agnostic native boundary | accept |
| Explicit opt-in CUDA graph handle | accept |
| Pod evidence | accept-with-boundary |
| Default runtime change | not authorized |
| Public speedup / paper reproduction claims | not authorized |

## Accepted Evidence

The accepted pod artifact is:

`docs/reports/goal2825_rtnn_cuda_graph_replay_pod/goal2825_summary.json`

Accepted narrow result:

| Points | Fused Batch Median (s) | Graph Replay Median (s) | Graph vs Fused |
| ---: | ---: | ---: | ---: |
| 32,768 | 0.000302468 | 0.000261544 | 1.156x |
| 65,536 | 0.000829425 | 0.000808079 | 1.026x |

The result parity fields are true after normalizing away the graph-only
metadata marker:

- `same_ranked_aggregate_summary`
- `same_ranked_aggregate_batch_summaries_normalized`

## Boundary

This consensus does not authorize:

- changing the default RTDL v2.5 path from Goal2822 fused batch to graph replay;
- public RTDL-beats-CuPy wording;
- public RTDL-beats-RTNN-paper wording;
- whole-app speedup wording;
- broad RT-core speedup wording;
- v2.5 release wording.

The accepted claim is only that RTDL has an opt-in, generic static prepared
CUDA graph replay handle for this aggregate-batch contract, with the measured
RTX A5000 pod evidence above.

