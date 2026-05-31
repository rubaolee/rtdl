# Goal2841: RTNN Same-Stream Scale Probe

Date: 2026-05-31

Status: pod-probed, externally reviewed, consensus accepted with boundary

## Purpose

Goal2839 added an app-facing result mode for the same-stream graph/CuPy consumer. Goal2841 measures the cost boundary at a larger 65K RTNN-shaped input by comparing:

- direct prepared CUDA graph replay:
  `ranked-summary-aggregate-prepared-query-batch-graph-float32`;
- same-stream prepared CUDA graph replay plus bounded CuPy consumer:
  `ranked-summary-aggregate-prepared-query-batch-graph-same-stream-cupy-float32`.

This is a traceability path, not a speedup path.

## Pod Setup

Pod:

```text
ssh root@69.30.85.171 -p 22167 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

Source commit:

```text
35ac09fe8f54bfb9e60584b7dee5f9618fb7708c
```

Dataset:

- 65,536 deterministic uniform 3-D points;
- radius `0.02`;
- base `k_max=50`;
- three heterogeneous aggregate requests;
- three repeats for each mode.

Artifacts:

- `docs/reports/goal2841_rtnn_same_stream_scale_pod/generated_uniform_65536.json`
- `docs/reports/goal2841_rtnn_same_stream_scale_pod/direct_graph_65536.json`
- `docs/reports/goal2841_rtnn_same_stream_scale_pod/same_stream_graph_65536.json`
- `docs/reports/goal2841_rtnn_same_stream_scale_pod/goal2841_summary.json`

## Result

Both modes passed and their aggregate summaries matched.

| Mode | Runs (s) | Median (s) |
| --- | --- | ---: |
| Direct CUDA graph replay | `0.000648`, `0.000453`, `0.000419` | `0.000453` |
| Same-stream graph + CuPy consumer | `0.227444`, `0.000872`, `0.000712` | `0.000872` |

Ratio:

```text
same_stream / direct median = 1.923x
```

Interpretation:

- The same-stream path preserves planner metadata and avoids host scalar read before the consumer.
- It is roughly 1.923x slower than direct native graph aggregate replay at this scale after warmup.
- The first same-stream run includes CuPy/JIT/cache startup cost (`0.227s`) and is not representative of steady-state replay.
- Direct native graph replay remains the faster app-facing aggregate path when no partner continuation is required.

## Boundary

Goal2841 does not authorize a public speedup claim. It records that the same-stream partner-consumer path is correct and traceable, while costing more than the direct native aggregate replay path on this fixture.

The value of the same-stream path is partner-continuation integration and auditability, not replacing the fastest native aggregate when a partner is unnecessary.

Independent review:

- `docs/reviews/goal2842_gemini_review_goal2841_rtnn_same_stream_scale_probe_2026-05-31.md`

Consensus:

- `docs/reports/goal2842_goal2841_rtnn_same_stream_scale_probe_consensus_2026-05-31.md`

## Codex Verdict

`accept-with-boundary`

The result is useful and honest: same-stream partner continuation is now app-facing and correct, but direct graph replay is still the faster RTNN aggregate mode on this 65K probe.
