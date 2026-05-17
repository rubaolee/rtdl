# Goal2226: Current RayJoin Same-Stream Snapshot

Status: current-commit pod snapshot imported; public performance claims remain bounded.

## Scope

This report records a current-commit same-stream snapshot after the Goal2207 LSI capacity fix and the Goal2212-2225 PIP compact-output, device-prefilter, and one-pass work.

- pod: `root@69.30.85.202 -p 22064`
- RTDL commit: `0ff12cef73ca2d7808d4dd1827d2db6395a7ff80`
- source artifact directory: `/root/goal2226_current_rayjoin_snapshot_pod/artifacts`
- streams: RayJoin-exported `gen_n=100000` LSI and PIP streams from Goal2198/2209

## RTDL Same-Stream Snapshot

| Workload | Backend | Repeats | Reference rows | Median seconds | Parity vs CPU reference |
| --- | --- | ---: | ---: | ---: | --- |
| `lsi` | `cpu` | `5` | `8921` | `1.367840` | true |
| `lsi` | `optix` | `5` | `8921` | `0.084044` | true |
| `pip` | `embree` | `10` | `8686` | `0.109063` | true |
| `pip` | `optix` | `10` | `8686` | `0.091035` | true |

## Immediate Reads

- LSI OptiX is about `16.28x` faster than the RTDL CPU same-stream reference.
- PIP OptiX is about `1.20x` faster than RTDL Embree on this current longer run.
- Both OptiX rows preserve parity against the CPU reference.
- This does not mean RTDL matches RayJoin's specialized query executor. The Goal2209 RayJoin RT query phases were about `0.612 ms` for LSI and `0.575 ms` for PIP, much faster than RTDL's current Python/runtime same-stream replay.

## Imported Artifacts

| File | Purpose |
| --- | --- |
| `docs/reports/goal2226_current_rayjoin_same_stream_snapshot_pod/progress.log` | pod setup and run progress |
| `docs/reports/goal2226_current_rayjoin_same_stream_snapshot_pod/build_optix.log` | OptiX build output |
| `docs/reports/goal2226_current_rayjoin_same_stream_snapshot_pod/rtdl_lsi_current_cpu_optix.log` | LSI runner output |
| `docs/reports/goal2226_current_rayjoin_same_stream_snapshot_pod/rtdl_lsi_current_cpu_optix.json` | LSI timing and parity |
| `docs/reports/goal2226_current_rayjoin_same_stream_snapshot_pod/rtdl_pip_current_embree_optix.log` | PIP runner output |
| `docs/reports/goal2226_current_rayjoin_same_stream_snapshot_pod/rtdl_pip_current_embree_optix.json` | PIP timing and parity |

## Claim Boundary

This is a current engineering snapshot. It does not authorize:

- RTDL beats RayJoin;
- broad RT-core speedup claims;
- paper-scale RayJoin reproduction;
- v2.0 release readiness.

The useful conclusion is narrower: RTDL now has parity-preserving OptiX same-stream paths for both RayJoin LSI and PIP, and the PIP weak spot has been reduced from seconds to roughly a tenth of a second on this stream.
