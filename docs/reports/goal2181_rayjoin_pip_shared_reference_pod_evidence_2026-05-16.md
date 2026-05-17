# Goal2181 RayJoin PIP Shared-Reference Pod Evidence

Date: 2026-05-16

Status: implemented and pod-validated.

## Purpose

Goal2181 rounds out the current RayJoin subproblem triad by adding the same
shared-reference timing discipline to the PIP workload that Goal2175/2179 added
for overlay and LSI.

The runner now has:

- `_run_pip_direct_backend(...)`
- shared PIP CPU Python reference rows reused by CPU/native-oracle, Embree, and
  OptiX
- existing generic RTDL kernel: `rayjoin_point_location_positive_hits_reference`

No native ABI or engine behavior changed.

## Pod Evidence

Pod access:

- `root@157.157.221.29`
- SSH port: `24240`
- Accepted local key: `id_ed25519_rtdl_codex`

Runtime facts inherited from the active RayJoin pod lane:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 580.65.06
- CUDA: 12.8
- OptiX SDK: v8.1.0
- RTDL runner commit: `173a12bca288a9bbddff4386fb1417c4d388be75`

Collected artifact:

- `docs/reports/goal2181_pip512_shared_reference_pod_2026-05-16.json`

The run used one warmup and five measured repeats on:

- case: `pip_county512`
- points: 512
- polygons: 481
- candidate point/polygon pairs: 246,272
- emitted positive-hit rows: 1,430
- shared CPU Python reference rows: 1,430, built once in `0.111331` sec

## Result

| Backend | Median sec | Rows | Parity vs CPU Python reference |
| --- | ---: | ---: | --- |
| CPU/native-oracle | 0.016410 | 1,430 | pass |
| Embree | 0.004546 | 1,430 | pass |
| OptiX | 0.004800 | 1,430 | pass |

Derived ratios:

| Ratio | Value |
| --- | ---: |
| CPU/native-oracle vs Embree | 3.610x |
| CPU/native-oracle vs OptiX | 3.419x |
| Embree vs OptiX | 0.947x |

## Interpretation

This is not an OptiX win. It is a correctness and boundary result:

- PIP is parity-clean across CPU/native-oracle, Embree, and OptiX.
- Both Embree and OptiX beat CPU/native-oracle on this row.
- Embree is slightly faster than OptiX at this size, by about `1.056x`.

The likely reason is workload shape. The row has only 246k candidate
point/polygon pairs and 1,430 emitted hits. That is enough for both RTDL
backends to be useful, but not enough to make OptiX's fixed launch and first-use
costs translate into a same-contract win over Embree in hot median timing.

Together with Goal2177 and Goal2179, this gives a cleaner RayJoin lesson:

- sparse large LSI: strong OptiX win
- large overlay dependency rows: widening OptiX win with scale
- bounded PIP row: parity-clean, but Embree slightly faster at this size

## Claim Boundary

This goal authorizes:

- a narrow statement that `pip_county512` is parity-clean across
  CPU/native-oracle, Embree, and OptiX
- a narrow statement that Embree beats CPU/native-oracle by `3.610x`
- a narrow statement that OptiX beats CPU/native-oracle by `3.419x`
- a narrow statement that OptiX does not beat Embree on this row

This goal does not authorize:

- full RayJoin paper reproduction
- broad RT-core speedup claims
- v2.0 release authorization
- whole-app RayJoin speedup claims
- claims that OptiX wins every RayJoin subproblem

## Verdict

Goal2181 is accepted as a PIP boundary result. It is valuable precisely because
it prevents overclaiming: RTDL's OptiX path can dominate sparse LSI and larger
overlay rows, but this PIP row remains an Embree-favored same-contract case at
the measured scale.
