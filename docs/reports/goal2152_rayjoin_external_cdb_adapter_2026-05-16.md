# Goal2152 RayJoin External CDB Adapter

Date: 2026-05-16

Status: local fixture evidence collected; pod/public-data evidence pending.

## Purpose

Goal2145 made a RayJoin-style RTDL v2 app over checked-in representative datasets. Goal2152 extends the app so a learner can point the same Python+partner+RTDL program at external RayJoin CDB files without changing the native engine.

This is the bridge from synthetic/fixture RayJoin work toward serious public or paper-style RayJoin datasets.

## User Contract

The app still exposes three workloads:

- `pip`
- `lsi`
- `overlay_seed`

The `--dataset` argument now accepts either the existing representative dataset names or external CDB paths:

| Workload | External form | Meaning |
| --- | --- | --- |
| `pip` | `path.cdb` | Derive probe points and polygons from one CDB file. |
| `pip` | `points.cdb + polygons.cdb` | Derive probe points from the left file and polygons from the right file. |
| `lsi` | `left.cdb + right.cdb` | Derive line-segment sets from left/right chain records. |
| `overlay_seed` | `left.cdb + right.cdb` | Derive left/right polygon chains and produce overlay dependency rows. |

Relative paths are resolved from the repository root. Absolute paths are accepted for pod and local Linux runs.

## App-Agnostic Boundary

This goal changes only the Python app-level adapter:

- `examples/rtdl_rayjoin_v2_spatial_join_app.py`

It does not add C/C++ symbols, native entry points, shader strings, OptiX continuations, or backend-specific app logic. The RTDL engine still sees generic primitive inputs and returns generic rows.

The external CDB adapter is deliberately outside the native engine because RayJoin file parsing, chain-to-polygon conversion, probe-point selection, and workload selection are application/data concerns.

## Local Evidence

Guard coverage:

- `tests/goal2145_rayjoin_v2_spatial_join_app_test.py`

The new test copies the RayJoin fixture CDB files to temporary external paths and verifies:

- a single external CDB path can drive the `pip` workload
- a `left.cdb + right.cdb` pair can drive the `overlay_seed` workload
- the app returns the same public output contracts
- no native customization is required

Focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2145_rayjoin_v2_spatial_join_app_test tests.goal2147_rayjoin_v2_scale_perf_test tests.goal2150_optix_shape_pair_relation_kernel_compile_test tests.goal2150_rayjoin_v2_optix_pod_perf_report_test tests.goal2151_gemini_review_goal2150_rayjoin_optix_pod_test
py -3 -m py_compile examples\rtdl_rayjoin_v2_spatial_join_app.py tests\goal2145_rayjoin_v2_spatial_join_app_test.py
```

Result: all focused tests passed locally.

## Next Pod Step

Use the working repo key, not the rejected default SSH key:

```text
ssh root@157.157.221.29 -p 24240 -i id_ed25519_rtdl_codex
```

On the pod, pull the current commit, rebuild OptiX if needed, download public RayJoin sample CDBs through `rtdsl.datasets.download_rayjoin_sample`, and run the app with absolute external CDB paths for PIP, LSI, and overlay seed.

## Claim Boundary

This goal authorizes:

- external CDB path ingestion at the user app layer
- local fixture evidence that the adapter preserves the RTDL v2 output contracts
- continued pod/public-data testing on RayJoin-style inputs

This goal does not authorize:

- full RayJoin paper reproduction
- paper-scale performance claims
- broad RT-core speedup claims
- new native app-specific engine functionality
- v2.0 release authorization

## Verdict

Goal2152 is accepted as an app-level data-ingestion improvement that keeps RTDL v2 engine boundaries clean. Pod/public-data evidence is still required before using it for performance conclusions.
