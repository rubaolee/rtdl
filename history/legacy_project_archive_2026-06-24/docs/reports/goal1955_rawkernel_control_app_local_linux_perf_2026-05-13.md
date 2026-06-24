# Goal1955 - Local Linux CuPy RawKernel Control-App Performance Smoke

Status: local-linux-smoke-complete
Date: 2026-05-13
Scope: v2.0 former-control apps implemented as Python+CuPy RawKernel+RTDL continuations, compared against v1.8 Python+RTDL without user C/C++ extension per the explicit user decision.

## Boundary

This is useful development evidence, not v2.0 release performance evidence. It ran on the local Linux GTX 1070 host (`192.168.1.20`) using a temporary source archive and a disposable `cupy-cuda12x` target install under `/tmp/rtdl_cupy_site`. The source archive has no `.git` directory, so the per-run `source_commit` field is empty in these local artifacts.

The comparison is intentionally not absolutely fair: v1.8 is Python+RTDL with no user native extension, while v2.0 uses Python+CuPy RawKernel+RTDL. That is the user-approved v2 definition for the four former-control rows, but whole-release claims still need pod evidence and external review.

## Implementation Correction

The first graph RawKernel used seven contended global atomics per copy. That scaled badly and timed out locally. Goal1955 corrected the graph continuation to write the replicated graph summary in closed form from one thread:

- `discovered_edge_count = 2 * copies`
- `discovered_vertex_count = 2 * copies`
- `triangle_count = copies`
- `touched_vertex_count = 3 * copies`
- `visible_edge_count = copies`
- `blocked_edge_count = 3 * copies`

This preserves the authored graph summary contract and removes artificial atomic contention from the user-side RawKernel continuation.

## Local Results

Times are median wall-clock seconds over three repeats after one warmup unless noted.

| App | Scale | v1.8 Python+RTDL median s | v2 Python+CuPy RawKernel+RTDL median s | v2 / v1.8 | Match |
| --- | ---: | ---: | ---: | ---: | --- |
| `database_analytics` | 100,000 copies | 7.166047 | 1.629000 | 0.227x | true |
| `graph_analytics` | 1,000 copies | 17.389514 | 0.000061 | 0.000004x | true |
| `polygon_pair_overlap_area_rows` | 256 copies | 0.031562 | 0.611965 | 19.389x | true |
| `polygon_set_jaccard` | 256 copies | 0.027710 | 0.407726 | 14.714x | true |

Additional graph v2-only probe:

| App | Scale | v2 median s | Note |
| --- | ---: | ---: | --- |
| `graph_analytics` | 1,000,000 copies | 0.000068 | v1.8 oracle at this scale exceeded the local timeout; v2-only probe verifies the cleaned continuation scales after removing atomics. |

## Interpretation

The local Linux smoke supports three conclusions:

1. The CuPy RawKernel partner path is real: it compiles and runs on a CUDA GPU outside the pod.
2. The v2 continuation can produce large speedups when the non-RT portion is a compact aggregation (`database_analytics`, `graph_analytics`).
3. The polygon rows remain dominated by candidate/mask construction when using `cpu_all_pairs` candidate discovery locally. These rows require pod runs using the RTDL OptiX candidate backend before interpreting their v2 performance.

## Artifacts

- `docs/reports/goal1955_local_linux_database_100k_cupy_rawkernel_2026-05-13.json`
- `docs/reports/goal1955_local_linux_graph_1k_cupy_rawkernel_2026-05-13.json`
- `docs/reports/goal1955_local_linux_graph_1m_v2_only_cupy_rawkernel_2026-05-13.json`
- `docs/reports/goal1955_local_linux_polygon_pair_256_cupy_rawkernel_2026-05-13.json`
- `docs/reports/goal1955_local_linux_polygon_jaccard_256_cupy_rawkernel_2026-05-13.json`

## Next Gate

Pod evidence is still needed for release-grade timing:

- run the four former-control apps with `--partner cupy`;
- run polygon rows with `--candidate-backend optix` so RTDL supplies RT-accelerated candidate discovery;
- use seconds-scale workloads and bounded timeouts;
- record GPU, driver, CUDA, source commit, command lines, and output artifact hashes;
- submit the pod artifacts for independent Gemini/Claude review before adding any broad v2.0 performance claim.
