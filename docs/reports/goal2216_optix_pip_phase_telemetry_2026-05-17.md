# Goal2216: OptiX PIP Phase Telemetry

Status: local telemetry hook ready for pod diagnosis.

## Purpose

Goal2213 proved that compact positive-hit output materially improved RTDL OptiX PIP on the RayJoin same-query stream, but the remaining gap is still large:

- RTDL OptiX PIP: about `0.618 s`
- RTDL Embree PIP: about `0.110 s`
- RayJoin specialized RT query phase: about `0.575 ms`

The next optimization needs phase attribution before changing algorithmic behavior again. Goal2216 adds an opt-in native telemetry line guarded by `RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_PROFILE`.

## Behavior

Default behavior is unchanged. When `RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_PROFILE` is set, `run_pip_optix` writes one stderr line per call:

`[rtdl_optix_point_primitive_anyhit_profile] positive_only=... points=... polygons=... chunks=... candidates=... emitted=... host_pack_s=... upload_s=... accel_build_s=... count_pass_s=... write_pass_s=... compact_download_s=... exact_refine_s=... total_s=...`

The fields are intentionally generic:

- `host_pack_s`: host-side record conversion before GPU upload;
- `upload_s`: device allocation/upload for point and polygon columns;
- `accel_build_s`: OptiX custom-geometry acceleration structure build;
- `count_pass_s`: compact positive-hit count traversal;
- `write_pass_s`: compact positive-hit write traversal;
- `compact_download_s`: compact candidate download;
- `exact_refine_s`: host exact refinement over compact candidates;
- `candidates`: conservative GPU candidate rows before exact refinement;
- `emitted`: final rows returned through the public API.

## Claim Boundary

This is diagnostic infrastructure only. It does not authorize a performance claim, alter the public Python API, or change the app-agnostic engine boundary. Pod evidence is still required to interpret which phase is the next real bottleneck.
