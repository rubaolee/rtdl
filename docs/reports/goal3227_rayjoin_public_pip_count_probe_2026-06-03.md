# Goal3227: RayJoin Public PIP Count Probe

Date: 2026-06-03

## Purpose

Goal3227 adds the public CDB PIP sibling to the Goal3218 public LSI probe and
Goal3225 public overlay active-count probe.

It reuses Goal2159 public CDB slice materialization and checks that the prepared
OptiX point/closed-shape count route matches the CPU reference
`positive_assignment_count` contract on the bounded `pip_county512` case.

## Artifact

- `docs/reports/goal3227_rayjoin_public_pip_count_probe_2026-06-03.json`
- `docs/reports/goal3227_rayjoin_public_pip_count_probe_2026-06-03.stdout`

Pod metadata:

- Commit: `67dcad5b4beb5c0d462a13ab75bb681c4aaee611`
- GPU: `NVIDIA A40, 570.211.01`
- CUDA driver query: present
- nvcc version: present
- OptiX library: `/root/rtdl_goal3151/build/librtdl_optix.so`
- Warmups: `1`
- Repeats: `5`
- Status: `pass`

| Case | Public Slice | Expected Positive Assignments | Observed Counts | Median Prepared Count (s) |
| --- | --- | ---: | --- | ---: |
| `pip_county512` | county 0:512 | 1430 | `[1430, 1430, 1430, 1430, 1430]` | 0.0749423447996378 |

## Interpretation

Goal3227 confirms the current prepared OptiX PIP count route on a bounded public
Brazil county CDB slice. Together with Goal3218 and Goal3225, this gives public
count/parity coverage for all three current RayJoin count-family workloads:

- PIP: public positive-assignment count,
- LSI: public segment-intersection count via fused dense left-id count,
- overlay_seed: public active pair-dependency count.

The native engine remains app-agnostic. It sees the generic
`POINT_CLOSED_SHAPE_MEMBERSHIP_2D` prepared count contract; RayJoin
interpretation remains in Python.

## Boundary

This report does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

The full RayJoin paper-scale comparison remains open.
