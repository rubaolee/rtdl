# Goal1956 - L4 RawKernel Control-App Partial Pod Evidence

Status: partial-no-optix-sdk
Date: 2026-05-14
Pod: `root@213.173.105.14 -p 20710`
GPU: NVIDIA L4, driver 550.127.05
Source label: `e0a3d6d22dc5e27fc1c6987879227dfe37130f77`

## What Happened

The pod was reachable with the repo-local `id_ed25519_rtdl_codex` key. `~/.ssh/id_ed25519` was rejected by the pod, and the first archive also exposed a Windows CRLF issue in the new shell runner. Goal1956 now has a `.gitattributes` LF rule for the runner.

CuPy installed and ran successfully on the L4. The CPU/oracle validation path initially failed because `libgeos_c` was missing; installing `libgeos-dev` and `pkg-config` fixed that path and the focused Goal1953/Goal1955 tests passed.

The OptiX SDK was not available at `/root/vendor/optix-sdk/include/optix.h`, and a search under `/root`, `/opt`, and `/usr/local` did not find `optix.h`. Therefore, polygon rows could not be measured with RTDL OptiX candidate discovery on this pod.

## Results Collected

These are useful partial artifacts, not release-grade polygon/whole-app evidence.

| App | Scale | Candidate backend | v1.8 median s | v2 CuPy RawKernel median s | v2 / v1.8 | Match |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| `database_analytics` | 100,000 copies | `cpu_all_pairs` | 5.058332 | 1.037488 | 0.205x | true |
| `graph_analytics` | 1,000 copies | `cpu_all_pairs` | 9.907824 | 0.000032 | 0.000003x | true |
| `polygon_pair_overlap_area_rows` | 512 copies | `cpu_all_pairs` | 0.044129 | 1.624540 | 36.813x | true |
| `polygon_set_jaccard` | 512 copies | `cpu_all_pairs` | 0.031311 | 0.987839 | 31.549x | true |

Additional v2-only sanity probe:

| App | Scale | v2 median s | Note |
| --- | ---: | ---: | --- |
| `graph_analytics` | 1,000,000 copies | 0.000038 | Confirms the closed-form graph RawKernel path remains tiny at large copy count. |

## Interpretation

The L4 run confirms that the Python+CuPy RawKernel partner path works on real CUDA hardware and preserves the v1.8 Python+RTDL oracle for all four former-control apps at the measured scales.

The performance split is clear:

- DB and graph benefit strongly because their non-RT continuation is a compact aggregation.
- Polygon rows are much slower when candidate discovery is `cpu_all_pairs`; the RawKernel continuation is not the whole app, and this is exactly why the next accepted evidence must use `--candidate-backend optix`.

## Claim Boundary

This artifact does not authorize:

- v2.0 release;
- whole-app speedup claims;
- broad RT-core speedup claims;
- polygon speedup claims;
- proof that RTDL+CuPy accelerates arbitrary RawKernel code.

The missing evidence is specific: rerun Goal1956 on a pod image with the OptiX SDK headers available, using polygon `--candidate-backend optix`.

## Artifacts

- `docs/reports/goal1956_rawkernel_control_app_pod_no_optix/database_analytics.json`
- `docs/reports/goal1956_rawkernel_control_app_pod_no_optix/graph_analytics.json`
- `docs/reports/goal1956_rawkernel_control_app_pod_no_optix/graph_analytics_1m_v2_only.json`
- `docs/reports/goal1956_rawkernel_control_app_pod_no_optix/polygon_pair_overlap_area_rows.json`
- `docs/reports/goal1956_rawkernel_control_app_pod_no_optix/polygon_set_jaccard.json`
- `docs/reports/goal1956_rawkernel_control_app_pod_no_optix/summary.json`
