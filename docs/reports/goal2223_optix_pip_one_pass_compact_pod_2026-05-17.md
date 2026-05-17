# Goal2223: OptiX PIP One-Pass Compact Pod Evidence

Status: pod evidence imported for review; public performance claims remain bounded.

## Scope

Goal2222 added a one-pass optimistic compact writer with overflow fallback. Goal2223 validates it on the same RayJoin-exported PIP stream used by Goals 2209, 2213, and 2219.

- pod: `root@69.30.85.202 -p 22064`
- RTDL commit: `7426c257674d32c4fb33567456c21683bf364ca4`
- source artifact directory: `/root/goal2222_pip_one_pass_pod/artifacts`
- workload: `pip`
- query count: `100000`
- reference backend: `cpu`
- reference row count: `8686`

The main interpretation uses the longer `10`-repeat Embree/OptiX run. CPU reference was still used for parity, but CPU repeats were omitted from the long run to keep the pod cycle focused.

## Long-Run Result

| Backend | Median seconds | Repeats | Rows | Parity vs CPU reference | RT core accelerated |
| --- | ---: | ---: | ---: | --- | --- |
| `embree` | `0.109791` | `10` | `8686` | true | false |
| `optix` | `0.090235` | `10` | `8686` | true | true |

OptiX is about `0.822x` of Embree time on this longer run, or about `1.22x` faster than Embree for this specific same-stream replay.

## Phase Telemetry

The repeat-run profile median confirms that the extra count pass is gone:

| Phase | Median seconds |
| --- | ---: |
| `one_pass` | `1` |
| `fallback_chunks` | `0` |
| `count_pass_s` | `0.000000` |
| `write_pass_s` | `0.037591` |
| `compact_download_s` | `0.000041` |
| `exact_refine_s` | `0.022831` |
| profiled native total | `0.064820` |

Candidate flow remains unchanged from Goal2219:

| Measure | Value |
| --- | ---: |
| conservative GPU candidates | `8793` |
| emitted rows | `8686` |

## Delta

| Comparison | Value |
| --- | ---: |
| OptiX speedup over Goal2209 original same-stream OptiX PIP | `45.52x` |
| OptiX speedup over Goal2213 compact-output OptiX PIP | `6.85x` |
| OptiX speedup over Goal2219 two-pass default-prefilter OptiX PIP | `1.35x` |
| candidate reduction vs Goal2213 | `318.16x` |
| OptiX speedup over Embree in the long run | `1.22x` |

## Interpretation

The one-pass compact path is a useful generic runtime improvement. The fallback contract keeps correctness for dense positive-hit streams, while sparse positive-hit streams avoid an entire OptiX traversal pass.

The PIP weak spot is now much smaller: RTDL OptiX moved from slower than CPU in Goal2209 to slightly faster than Embree on this same stream. This is still not a claim that RTDL beats RayJoin. RayJoin's specialized RT query phase remains far faster, and a paper-scale reproduction would need its full experimental contract.

## Imported Artifacts

| File | Purpose |
| --- | --- |
| `docs/reports/goal2223_optix_pip_one_pass_compact_pod/progress.log` | pod setup and run progress |
| `docs/reports/goal2223_optix_pip_one_pass_compact_pod/build_optix.log` | OptiX build output |
| `docs/reports/goal2223_optix_pip_one_pass_compact_pod/rtdl_pip_one_pass.log` | 3-repeat runner output and profile lines |
| `docs/reports/goal2223_optix_pip_one_pass_compact_pod/rtdl_pip_one_pass_same_rayjoin_stream.json` | 3-repeat timing and parity |
| `docs/reports/goal2223_optix_pip_one_pass_compact_pod/rtdl_pip_one_pass_long.log` | 10-repeat runner output and profile lines |
| `docs/reports/goal2223_optix_pip_one_pass_compact_pod/rtdl_pip_one_pass_long_same_rayjoin_stream.json` | 10-repeat timing and parity |
| `docs/reports/goal2223_optix_pip_one_pass_compact_pod_2026-05-17.json` | compact summary and claim boundary |

## Claim Boundary

This evidence authorizes only a narrow engineering statement: the default OptiX PIP one-pass compact path preserves same-stream parity and substantially improves RTDL OptiX PIP on this stream.

It does not authorize:

- RTDL beats RayJoin;
- broad RT-core speedup claims;
- paper-scale RayJoin reproduction;
- v2.0 release readiness.

External review and a separate consensus report are required before this result can be used in a public performance narrative.
