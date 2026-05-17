# Goal2163 Prepared OptiX LSI Build Reuse

Date: 2026-05-16

Status: implemented, pod-validated, external review pending.

## Purpose

Goal2161 showed an important negative result: for bounded public CDB RayJoin line-segment-intersection slices, a simple CuPy CUDA-core brute-force kernel beat the one-shot RTDL/OptiX path.

Goal2163 addresses the most obvious RTDL-side design problem without adding app-specific native logic. The OptiX engine now exposes a generic prepared segment-pair-intersection surface that can keep the build-side segment array and acceleration structure alive across repeated query launches.

This is a reusable RTDL primitive shape, not a RayJoin-specific native continuation.

## What Changed

The OptiX native surface now includes:

- `rtdl_optix_prepare_segment_pair_intersection`
- `rtdl_optix_run_prepared_segment_pair_intersection`
- `rtdl_optix_destroy_prepared_segment_pair_intersection`

The Python runtime wraps the handle as `PreparedOptixSegmentPairIntersection` and exposes `prepare_segment_pair_intersection_optix(right_segments)`.

The RayJoin public CDB runner gained an `optix_prepared_lsi` backend that:

- prepares the right/build-side segment set once
- reuses the OptiX GAS and uploaded build-side device buffers across repeats
- records `prepare_elapsed_sec` separately from repeated traversal time
- keeps the same output schema as CPU, Embree, one-shot OptiX, and CuPy
- checks parity against the CPU Python reference

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
- RTDL runner commit: `3b1e9d86d024497b7772b807ac309e6c41b65219`
- CuPy package: `cupy-cuda12x 14.0.1`

Collected artifacts:

- `docs/reports/goal2163_rayjoin_prepared_optix_lsi_count192_pod_2026-05-16.json`
- `docs/reports/goal2163_rayjoin_prepared_optix_lsi_count256_pod_2026-05-16.json`
- `docs/reports/goal2163_rayjoin_prepared_optix_lsi_count384_pod_2026-05-16.json`

## Results

All rows below use five measured repeats after one warmup. The `prepare` column is the one-time prepared OptiX build-side setup cost and is intentionally not folded into the repeat-traversal median.

| Case | Candidate pairs | Rows | One-shot OptiX sec | Prepared OptiX prepare sec | Prepared OptiX repeat sec | CuPy brute-force sec | Prepared vs one-shot | Prepared vs CuPy | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `lsi_county256_soil256_count192` | 26,016,768 | 85 | 0.015259 | 0.011712 | 0.010752 | 0.010711 | 1.419x | 0.996x | all pass |
| `lsi_county256_soil256_count256` | 44,938,225 | 88 | n/a | 0.724443 | 0.015056 | 0.016440 | n/a | 1.092x | all pass |
| `lsi_county256_soil256_count384` | 83,323,218 | 116 | n/a | 0.783656 | 0.022392 | 0.026799 | n/a | 1.197x | all pass |

## Interpretation

The Goal2161 loss was real, but it was not the end of the story. One-shot OptiX was paying too much per app call, especially by rebuilding and re-uploading the build-side state.

Goal2163 shows that a generic prepared segment-pair-intersection handle fixes that specific design problem:

- on `count192`, prepared OptiX removes most of the one-shot overhead and reaches parity with CuPy
- on `count256`, prepared OptiX is faster than CuPy by about `1.09x`
- on `count384`, prepared OptiX is faster than CuPy by about `1.20x`

The trend is consistent with the expected RTDL/OptiX shape: build-side reuse matters, and the traversal path becomes more competitive as candidate-pair count grows.

## Design Lesson

For v2.0 user programs, RTDL should not expose only one-shot calls for expensive geometric primitives. It needs reusable prepared objects when one side of a relation is stable across many queries.

The engine-side primitive should remain generic:

- segment pair intersection
- prepared build-side geometry
- repeated query launches
- explicit output capacity and parity contract

The app layer may call that primitive for RayJoin, overlay, filtering, or any other workload that can phrase work as repeated segment-pair intersection.

## Claim Boundary

This goal authorizes:

- a narrow statement that prepared OptiX build-side reuse improves RTDL/OptiX RayJoin LSI performance on bounded public CDB slices
- a narrow statement that prepared OptiX reaches CuPy parity at `count192` and beats the measured CuPy brute-force baseline at `count256` and `count384`
- a design conclusion that prepared/reusable primitive handles are necessary for v2.0 performance credibility

This goal does not authorize:

- full RayJoin paper reproduction
- a broad claim that OptiX always beats CuPy
- a broad RT-core speedup claim for all spatial joins
- v2.0 release authorization

## Next Work

1. Extend the public CDB RayJoin matrix to larger slices while keeping CPU parity feasible.
2. Add bounded or streaming output capacity so the runner does not allocate full pair-count output buffers when the hit count is sparse.
3. Compare against a CuPy spatial-prefilter variant, not only brute-force all-pairs.
4. Run the same prepared primitive through a reviewed learner-facing example once the public claim wording is externally accepted.

## Verdict

Goal2163 is accepted as a v2.0 performance-design improvement. It turns the Goal2161 negative result into a more precise engineering lesson: RTDL/OptiX needs prepared primitive reuse, and with that reuse the RT path becomes competitive with a strong CuPy non-RT CUDA-core baseline on larger bounded public CDB LSI slices.
