# Goal3606 - RayJoin PIP Boundary Signal 4096-Chain Negative Probe

Date: 2026-06-06

Status: internal v2.9 negative evidence. This does not authorize release, public speedup wording, RayJoin paper reproduction, RTDL-beats-RayJoin, RT-core speedup, true zero-copy, or native default-route claims.

## Purpose

Goal3604 showed that the boundary-event signal route was exact on 512, 1024, and 2048 public-CDB county slices, but much slower than the dense CuPy scalar-count baseline.

Before treating that route as a possible future default after optimization, Goal3606 tests the same signal on a larger 4096-chain county slice and sweeps the boundary-event tolerance.

## Evidence

Pod:

- NVIDIA RTX A5000, driver 580.126.09

Source:

- commit `df9c355a3f9a37c72a1b8aba1b19a2f3d3e80fd7`
- artifact path `docs/reports/goal3606_rayjoin_pip_boundary_signal_4096_negative_a5000/summary.json`

The probe reuses:

- `scripts/goal3388_boundary_event_tolerance_signal_slice_sweep.py`
- source CDB `data/rayjoin_public_cdb/br_county.cdb`
- start chain `256`
- chain count `4096`
- selected-point signal `candidate_count_gt_strict_zero_boundary_candidate_count_and_strict_zero_count_lte_2`

## Results

The exact prepared/CuPy count is `11316`. No tested tolerance matched it.

| `crossing_tolerance` | Filtered Count | Missing Exact Rows | Extra Rows | Selected Points | Missed True-Extra Points | False-Positive Selected Points | Match |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 11311 | 6 | 1 | 103 | 1 | 6 | false |
| 1e-6 | 11311 | 6 | 1 | 103 | 1 | 6 | false |
| 1e-5 | 11314 | 3 | 1 | 103 | 1 | 6 | false |
| 1e-4 | 11317 | 3 | 4 | 103 | 1 | 6 | false |
| 1e-3 | 11329 | 3 | 16 | 103 | 1 | 6 | false |

The repeated missing sample across tolerances includes:

```text
(4283, 4286), (4284, 4286), (4285, 4286)
```

At low tolerances, the previously known near-boundary points also disappear:

```text
(633, 632), (634, 632), (635, 632)
```

At higher tolerances, extra rows re-enter faster than the missing rows are recovered.

## Interpretation

Goal3606 changes the boundary-event signal status from "bounded constructive candidate" to "not robust enough for default routing."

The route remains useful as a design probe:

- it proves generic candidate and boundary-event columns can expose helpful signals,
- it shows why exact closed-shape membership needs topology/ownership/tolerance policy,
- it reinforces that the engine must not invent RayJoin/CDB semantics.

But it should not be promoted as a current v2.9 RayJoin PIP performance path. The right current route decision stays:

- CuPy dense CUDA-core scalar count for public-CDB PIP count;
- prepared OptiX exact count only for no-partner RTDL/OptiX PIP count;
- future fused generic exact closed-shape membership/count primitive for serious RTDL-side PIP acceleration.

## Boundary

This is negative internal evidence only. It blocks default-route promotion for the tested signal family and does not authorize public claims.
