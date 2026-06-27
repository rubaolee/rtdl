# Goal2165 Count-First OptiX LSI Output

Date: 2026-05-16

Status: implemented, pod-validated, external review pending.

## Purpose

Goal2163 proved that prepared OptiX build-side reuse fixes the biggest one-shot LSI overhead. It also exposed the next generic bottleneck: the segment-pair-intersection launch reserved output space for every possible left/right pair, even when the final hit count was tiny.

Goal2165 changes the generic OptiX LSI launch to a count-first candidate output protocol:

1. run the same OptiX traversal once with no output buffer and count AABB candidates
2. allocate only the counted candidate capacity
3. rerun traversal and write candidate rows into the compact output buffer
4. keep the existing host exact-refine step for correctness

This keeps the native engine app-agnostic. The primitive remains segment-pair intersection; no RayJoin-specific logic was added.

## What Changed

`src/native/optix/rtdl_optix_workloads.cpp` now uses `launch_candidate_pass` inside the generic segment-pair-intersection helper.

Before Goal2165:

- output capacity was `left_count * right_count`
- sparse workloads still reserved huge device buffers
- the prepared path could be competitive but carried unnecessary allocation pressure

After Goal2165:

- first pass counts emitted AABB candidates
- second pass allocates only `gpu_count` candidate records
- host exact refinement remains unchanged
- the public Python API and app-visible row contract remain unchanged

## Pod Evidence

Pod access:

- `root@157.157.221.29`
- SSH port: `24240`
- Accepted local key: `id_ed25519_rtdl_codex`

Runtime facts:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 580.65.06
- CUDA: 12.8
- OptiX SDK: v8.1.0
- RTDL runner commit: `c204698dd85cdf8f2df263a4f5100429f9798049`
- CuPy package: `cupy-cuda12x 14.0.1`

Collected artifacts:

- `docs/reports/goal2165_rayjoin_count_first_optix_lsi_count192_pod_2026-05-16.json`
- `docs/reports/goal2165_rayjoin_count_first_optix_lsi_count256_pod_2026-05-16.json`
- `docs/reports/goal2165_rayjoin_count_first_optix_lsi_count384_pod_2026-05-16.json`

## Results

All rows below use the same public CDB slices and five measured repeats after one warmup. The comparison is against the same-runner CuPy CUDA-core brute-force baseline from Goal2161.

| Case | Candidate pairs | Rows | Prepared OptiX sec | CuPy brute-force sec | Prepared OptiX vs CuPy | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `lsi_county256_soil256_count192` | 26,016,768 | 85 | 0.010135 | 0.010791 | 1.065x | all pass |
| `lsi_county256_soil256_count256` | 44,938,225 | 88 | 0.013383 | 0.016580 | 1.239x | all pass |
| `lsi_county256_soil256_count384` | 83,323,218 | 116 | 0.017004 | 0.026702 | 1.570x | all pass |

## Interpretation

This is the first RayJoin LSI public-CDB result in this lane where the RTDL/OptiX path beats the measured CuPy CUDA-core baseline across all tested bounded nonzero slices.

The key performance mechanism is not an app shortcut. It is a generic output protocol:

- keep build-side OptiX acceleration reuse from Goal2163
- stop reserving full Cartesian output memory
- keep exact host refinement for correctness
- make sparse candidate emission cheaper enough that RT traversal can outrun a flat CUDA-core brute-force kernel

The result also explains why Goal2161 lost: the one-shot path had both build-side setup overhead and full-pair output allocation pressure. Goal2163 fixed the first problem; Goal2165 fixed the second.

## Claim Boundary

This goal authorizes:

- a narrow statement that count-first output improves prepared OptiX LSI on bounded public CDB RayJoin slices
- a narrow statement that prepared OptiX beats the measured same-runner CuPy brute-force baseline on the three recorded public CDB LSI slices
- a v2.0 design lesson that generic prepared primitives need compact or streaming output protocols

This goal does not authorize:

- full RayJoin paper reproduction
- a broad claim that OptiX always beats CuPy
- a broad claim that RT cores accelerate every RayJoin workload
- v2.0 release authorization

## Remaining Work

1. Add larger public CDB slices once CPU parity remains feasible and output capacity stays bounded.
2. Compare against a stronger CuPy spatial-prefilter baseline, not only flat brute force.
3. Consider exposing a public bounded-output metadata API for users who want streaming partial rows instead of materialized complete rows.
4. Ask external review to verify the app-agnostic boundary and the claim wording.

## Verdict

Goal2165 is accepted as a strong v2.0 performance-design improvement. It turns RayJoin LSI from a correctness-only integration example into a credible narrow RTDL/OptiX speedup case against a strong non-RT CUDA-core partner baseline, while preserving app-agnostic native engine design.
