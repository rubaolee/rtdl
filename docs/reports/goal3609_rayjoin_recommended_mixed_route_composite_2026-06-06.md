# Goal3609 - RayJoin Recommended Mixed-Route Composite Timing

Date: 2026-06-06

Status: internal v2.9 performance evidence. This does not authorize release, public speedup wording, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true zero-copy, or native default-route claims.

## Purpose

Goal3608 decided that the current RayJoin benchmark should not force every contract through RTDL/OptiX. The honest v2.9 route is mixed:

- PIP scalar count: CuPy dense CUDA-core count.
- LSI count: RTDL/OptiX prepared left-id dense count.
- Overlay active-count: RTDL/OptiX prepared shape-pair active count.

Goal3609 measures that mixed route against an all-CuPy dense same-contract baseline using an unweighted sum of hot median seconds for PIP, LSI, and overlay_seed.

## Evidence

Pod:

- NVIDIA RTX A5000, driver 580.126.09
- SSH evidence host supplied by user: `root@69.30.85.203 -p 22057`

Source:

- commit `2838ff71bc8b0717670ae5e7172dedd9079fc393`
- runner `scripts/goal3609_rayjoin_recommended_mixed_route_composite.py`
- artifact `docs/reports/goal3609_rayjoin_recommended_mixed_route_composite_a5000/summary.json`

Dataset:

- public CDB slices from `br_county.cdb` and `br_soil.cdb`
- start chain `256`
- measured successful chain count `512`
- repeat `20`, warmup `5`

## Result

The 512-chain composite is exact and strongly favors the recommended mixed route.

| Chains | All-CuPy Sum Median Sec | Recommended Mixed Sum Median Sec | Speedup | Counts Match |
| ---: | ---: | ---: | ---: | --- |
| 512 | 0.071518790 | 0.003302796 | 21.654x | true |

Per-contract:

| Contract | All-CuPy Median Sec | Recommended Route | Recommended Median Sec | Route Speedup |
| --- | ---: | --- | ---: | ---: |
| PIP scalar count | 0.000447244 | CuPy dense CUDA-core | 0.000447244 | 1.000x |
| LSI count | 0.021151579 | RTDL/OptiX prepared left-id dense count | 0.000182197 | 116.092x |
| Overlay active-count | 0.049919968 | RTDL/OptiX prepared shape-pair active count | 0.002673354 | 18.673x |

## Interpretation

This is the first useful single-number RayJoin composite for the current route decision. It confirms the design principle:

- use the partner when it is the best same-contract implementation;
- use RTDL/OptiX when the generic RT route is the best same-contract implementation;
- do not force a slower RT path only to make the app look uniformly RT-only.

The high composite speedup comes from LSI and overlay. PIP contributes parity because Goal3604 and Goal3606 showed that the current RT boundary-signal PIP route is not a valid default.

## Large-Scale Boundary

The same runner was also attempted at `4096` chains. It failed closed before writing a composite artifact because the LSI same-contract count did not match:

```text
count=4096 workload=lsi: CuPy=4977, recommended RTDL/OptiX=4985
```

Goal3610 follows this up with a targeted diagnostic. The short version is that the difference is exactly eight extra RTDL/OptiX left-id counts on near-degenerate segment cases. Therefore:

- the 512-chain composite is accepted as internal evidence;
- the 4096-chain composite is blocked;
- no large-scale RayJoin composite claim is authorized until the LSI near-degenerate segment policy is made identical across the CuPy baseline and the RTDL/OptiX route.

## Boundary

This is an internal v2.9 timing packet. It is not a release packet and not a public claim packet.
