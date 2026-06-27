# Goal1968 Pod Control Perf After Partner Algebra

Date: 2026-05-14

Status: pod evidence, release still blocked

## Environment

Pod: `root@213.173.109.6 -p 31938`

GPU: NVIDIA RTX 2000 Ada Generation, driver `565.57.01`, CUDA runtime `12.7`

Source commit label: `ccd93252f11fd4e0b2583ffd264690ef5d0d5bb4`

Installed during setup:

- `cupy-cuda12x` `14.0.1`
- `cmake`, `build-essential`, `ninja-build`, `python3-pip`
- `libgeos-dev`
- `libembree-dev`

OptiX status: blocked. The pod did not contain `optix.h`, `libnvoptix`, or an
apt package for the OptiX SDK. `make build-optix
OPTIX_PREFIX=/root/vendor/optix-sdk` failed at the intended SDK-header gate.

Embree status: installed and loaded successfully as Embree `3.12.2`.

## What Ran

The main run used `scripts/goal1956_rawkernel_control_app_pod_runner.sh` with:

```text
RUN_POLYGON_WITH_OPTIX=0
DB_COPIES=100000
GRAPH_COPIES=1000
POLYGON_COPIES=2048
REPEATS=3
WARMUPS=1
```

This records the no-OptiX fallback behavior, not the final RT-core path. A
second targeted run measured the two polygon rows with `--candidate-backend
embree` after installing Embree.

## Results

| App | Candidate backend | Copies | v1.8 median s | v2 median s | v2/v1.8 | Correct |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `database_analytics` | `cpu_all_pairs` | 100000 | 8.074170 | 1.666684 | 0.206x | yes |
| `graph_analytics` | `cpu_all_pairs` | 1000 | 18.005865 | 0.000052 | 0.000003x | yes |
| `polygon_pair_overlap_area_rows` | `cpu_all_pairs` | 2048 | 0.281716 | 47.259478 | 167.756x | yes |
| `polygon_set_jaccard` | `cpu_all_pairs` | 2048 | 0.220814 | 27.553158 | 124.780x | yes |
| `polygon_pair_overlap_area_rows` | `embree` | 2048 | 0.283754 | 0.988480 | 3.484x | yes |
| `polygon_set_jaccard` | `embree` | 2048 | 0.241081 | 0.666283 | 2.764x | yes |

## Interpretation

The DB and graph rows remain positive under the user-approved
Python+CuPy-RawKernel+RTDL comparison boundary.

The graph result is still a closed-form authored continuation for this app, not
a reusable graph primitive. It must not be marketed as general graph traversal
acceleration.

The polygon rows show the core design problem. With `cpu_all_pairs`, v2 is
catastrophically slower because candidate construction hands the partner a huge
pair set. Embree candidate discovery removes most of that blow-up, but v2 is
still slower than v1.8 by `2.764x` to `3.484x`. That means the remaining
problem is the continuation contract itself: exact polygon/set summaries still
need a better reusable shape/set reduction, not an app-customized native engine
path.

## Claim Boundary

This run does not authorize:

- v2.0 release readiness;
- broad RT-core speedup;
- whole-app speedup claims;
- arbitrary PyTorch/CuPy acceleration claims;
- final polygon performance claims.

The next required hardware run needs a pod with the OptiX SDK installed at a
real `OPTIX_PREFIX`, or a repo-supported way to provision that SDK, so the
polygon candidate path can be measured with `--candidate-backend optix`.

## Artifacts

- `docs/reports/goal1968_pod_no_optix_control_perf/summary.json`
- `docs/reports/goal1968_pod_no_optix_control_perf/database_analytics.json`
- `docs/reports/goal1968_pod_no_optix_control_perf/graph_analytics.json`
- `docs/reports/goal1968_pod_no_optix_control_perf/polygon_pair_overlap_area_rows.json`
- `docs/reports/goal1968_pod_no_optix_control_perf/polygon_set_jaccard.json`
- `docs/reports/goal1968_pod_embree_polygon_control_perf.json`

