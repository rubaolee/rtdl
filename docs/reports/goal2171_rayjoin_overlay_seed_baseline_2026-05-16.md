# Goal2171 RayJoin Overlay Seed Baseline

Date: 2026-05-16

Status: bounded overlay-seed pod baseline recorded.

## Purpose

Goals 2163 through 2169 improved the RayJoin line-segment-intersection lane by adding prepared OptiX build reuse, count-first compact output, and conservative device-side candidate filtering.

Goal2171 moves beyond the isolated LSI row and records a first bounded RayJoin-style overlay dependency slice. The goal is not to reproduce the full RayJoin paper, but to measure whether RTDL can accelerate the overlay seed path on public CDB slices while preserving exact row parity.

## Workload

The measured runner case is:

- `overlay_county128_soil128`
- county slice: `br_county_start0_count128.cdb`
- soil slice: `br_soil_start0_count128.cdb`
- workload label: `overlay_seed`

The row emits the bounded overlay dependency seed output used by the RTDL RayJoin exploration. It is a stronger signal than the LSI-only rows because it exercises polygon/shape relation work, not only segment-pair intersection.

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
- RTDL runner commit: `7e4f440425b8e19caed147097945504b47aa9b81`

Collected artifact:

- `docs/reports/goal2171_rayjoin_overlay_seed_baseline_pod_2026-05-16.json`

## Result

The run used one warmup and five measured repeats.

| Case | Output rows | CPU sec | Embree sec | OptiX sec | CPU vs Embree | CPU vs OptiX | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `overlay_county128_soil128` | 14,036 | 0.152511 | 0.022165 | 0.025159 | 6.880x | 6.061x | all pass |

The hot OptiX repeats were stable around 25 ms:

- `0.025233`
- `0.025202`
- `0.025159`
- `0.024982`
- `0.025148`

## Interpretation

This is a useful RayJoin progress signal:

- both Embree and OptiX preserve row parity against the CPU Python reference
- both RTDL backends accelerate the overlay seed path by about 6x over the measured CPU reference
- OptiX is still slower than Embree on this slice, so the result does not yet support an RTX-over-CPU-RT claim for the overlay seed path

The likely reason is setup and output shape, not RT traversal capability alone. The current OptiX shape-pair relation path still rebuilds or repacks more relation state per call than the prepared LSI path, and it returns a bounded relation table rather than a more compact prepared/streamed overlay summary.

The next engineering target should therefore mirror the Goal2163 LSI improvement:

- add a prepared/reused generic OptiX shape-pair relation surface
- reuse right-side shape geometry and acceleration state across repeated overlay-seed calls
- keep Python-level overlay semantics outside the native engine
- keep the native ABI generic, for example around shape-pair relation rather than RayJoin-specific names

## Why This Still Does Not Match RayJoin Paper Speedups

This goal measures a bounded RTDL overlay-seed slice, not the complete RayJoin system. Remaining differences include:

- no full RayJoin paper-scale protocol yet
- no complete end-to-end overlay operator comparison yet
- no specialized full-system RayJoin baseline or paper implementation comparison yet
- no prepared/reused OptiX shape-pair relation path yet
- no stronger non-RT GPU spatial-prefilter baseline for this overlay-seed row yet

## Claim Boundary

This goal authorizes:

- a narrow statement that RTDL Embree and OptiX both accelerate the measured bounded overlay-seed row over the CPU Python reference
- a narrow statement that the measured OptiX overlay-seed row is RT-core-accelerated and parity-clean on this slice
- using the result to prioritize a prepared/reused generic OptiX shape-pair relation path

This goal does not authorize:

- full RayJoin paper reproduction
- broad RT-core speedup claims
- claims that OptiX beats Embree on overlay seed
- v2.0 release authorization
- claims against stronger CuPy or CUDA spatial-prefilter baselines that have not been implemented and measured yet

## Verdict

Goal2171 is accepted as a bounded overlay-seed baseline. It proves that RTDL can accelerate this RayJoin-style dependency row over the CPU Python reference, but it also shows that the OptiX overlay path needs prepared/reused shape-pair relation state before it can make the same kind of strong GPU advantage claim that the LSI lane started to show after Goal2163 and Goal2165.
