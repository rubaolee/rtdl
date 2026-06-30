# Goal2962: Large-Scale v2.5 Stress Probe

Date: 2026-06-01
Status: pod stress probe passed

## Purpose

Goal2959 showed that the current v2.5 canonical packet has zero performance
targets at the packet scale. Goal2962 checks whether three high-risk
RT-core-plus-partner paths still behave well at larger scale:

- RTNN ranked summaries at 262,144 query/search points.
- Exact Hausdorff/X-HD at 16,384 by 16,384 points.
- RT-DBSCAN grouped-stream continuation at 262,144 points.

This is stress evidence only. It is not a release authorization and it does not
convert internal ratios into public speedup claims.

## Pod Evidence

Pod target: `root@69.30.85.171 -p 22167`

Source commit: `8deb21bea3930830ad03d3d7410356c786af5479`

Artifacts:

- `docs/reports/goal2962_large_scale_stress_pod/goal2962_rtnn_262k.json`
- `docs/reports/goal2962_large_scale_stress_pod/goal2962_hausdorff_16k.json`
- `docs/reports/goal2962_large_scale_stress_pod/goal2962_rt_dbscan_262k.json`

The enclosing SSH summary wrapper printed a harmless trailing here-doc `NameError`
after all three JSON payloads had already been written and summarized. The
individual workload artifacts are the source of truth, and each reports
`status: pass`, clean source, and the expected claim boundaries.

## Results

### RTNN

262,144 query/search points, radius `0.02`, `k=50`, repeat `5`.

| Distribution | Query batches | RTDL sec | CuPy sec | CuPy/RTDL ratio |
| --- | ---: | ---: | ---: | ---: |
| uniform | `4` | `0.001075` | `0.003610` | `3.359x` |
| clustered | `4` | `0.212251` | `0.439508` | `2.071x` |
| shell | `4` | `0.031294` | `0.144215` | `4.608x` |

All three rows match the same-contract CuPy grid opponent, use the graph-safe
`65536` query chunk, and report `upload_sec: 0.0` in the native phase.

### Hausdorff/X-HD

16,384 by 16,384 exact directed Hausdorff, repeat `5`.

| Method | Median sec | Notes |
| --- | ---: | --- |
| RTDL/OptiX reduced nearest witness | `0.014730` | exact, RT-core accelerated |
| CuPy grouped grid rawkernel | `0.015727` | exact CUDA-core opponent |

RTDL/CuPy ratio: `0.937x`. The result matches the exact baseline with zero
distance error. This supports keeping the target-8192 reduced RT path, but it
does not authorize a claim to beat X-HD or an optimized CUDA implementation in
general.

### RT-DBSCAN

262,144 clustered 3D points, repeat count `3`.

| Path | Tail median sec |
| --- | ---: |
| Prepared CuPy grid | `5.479164` |
| RT count prepared grid | `3.066458` |
| RTDL grouped stream + CuPy components | `1.196323` |

Grouped-stream speedup versus the prepared CuPy grid opponent: `4.580x`.
The grouped-stream path remains RT-core accelerated, avoids materializing
neighbor rows and the full directed adjacency stream, and preserves signature
matching.

## Boundary

Goal2962 strengthens the internal engineering confidence that the current v2.5
route choices are not only short-row wins. It does not authorize:

- v2.5 release or release tag action;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true zero-copy wording;
- package-install wording;
- Triton preview auto-selection;
- paper reproduction claims;
- app-specific native engine customization.
