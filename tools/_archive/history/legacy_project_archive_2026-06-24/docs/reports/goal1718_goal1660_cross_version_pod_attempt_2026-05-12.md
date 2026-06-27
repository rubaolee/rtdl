# Goal1718 Goal1660 Cross-Version Pod Attempt

Date: 2026-05-12

Status: raw Goal1660 cross-version execution attempt on the RTX 4000 Ada pod.

## Context

Goal1716 completed all 16 active Goal1659 current-version pod rows after the
GEOS C link fix and graph CSR binding fix. Goal1718 attempted the next layer:
running the Goal1660 planned v1.6.11-versus-v1.0 command matrix from two pod
workspaces.

Workspaces:

```text
current candidate: /workspace/rtdl_goal1714
v1.0 baseline:     /workspace/rtdl_goal1714_v1_0
```

The baseline worktree was created from the local `v1.0` tag:

```text
b9c9620af78a2fab92083d43af312bb6310e452a
```

The v1.0 worktree successfully built Embree and OptiX on the pod:

```bash
make build-embree
make build-optix OPTIX_PREFIX=/opt/optix CUDA_PREFIX=/usr/local/cuda CUDA_LIB=/usr/local/cuda/targets/x86_64-linux/lib NVCC=/usr/local/cuda/bin/nvcc GEOS_LIBS=-lgeos_c
```

The v1.0 build produced:

```text
build/librtdl_embree.so 377040 bytes
build/librtdl_optix.so 597832 bytes
```

and `ldd build/librtdl_optix.so` included:

```text
libgeos_c.so.1
libgeos.so.3.12.1
```

## Raw Runner

The raw cross-version runner executed every Goal1660 `planned` row twice:

- v1.6.11 command in `/workspace/rtdl_goal1714`
- v1.0 command in `/workspace/rtdl_goal1714_v1_0`

Raw artifacts:

```text
docs/reports/goal1718_goal1660_cross_version_raw_2026-05-12.json
docs/reports/goal1718_goal1660_cross_version_raw_2026-05-12.log
```

The runner completed all invocations:

```text
completed_invocation_count: 56
expected_invocation_count: 56
```

## Results

Current candidate:

```text
v1_6_11: 28 / 28 planned invocations returned 0 and wrote JSON artifacts
```

Baseline:

```text
v1_0: 4 / 28 planned invocations returned 0 and wrote JSON artifacts
```

The four v1.0 rows that produced artifacts were:

| App | Engine | Artifact |
| --- | --- | --- |
| `database_analytics` | `embree` | `docs/reports/goal1660_v1_0_database_analytics_embree.json` |
| `database_analytics` | `optix` | `docs/reports/goal1660_v1_0_database_analytics_optix.json` |
| `graph_analytics` | `optix` | `docs/reports/goal1660_v1_0_graph_analytics_optix.json` |
| `outlier_detection` | `optix` | `docs/reports/goal1660_v1_0_outlier_detection_optix.json` |

The remaining 24 v1.0 invocations failed before producing artifacts because the
tagged v1.0 scripts do not accept the newer current-manifest `--backend`
argument. Representative errors:

```text
goal811_spatial_optix_summary_phase_profiler.py: error: unrecognized arguments: --backend embree
goal887_prepared_decision_phase_profiler.py: error: unrecognized arguments: --backend optix
goal933_prepared_segment_polygon_optix_profiler.py: error: unrecognized arguments: --backend embree
goal934_prepared_segment_polygon_pair_rows_optix_profiler.py: error: unrecognized arguments: --backend optix
goal877_polygon_overlap_optix_phase_profiler.py: error: unrecognized arguments: --backend embree
goal760_optix_robot_pose_flags_phase_profiler.py: error: unrecognized arguments: --backend optix
```

This is a baseline command-shape/schema compatibility blocker. It is not a
current-source build failure and not a pod hardware failure.

## Current-Candidate Coverage

The current candidate did produce artifacts for all 28 planned Goal1660
invocations, including the long `polygon_set_jaccard/embree` row:

```text
polygon_set_jaccard embree: return code 0, artifact written, elapsed 447.63 seconds
```

This strengthens the current-side release-candidate evidence, but it does not
make the cross-version comparison complete because most v1.0 paired rows remain
missing.

## Verdict

Goal1718 is:

```text
accept-with-boundary
```

Accepted:

- The v1.0 baseline checkout exists and builds Embree/OptiX on the pod.
- The raw runner completed all 56 planned invocations.
- The current candidate produced artifacts for 28/28 planned Goal1660
  invocations.
- Four v1.0 baseline rows produced artifacts.

Boundary:

- The full Goal1660 v1.6.11-versus-v1.0 timed comparison is incomplete.
- 24 v1.0 rows require a baseline-compatible command adapter or explicit
  unsupported-row classification before any complete cross-version matrix can
  be claimed.
- No public speedup wording, release/tag action, or v1.8/v2.0 readiness claim is
  authorized by this attempt.

Release readiness remains:

```text
needs-more-evidence
```
