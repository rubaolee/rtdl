# Goal2287: Packed-Left Segment-Pair 2-AI Consensus

Status: accepted.

## Scope

Goal2287 closes the Goal2283-2285 segment-pair telemetry and packed-left
evidence package. The accepted claim is narrow: on one recorded RTX A5000 pod
and one RayJoin-exported 100k LSI stream, prepacking reusable left/query segment
geometry removes repeated Python packing overhead and improves repeated prepared
segment-pair raw/count calls by about `20x` versus passing tuple records each
call.

## Evidence

- Telemetry implementation report:
  `docs/reports/goal2283_segment_pair_phase_telemetry_2026-05-17.md`
- Pod telemetry report:
  `docs/reports/goal2284_segment_pair_phase_telemetry_pod_2026-05-17.md`
- Plain tuple artifact:
  `docs/reports/goal2284_segment_pair_phase_telemetry_pod_2026-05-17.json`
- Prepacked-left artifact:
  `docs/reports/goal2285_segment_pair_packed_left_probe_pod_2026-05-17.json`
- Gemini review:
  `docs/reviews/goal2286_gemini_review_goal2284_2285_packed_left_2026-05-17.md`

## Consensus

Codex verdict: `accept`.

Gemini/Antigravity verdict: `accept`.

The agreed interpretation is:

- the native prepared segment-pair phases are small relative to tuple-input wall
  time on the measured stream;
- repeated tuple-input calls are dominated by Python-side packing of the 100k
  left/query segments;
- prepacking the left/query batch once reduces repeated raw/count medians from
  about `0.20s` to about `0.010s`;
- this is a v2 programming-model lesson, not a new engine specialization.

## Claim Boundary

Allowed claim:

On the recorded RTX A5000 pod and RayJoin-exported 100k LSI stream, reusing a
prepacked left/query segment batch improves repeated prepared segment-pair raw
row and scalar-count calls by about `20x` versus passing tuple records to each
call.

Not allowed:

- whole RayJoin application speedup;
- RayJoin paper reproduction;
- RTDL beats RayJoin;
- broad RT-core speedup;
- true zero-copy;
- claim that all workloads get a 20x gain from prepacking.
