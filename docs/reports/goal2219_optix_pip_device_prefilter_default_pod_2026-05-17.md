# Goal2219: OptiX PIP Device Prefilter Default Pod Evidence

Status: pod evidence imported for review; public performance claims remain bounded.

## Scope

Goal2218 made the device-side PIP prefilter the default positive-only OptiX path while preserving host exact refinement. Goal2219 validates the default path on the same RayJoin-exported PIP stream used by Goals 2209 and 2213.

- pod: `root@69.30.85.202 -p 22064`
- RTDL commit: `4c839305ac3e2284aa34be3a19641af9fa474564`
- source artifact directory: `/root/goal2218_pip_prefilter_default_pod/artifacts`
- workload: `pip`
- query count: `100000`
- reference backend: `cpu`
- reference row count: `8686`

No `RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DEVICE_PREFILTER` environment variable was set. This is the new default path. `RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_PROFILE=1` was set only to capture phase telemetry.

## Result

| Backend | Median seconds | Runs | Rows | Parity vs CPU reference | RT core accelerated |
| --- | ---: | --- | ---: | --- | --- |
| `cpu` | `3.124819` | `3.124819`, `3.328613`, `2.765293` | `8686` | true | false |
| `embree` | `0.109553` | `0.105981`, `0.109553`, `0.110455` | `8686` | true | false |
| `optix` | `0.121710` | `0.128955`, `0.121710`, `0.115761` | `8686` | true | true |

## Phase Telemetry

The repeat-run median profile line shows the new bottleneck moved away from host exact refinement:

| Phase | Median seconds |
| --- | ---: |
| `count_pass_s` | `0.032660` |
| `write_pass_s` | `0.032737` |
| `compact_download_s` | `0.000036` |
| `exact_refine_s` | `0.022901` |
| profiled native total | `0.096581` |

The key candidate-flow change is:

| Measure | Before default prefilter | After default prefilter |
| --- | ---: | ---: |
| conservative GPU candidates | `2797698` | `8793` |
| emitted rows | `8686` | `8686` |

## Delta

| Comparison | Value |
| --- | ---: |
| OptiX speedup over Goal2209 original same-stream OptiX PIP | `33.75x` |
| OptiX speedup over Goal2213 compact-output OptiX PIP | `5.08x` |
| candidate reduction vs Goal2213 | `318.16x` |
| OptiX vs CPU | `0.039x` |
| OptiX vs Embree | `1.111x` |

## Interpretation

The fix is real and specific. Goal2212 removed the full Cartesian bitmap scan. Goal2218/2219 remove almost all obvious non-hit candidates before host exact refinement. Together they turn the PIP weak spot from `4.108 s` into `0.122 s` on the same stream while preserving row parity.

The result is still not a RayJoin paper reproduction. RTDL OptiX is now near RTDL Embree on this stream, but still slower than Embree by about `11%` and much slower than RayJoin's specialized RT query phase. The remaining gap is likely the generic two-pass count/write structure plus RTDL's public Python/runtime overhead, not the old host candidate explosion.

## Imported Artifacts

| File | Purpose |
| --- | --- |
| `docs/reports/goal2219_optix_pip_device_prefilter_default_pod/progress.log` | pod setup and run progress |
| `docs/reports/goal2219_optix_pip_device_prefilter_default_pod/build_optix.log` | OptiX build output |
| `docs/reports/goal2219_optix_pip_device_prefilter_default_pod/rtdl_pip_default.log` | runner output and profile lines |
| `docs/reports/goal2219_optix_pip_device_prefilter_default_pod/rtdl_pip_default_same_rayjoin_stream.json` | parsed backend timing and parity |
| `docs/reports/goal2219_optix_pip_device_prefilter_default_pod_2026-05-17.json` | compact summary and claim boundary |

## Claim Boundary

This evidence authorizes only a narrow engineering statement: the default OptiX PIP path now preserves same-stream parity and is much faster than the previous RTDL OptiX implementations on this stream.

It does not authorize:

- RTDL beats RayJoin;
- broad RT-core speedup claims;
- paper-scale RayJoin reproduction;
- v2.0 release readiness.

External review and a separate consensus report are required before this result can be used in a public performance narrative.
