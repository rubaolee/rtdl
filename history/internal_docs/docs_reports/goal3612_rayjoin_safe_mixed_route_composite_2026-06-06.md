# Goal3612 - RayJoin Safe Mixed-Route Composite At 4096 Chains

Date: 2026-06-06

Status: internal v2.9 same-contract performance evidence. This does not authorize release, public speedup wording, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true zero-copy, or native default-route claims.

## Purpose

Goal3609 showed that the mixed RayJoin route can be much faster than an all-CuPy dense baseline, but the first mixed runner used the pure device left-id dense count for LSI. Goal3610 then showed why that is not safe at 4096 chains: the dense left-id count route produced `4985` LSI hits while the CuPy same-contract baseline produced `4977`.

Goal3612 keeps the mixed-route principle but repairs the LSI contract:

- PIP scalar count stays on CuPy dense CUDA-core count.
- LSI count uses exact prepared RTDL/OptiX count with host double refinement after RT candidate traversal.
- Overlay active-count stays on RTDL/OptiX prepared shape-pair active count.

## Evidence

Pod:

- NVIDIA RTX A5000, driver 580.126.09
- SSH evidence host supplied by user: `root@69.30.85.203 -p 22057`

Source:

- commit `83eb51dbd11a8dc2e05e26310fd8511ea76c2e2a`
- runner `scripts/goal3612_rayjoin_safe_mixed_route_composite.py`
- artifact `docs/reports/goal3612_rayjoin_safe_mixed_route_composite_a5000/summary.json`

Dataset:

- public CDB slices from `br_county.cdb` and `br_soil.cdb`
- start chain `256`
- chain count `4096`
- repeat `20`, warmup `5`

## Result

The 4096-chain safe mixed composite is exact and strongly faster than the all-CuPy dense same-contract baseline.

| Chains | All-CuPy Sum Median Sec | Safe Mixed Sum Median Sec | Speedup | Counts Match |
| ---: | ---: | ---: | ---: | --- |
| 4096 | 1.433168449 | 0.007389807 | 193.939x | true |

Per-contract:

| Contract | All-CuPy Median Sec | Safe Mixed Route | Safe Mixed Median Sec | Route Speedup | Count |
| --- | ---: | --- | ---: | ---: | ---: |
| PIP scalar count | 0.000886511 | CuPy dense CUDA-core | 0.000886511 | 1.000x | 11316 |
| LSI count | 1.269116998 | RTDL/OptiX exact prepared count | 0.001664417 | 762.499x | 4977 |
| Overlay active-count | 0.163164941 | RTDL/OptiX active-count | 0.004838879 | 33.720x | 4250 |

## What Changed From Goal3609

The winning route is still mixed, but the LSI leg is no longer the unsafe pure device left-id dense count route.

That distinction matters:

- `prepared_optix_left_id_dense_count` is very fast but currently counts eight extra near-degenerate LSI candidates at 4096.
- `prepared_optix_exact_segment_pair_count` is still RT-accelerated for candidate traversal, then applies the refined host double segment-pair contract, and matches the all-CuPy baseline exactly.

This is the better v2.9 RayJoin reference route because it is both fast and same-contract correct.

## Design Meaning

This result is a good example of RTDL's current practical shape:

- the user can choose partners;
- RTDL can recommend a route per generic contract;
- the engine stays app-agnostic;
- exactness gates route promotion, even when a faster device-resident route exists.

The next engineering direction is still generic, not RayJoin-specific: promote a robust segment-pair count policy that can keep the LSI reduction fully device-resident while applying the same near-degenerate denominator, endpoint, collinearity, and tolerance policy as the exact route.

## Boundary

This is internal public-CDB benchmark-app evidence. It is not a RayJoin paper reproduction, not a release packet, and not a public speedup claim packet.
