# Goal2221: OptiX PIP Default Prefilter 2-AI Consensus

Status: Codex + Gemini consensus recorded for the Goal2219 default-path pod evidence.

## Inputs

- Source change report: `docs/reports/goal2218_optix_pip_device_prefilter_default_2026-05-17.md`
- Pod evidence report: `docs/reports/goal2219_optix_pip_device_prefilter_default_pod_2026-05-17.md`
- Pod evidence summary: `docs/reports/goal2219_optix_pip_device_prefilter_default_pod_2026-05-17.json`
- Independent Gemini review: `docs/reviews/goal2220_gemini_review_goal2219_optix_pip_default_prefilter_pod_2026-05-17.md`

## Consensus

Codex and Gemini agree that Goal2219 supports the narrow engineering conclusion:

The default RTDL OptiX PIP path, without setting `RTDL_OPTIX_PIP_DEVICE_PREFILTER`, preserves same-stream parity and improves the RayJoin-exported PIP replay from the previous RTDL OptiX baselines to `0.121710 s` median on the tested pod.

Gemini's independent verdict is `accept`. Codex records the result as accepted with strict claim boundaries.

## Confirmed Facts

| Item | Consensus |
| --- | --- |
| Same RayJoin-exported PIP stream contract | accepted |
| CPU/Embree/OptiX parity vs CPU reference | accepted |
| Reference row count | `8686` |
| OptiX median after default prefilter | `0.121710 s` |
| OptiX speedup over Goal2209 original OptiX PIP | `33.75x` |
| OptiX speedup over Goal2213 compact-output OptiX PIP | `5.08x` |
| Candidate reduction vs Goal2213 | `318.16x` |
| OptiX still slower than RTDL Embree | accepted |
| RTDL beats RayJoin claim | not authorized |
| Broad RT-core speedup claim | not authorized |
| v2.0 release readiness | not authorized |

## Next Engineering Read

The old host candidate explosion is no longer the bottleneck. Phase telemetry now points to the generic two-pass count/write structure and Python/runtime overhead as the next likely gap. A safe next experiment is a one-pass optimistic compact writer with overflow fallback.
