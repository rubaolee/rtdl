# Goal2297: Prepared Closed-Shape Phase Telemetry 2-AI Consensus

Status: accepted.

## Scope

Goal2297 closes the Goal2295 diagnostic telemetry package. The accepted claim is
narrow: prepared closed-shape membership now exposes last-call phase timings for
rows/count mode, and the RTX A5000 RayJoin-exported PIP probe shows candidate
traversal/write as the largest measured native phase.

This is instrumentation, not a speedup goal.

## Evidence

- Report:
  `docs/reports/goal2295_prepared_closed_shape_phase_telemetry_2026-05-17.md`
- Pod artifact:
  `docs/reports/goal2295_closed_shape_phase_probe_pod_2026-05-17.json`
- Gemini review:
  `docs/reviews/goal2296_gemini_review_goal2295_closed_shape_telemetry_2026-05-17.md`

## Consensus

Codex verdict: `accept`.

Gemini/Antigravity verdict: `accept`.

The agreed interpretation is:

- the telemetry is app-agnostic diagnostic instrumentation for the generic
  closed-shape membership primitive;
- the pod artifact supports the report's phase split;
- candidate traversal/write is the largest measured native phase on the tested
  PIP stream;
- point pack/upload are too small to be the next meaningful optimization target;
- the report avoids speedup, RayJoin reproduction, RTDL-beats-RayJoin,
  true-zero-copy, and release-readiness overclaims.

## Boundary

Allowed claim:

On the recorded RTX A5000 pod and RayJoin-exported 100k PIP stream, the prepared
closed-shape membership telemetry recorded candidate write/traversal around
`0.037s` and exact host refinement around `0.010s` to `0.013s`, making
candidate traversal/write the largest measured native phase.

Not allowed:

- PIP speedup claim;
- RayJoin paper reproduction;
- RTDL beats RayJoin;
- whole-application speedup;
- true zero-copy;
- v2.0 release readiness.
