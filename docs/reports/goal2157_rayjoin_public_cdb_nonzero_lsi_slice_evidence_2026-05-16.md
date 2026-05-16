# Goal2157 RayJoin Public-CDB Nonzero LSI Slice Evidence

Date: 2026-05-16

Status: pod evidence collected; external review pending.

## Purpose

Goal2153 proved that the RayJoin v2 external-CDB adapter can run public sample CDB files, but its first county/soil LSI prefix slice had zero intersections. Goal2157 searches for and measures bounded public RayJoin sample slices with real cross-dataset line-segment intersections.

This gives the RayJoin performance work a better LSI fight than a zero-hit row.

## Method

The pod used the downloaded public RayJoin `br_county` and `br_soil` CDB files from Goal2153. A bounded offset search scanned 48-chain county/soil windows over the first 4,096 chains with Embree, looking for nonzero cross-dataset intersections.

Best found 48-chain slice:

- county start: `256`
- soil start: `256`
- county chains: `48`
- soil chains: `48`
- left segments: `3,506`
- right segments: `815`
- intersections: `34`

Larger follow-up slices at the same offset:

- count `128`: 6,064 left segments, 2,034 right segments, 56 intersections
- count `192`: 9,216 left segments, 2,823 right segments, 85 intersections

The slices are bounded derived inputs, not exact RayJoin paper-scale inputs.

## Pod Environment

Pod access:

- `root@157.157.221.29`
- SSH port: `24240`
- Accepted local key: `id_ed25519_rtdl_codex`

Runtime facts:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 580.65.06
- CUDA: 12.8
- OptiX SDK: v8.1.0
- Embree: 4.3.0
- RTDL commit on pod: `9931585362e0e27ccf1a4e657afc7fd670209041`

## Artifacts

Collected artifacts:

- `docs/reports/goal2157_rayjoin_public_cdb_nonzero_lsi_slice_pod_2026-05-16.json`
- `docs/reports/goal2157_rayjoin_public_cdb_nonzero_lsi_larger_slices_pod_2026-05-16.json`

All measured rows use one warmup and five measured repeats. Each backend preserved parity against the CPU Python reference.

## Results

Values below are median app-level backend seconds. Ratios above `1.0x` favor OptiX.

| Case | Rows | CPU sec | Embree sec | OptiX sec | OptiX vs CPU | OptiX vs Embree | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `count48` | 34 | 0.005836 | 0.016302 | 0.006254 | 0.93x | 2.61x | all pass |
| `count128` | 56 | 0.011694 | 0.022744 | 0.010525 | 1.11x | 2.16x | all pass |
| `count192` | 85 | 0.016114 | 0.029917 | 0.003110 | 5.18x | 9.62x | all pass |

## Interpretation

The first nonzero 48-chain slice is still too small for a strong OptiX-vs-CPU claim, but it already shows OptiX beating Embree on this LSI shape.

The 128-chain slice is the first mild OptiX win over CPU.

The 192-chain slice is the important result: same offset, more chain context, 85 true intersections, all parity true, and warm OptiX is substantially faster than both CPU and Embree. This is still bounded derived-input evidence, but it is a much healthier RayJoin LSI experiment than the zero-hit prefix slice.

The Embree shared-endpoint fix from Goal2155 remains in effect for these measurements and all rows pass parity.

## Claim Boundary

This goal authorizes:

- bounded public-sample RayJoin LSI evidence with nonzero cross-dataset intersections
- a narrow statement that warm OptiX is faster than CPU and Embree on the measured `count192` bounded slice
- continued development of RayJoin public-CDB benchmark runners

This goal does not authorize:

- full RayJoin paper reproduction
- paper-scale performance claims
- broad RT-core speedup claims
- whole-app RayJoin acceleration claims
- v2.0 release authorization

## Next Work

1. Turn the one-off offset search and slice timing into a committed reusable runner.
2. Add CUDA/CuPy non-RT baselines for the same nonzero LSI slices.
3. Search for larger nonzero county/soil and other public RayJoin family slices that run in seconds.
4. Decide whether RayJoin LSI should become a first-class v2.0 public benchmark row after independent review.

## Verdict

Goal2157 is accepted as a stronger bounded RayJoin LSI development result. It is not release evidence by itself.
