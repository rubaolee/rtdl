# Goal1956 - L4 RawKernel Control-App OptiX v8.0 Pod Evidence

Status: pass-with-mixed-performance
Date: 2026-05-14
Pod: `root@213.173.105.14 -p 20710`
GPU: NVIDIA L4, driver 550.127.05
Source label: `98fb1378fe615141119ee134a9fade880e45f3bb`

## Setup Correction

The first pod attempt was incomplete because I stopped at "OptiX SDK missing." That was too early.

The actual fix was:

1. Use the repo-local key `id_ed25519_rtdl_codex`; `~/.ssh/id_ed25519` was rejected.
2. Install missing validation/runtime dependencies: `cupy-cuda12x`, `libgeos-dev`, and `pkg-config`.
3. Clone NVIDIA's official OptiX SDK source-release headers:
   - `git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-sdk.git /root/vendor/optix-sdk-v8.0.0`
4. Build RTDL OptiX with `OPTIX_PREFIX=/root/vendor/optix-sdk-v8.0.0`.

The newer `NVIDIA/optix-dev` header repo currently exposes OptiX 9.1 headers (`OPTIX_VERSION 90100`, ABI 118), which are not compatible with this pod's R550 driver. Patched 9.1 headers were also rejected (`Unsupported ABI version` or function-table-size mismatch), so the correct path is official v8.0 headers.

## Command Shape

The successful run used:

```bash
OUT_DIR=docs/reports/goal1956_rawkernel_control_app_pod_optix_v800 \
DB_COPIES=100000 \
GRAPH_COPIES=1000 \
POLYGON_COPIES=2048 \
REPEATS=3 \
WARMUPS=1 \
STEP_TIMEOUT_SECONDS=1800 \
OPTIX_PREFIX=/root/vendor/optix-sdk-v8.0.0 \
RTDL_SOURCE_COMMIT_LABEL=98fb1378fe615141119ee134a9fade880e45f3bb \
bash scripts/goal1956_rawkernel_control_app_pod_runner.sh
```

## Results

Times are median wall-clock seconds over three repeats after one warmup.

| App | Scale | Candidate backend | v1.8 median s | v2 CuPy RawKernel median s | v2 / v1.8 | Match |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| `database_analytics` | 100,000 copies | `cpu_all_pairs` | 5.375620 | 1.095086 | 0.204x | true |
| `graph_analytics` | 1,000 copies | `cpu_all_pairs` | 10.401499 | 0.000031 | 0.000003x | true |
| `polygon_pair_overlap_area_rows` | 2,048 copies | `optix` | 0.173896 | 2.626271 | 15.103x | true |
| `polygon_set_jaccard` | 2,048 copies | `optix` | 0.138648 | 2.486790 | 17.936x | true |

## Interpretation

This is real pod evidence that the four former-control apps can run as Python+CuPy RawKernel+RTDL versions and match their v1.8 Python+RTDL oracles.

The performance story is mixed:

- `database_analytics` is a strong positive v2 partner continuation case: roughly 4.9x faster than v1.8 Python+RTDL.
- `graph_analytics` is a strong positive for the authored replicated-graph summary, but the number must be described carefully: this is a closed-form partner continuation, not proof of generic graph traversal acceleration.
- The two polygon rows remain negative even with OptiX candidate discovery. The v2 path is correct, but host-side candidate/mask construction plus the RawKernel continuation do not beat the compact v1.8 Python+RTDL summary at this scale on the L4 pod.

## Claim Boundary

This evidence still does not authorize:

- v2.0 release;
- broad RT-core speedup claims;
- whole-app acceleration claims;
- generic "CuPy RawKernel makes RTDL apps faster" claims;
- polygon speedup claims.

It does authorize a narrower statement: the v2 RawKernel control-app path is functional on CUDA hardware, preserves v1.8 oracle results for the measured apps, and has positive measured evidence for DB and graph continuation workloads while exposing negative evidence for the two polygon workloads.

## Artifacts

- `docs/reports/goal1956_rawkernel_control_app_pod_optix_v800/database_analytics.json`
- `docs/reports/goal1956_rawkernel_control_app_pod_optix_v800/graph_analytics.json`
- `docs/reports/goal1956_rawkernel_control_app_pod_optix_v800/polygon_pair_overlap_area_rows.json`
- `docs/reports/goal1956_rawkernel_control_app_pod_optix_v800/polygon_set_jaccard.json`
- `docs/reports/goal1956_rawkernel_control_app_pod_optix_v800/summary.json`

## Follow-Up

The next engineering work is not "install OptiX"; that is solved for this pod class by using official v8.0 headers. The next work is to analyze and reduce the polygon host-side and continuation overhead, or to document the polygon rows as negative v2 evidence for this RawKernel implementation.
