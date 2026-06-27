# Goal2225: OptiX PIP One-Pass Compact 2-AI Consensus

Status: Codex + Gemini consensus recorded for the Goal2223 one-pass compact pod evidence.

## Inputs

- Source change report: `docs/reports/goal2222_optix_pip_one_pass_compact_experiment_2026-05-17.md`
- Pod evidence report: `docs/reports/goal2223_optix_pip_one_pass_compact_pod_2026-05-17.md`
- Pod evidence summary: `docs/reports/goal2223_optix_pip_one_pass_compact_pod_2026-05-17.json`
- Independent Gemini review: `docs/reviews/goal2224_gemini_review_goal2223_optix_pip_one_pass_compact_pod_2026-05-17.md`

## Consensus

Codex and Gemini agree that Goal2223 supports the narrow engineering conclusion:

The default RTDL OptiX PIP one-pass compact path preserves same-stream parity and improves the RayJoin-exported PIP replay to `0.090235 s` median on the tested pod.

Gemini's independent verdict is `accept`. Codex records the result as accepted with strict claim boundaries.

## Confirmed Facts

| Item | Consensus |
| --- | --- |
| Same RayJoin-exported PIP stream contract | accepted |
| Embree/OptiX parity vs CPU reference | accepted |
| Reference row count | `8686` |
| OptiX long-run median | `0.090235 s` |
| Embree long-run median | `0.109791 s` |
| OptiX speedup over Goal2209 original OptiX PIP | `45.52x` |
| OptiX speedup over Goal2213 compact-output OptiX PIP | `6.85x` |
| OptiX speedup over Goal2219 two-pass default-prefilter OptiX PIP | `1.35x` |
| OptiX speedup over Embree in this long run | `1.22x` |
| One-pass path used | `one_pass=1` |
| Fallback chunks | `0` |
| RTDL beats RayJoin claim | not authorized |
| Broad RT-core speedup claim | not authorized |
| v2.0 release readiness | not authorized |

## Boundary

This consensus is performance evidence for a specific RTDL same-query replay and a specific generic runtime improvement. It does not close the RayJoin paper reproduction lane, does not prove RTDL beats RayJoin, and does not authorize v2.0 release readiness.
