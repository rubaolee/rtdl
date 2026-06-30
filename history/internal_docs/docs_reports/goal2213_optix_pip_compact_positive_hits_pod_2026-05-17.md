# Goal2213: OptiX PIP Compact Positive-Hit Pod Evidence

Status: pod evidence imported for review; public performance claims remain bounded.

## Scope

Goal2212 changed the OptiX point-in-polygon positive-hit path from a full Cartesian bitmap scan to compact positive-hit candidate output. Goal2213 validates that implementation on the same RayJoin-exported PIP stream used by Goal2209:

- pod: `root@69.30.85.202 -p 22064`
- RTDL commit: `09b1b4122e63d911187701a11d4e86d118ef201c`
- source artifact directory: `/root/goal2212_pip_compact_pod/artifacts`
- workload: `pip`
- query count: `100000`
- reference backend: `cpu`
- reference row count: `8686`

This is a same-stream diagnostic rerun. It is not a full RayJoin paper reproduction and does not authorize a public "RTDL beats RayJoin" claim.

## Result

| Backend | Median seconds | Runs | Rows | Parity vs CPU reference | RT core accelerated |
| --- | ---: | --- | ---: | --- | --- |
| `cpu` | `2.785631` | `2.785631`, `2.791117`, `2.726437` | `8686` | true | false |
| `embree` | `0.110135` | `0.106592`, `0.111970`, `0.110135` | `8686` | true | false |
| `optix` | `0.618395` | `0.547134`, `0.627965`, `0.618395` | `8686` | true | true |

The OptiX PIP result improved from the Goal2209 baseline of `4.107544 s` to `0.618395 s`.

| Comparison | Value |
| --- | ---: |
| OptiX vs previous Goal2209 OptiX | `0.151x` |
| OptiX speedup over previous Goal2209 OptiX | `6.64x` |
| OptiX vs CPU | `0.222x` |
| OptiX vs Embree | `5.615x` |

## Interpretation

The compact-output fix worked. It removed the pathological host scan over the full point-by-polygon Cartesian bitmap and preserved exact parity against the CPU reference.

The result is still not RayJoin-competitive. RTDL OptiX PIP is now faster than the RTDL CPU reference, but it is still slower than RTDL Embree on this stream and much slower than RayJoin's specialized RT query phase from Goal2209. The remaining likely gaps are launch/pass structure, scene preparation reuse, exact-refine placement, and RayJoin-specific grouping that RTDL intentionally cannot bake into the generic engine.

## Imported Artifacts

The repo keeps the compact rerun evidence small and reviewable:

| File | Purpose |
| --- | --- |
| `docs/reports/goal2213_optix_pip_compact_positive_hits_pod/progress.log` | pod setup and run progress |
| `docs/reports/goal2213_optix_pip_compact_positive_hits_pod/build_optix.log` | OptiX build output |
| `docs/reports/goal2213_optix_pip_compact_positive_hits_pod/rtdl_pip_same_stream.log` | runner stdout/stderr |
| `docs/reports/goal2213_optix_pip_compact_positive_hits_pod/rtdl_pip_same_rayjoin_stream.json` | parsed CPU/Embree/OptiX timing and parity |
| `docs/reports/goal2213_optix_pip_compact_positive_hits_pod_2026-05-17.json` | compact summary and claim boundary |

## Claim Boundary

This evidence authorizes only a narrow engineering statement: compact positive-hit output makes the RTDL OptiX PIP same-stream replay about `6.64x` faster than the previous Goal2209 RTDL OptiX PIP replay while preserving parity.

It does not authorize:

- RTDL beats RayJoin;
- broad RT-core speedup claims;
- paper-scale RayJoin reproduction;
- v2.0 release readiness.

External review and a separate consensus report are still required before the result can be used in a public performance narrative.
