# Goal2169 OptiX LSI Device Candidate Filter

Date: 2026-05-16

Status: implemented and pod-validated.

## Purpose

Goal2165 fixed the largest RayJoin LSI output problem by using count-first compact output. Goal2169 tests the next step toward a RayJoin-style RT pipeline: reject obvious non-intersections on the GPU before candidates reach the host exact-refine stage.

The change remains generic. It is still the OptiX `segment_pair_intersection` primitive, not a RayJoin-specific native engine path.

## What Changed

The OptiX segment-pair-intersection any-hit program now runs a conservative device-side segment-intersection candidate check before incrementing `output_count`.

The check is deliberately conservative:

- obvious non-intersections are rejected on the GPU
- near-degenerate or nearly parallel cases remain candidates
- host-side `exact_segment_intersection` remains the final correctness authority

This preserves the existing exact-refinement contract while reducing candidate traffic when the device can safely reject a pair.

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
- RTDL runner commit: `3ec61f3971c37c38c7560789c7e87f1233d7358b`
- CuPy package: `cupy-cuda12x 14.0.1`

Collected artifacts:

- `docs/reports/goal2169_rayjoin_device_filter_optix_lsi_count192_pod_2026-05-16.json`
- `docs/reports/goal2169_rayjoin_device_filter_optix_lsi_count384_pod_2026-05-16.json`
- `docs/reports/goal2169_rayjoin_device_filter_optix_lsi_count512_pod_2026-05-16.json`

## Results

All rows below use five measured repeats after one warmup.

| Case | Candidate pairs | Rows | Prepared OptiX sec | CuPy brute-force sec | Prepared OptiX vs CuPy | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `lsi_county256_soil256_count192` | 26,016,768 | 85 | 0.009808 | 0.010792 | 1.100x | all pass |
| `lsi_county256_soil256_count384` | 83,323,218 | 116 | 0.016940 | 0.026953 | 1.591x | all pass |
| `lsi_county256_soil256_count512` | 136,411,275 | 269 | 0.021567 | 0.040624 | 1.884x | all pass |

## Interpretation

Goal2169 is a correctness-preserving refinement, not a dramatic new speedup by itself.

The main RayJoin LSI performance gains still come from:

1. prepared build-side OptiX reuse
2. count-first compact output

The device-side candidate filter gives a modest improvement on smaller slices and keeps the larger-slice result essentially stable. That is still useful: it moves more of the LSI pipeline toward GPU-side filtering while keeping the host exact-refine guardrail.

## Why This Still Does Not Match RayJoin Paper Speedups

This result narrows one gap but does not close the whole RayJoin system gap. We are still measuring a bounded LSI primitive against a strong same-runner CuPy baseline, not reproducing the full RayJoin overlay pipeline against the paper's full baseline suite.

Remaining gaps include:

- full polygon overlay pipeline, not only LSI
- stronger non-RT baselines such as grid/prefiltered CuPy
- larger paper-scale dataset protocols
- more GPU-side exact refinement or exact-output construction
- end-to-end PIP plus LSI plus overlay composition

## Claim Boundary

This goal authorizes:

- a narrow statement that the OptiX LSI any-hit path now performs conservative device-side candidate filtering
- a narrow statement that parity was preserved on the three recorded public CDB slices
- a narrow statement that prepared OptiX still beats the same-runner CuPy brute-force baseline on those slices

This goal does not authorize:

- full RayJoin paper reproduction
- broad RT-core speedup claims
- v2.0 release authorization
- claims against stronger CuPy spatial-prefilter baselines

## Verdict

Goal2169 is accepted as a safe incremental RayJoin LSI improvement. It confirms that conservative GPU-side candidate filtering can be added without breaking parity, but the evidence also shows that prepared reuse and compact output remain the dominant performance mechanisms.
