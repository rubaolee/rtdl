# Goal2295: Prepared Closed-Shape Membership Phase Telemetry

Status: accepted with Goal2297 2-AI consensus.

## Purpose

Goal2292 showed that the current RayJoin-style PIP route is still slower than
the current LSI route. Goal2295 adds phase telemetry for the prepared
closed-shape membership primitive so the next optimization target is grounded in
measurement rather than guesswork.

This is instrumentation, not an optimization.

## Implementation

The OptiX backend now records the last prepared closed-shape membership call's:

- point host-pack time;
- point upload time;
- candidate count pass time;
- candidate write/traversal pass time;
- candidate download time;
- host exact-refinement time;
- raw candidate count;
- emitted exact count;
- mode: `rows` or `count`.

Python exposes the telemetry through:

- `rtdsl.optix_runtime.get_last_closed_shape_membership_phase_timings()`
- `PreparedOptixPointClosedShapeMembership2D.last_phase_timings()`

The public row/count semantics are unchanged.

## Pod Evidence

Artifact:
`docs/reports/goal2295_closed_shape_phase_probe_pod_2026-05-17.json`

Environment:

- Pod SSH: `root@69.30.85.202 -p 22064`
- Base commit: `398a0f52` plus the Goal2295 telemetry patch
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Query stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_pip_gen100000_stream.json`

| Mode | Wall (s) | Point Pack (s) | Point Upload (s) | Candidate Write (s) | Candidate Download (s) | Exact Refine (s) | Raw Candidates | Emitted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| rows | 0.065984538 | 0.001307263 | 0.000312892 | 0.037341257 | 0.000042015 | 0.012925899 | 8,793 | 8,686 |
| count | 0.048410043 | 0.000324620 | 0.000287538 | 0.037544275 | 0.000027711 | 0.009765691 | 8,793 | 8,686 |

## Interpretation

The prepared PIP bottleneck is now precise:

- point packing/upload is small and is not the next meaningful target;
- candidate traversal/write is the largest measured native phase;
- exact host refinement is still material, but smaller than the traversal/write
  phase on this stream;
- scalar count is faster than row return because it avoids Python-visible row
  materialization, but it still launches the candidate write pass and performs
  host exact refinement.

The next performance work should therefore focus on generic runtime mechanisms
that reduce candidate traversal/write cost or move exact continuation closer to
the device/partner side. A pure Python packing tweak is unlikely to move the
PIP row substantially.

## Boundary

This report does not authorize:

- a PIP speedup claim;
- a RayJoin paper reproduction claim;
- a claim that RTDL beats RayJoin;
- whole-application speedup;
- true zero-copy;
- v2.0 release readiness.

The accepted use of this evidence is bottleneck diagnosis for the prepared
closed-shape membership primitive.
