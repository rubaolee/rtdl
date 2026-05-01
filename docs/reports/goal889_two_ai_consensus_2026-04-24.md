# Goal889 Two-AI Consensus

Date: 2026-04-24

## Scope

Goal889 adds a bounded graph RT-core candidate:

```text
graph_analytics / visibility_edges
```

The sub-path maps graph candidate visibility edges to RTDL
`visibility_rows(...)`, which is the existing ray/triangle any-hit surface used
by OptiX on RTX hardware.

## Codex Position

ACCEPT.

The implementation is intentionally narrow. It gives the graph app one
accelerator-facing RT traversal path while preserving the existing honesty
boundary: BFS and triangle-count remain host-indexed fallback paths and are not
claimed as RT-core accelerated.

## Gemini Position

ACCEPT.

Gemini reviewed the implementation and wrote:

```text
The implementation is surgical, honest, and correctly integrated into the broader RTX readiness framework.
```

Full review:

```text
docs/reports/goal889_gemini_external_review_2026-04-24.md
```

## Consensus

ACCEPT.

`graph_analytics` may move to `needs_real_rtx_artifact` and
`rt_core_partial_ready` only for the `visibility_edges` sub-path.

## Non-Claims

Goal889 does not claim RT-core acceleration for:

- BFS,
- triangle count,
- shortest path,
- graph database workloads,
- general graph analytics.

## Release Gate

The cloud claim remains blocked until the deferred Goal889 gate runs on a real
RTX host and passes strict CPU-vs-OptiX parity:

```bash
python3 scripts/goal889_graph_visibility_optix_gate.py \
  --copies 20000 \
  --output-mode summary \
  --strict \
  --output-json docs/reports/goal889_graph_visibility_optix_gate_rtx.json
```
