# Goal3610 - RayJoin LSI 4096 Count Mismatch Probe

Date: 2026-06-06

Status: internal v2.9 blocker diagnostic. This does not authorize release, public speedup wording, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true zero-copy, or native default-route claims.

## Purpose

Goal3609 produced a strong 512-chain RayJoin mixed-route composite result, but the same runner failed closed on the 4096-chain public-CDB slice because the LSI count differed:

```text
CuPy dense baseline: 4977
RTDL/OptiX left-id dense count: 4985
```

Goal3610 diagnoses whether that mismatch is random, broad, or concentrated.

## Evidence

Pod:

- NVIDIA RTX A5000, driver 580.126.09
- SSH evidence host supplied by user: `root@69.30.85.203 -p 22057`

Source:

- base commit `2838ff71bc8b0717670ae5e7172dedd9079fc393`
- diagnostic runner `scripts/goal3610_rayjoin_lsi_4096_mismatch_probe.py`
- artifact `docs/reports/goal3610_rayjoin_lsi_4096_count_mismatch_probe_a5000/summary.json`

Dataset:

- `br_county_start256_count4096.cdb + br_soil_start256_count4096.cdb`
- left segments: `68840`
- right segments: `114534`
- dense candidate pairs: `7884520560`

## Result

The mismatch is concentrated and one-sided.

| Measure | Value |
| --- | ---: |
| CuPy total | 4977 |
| RTDL/OptiX total | 4985 |
| Differing left ids | 8 |
| Delta sum | 8 |

Each differing left id has `RTDL/OptiX = CuPy + 1`; no left id has fewer RTDL/OptiX hits than CuPy.

Sample:

| Left Id | CuPy | RTDL/OptiX | Delta | Segment |
| ---: | ---: | ---: | ---: | --- |
| 1050 | 0 | 1 | 1 | `[-58.161307078, -2.1323730298, -58.174415053, -2.1189082909]` |
| 18705 | 1 | 2 | 1 | `[-48.231198602, -5.9457514655, -48.226647372, -5.9554207638]` |
| 34424 | 1 | 2 | 1 | `[-43.6914973, -5.9190425659, -43.696431848, -5.9267038803]` |
| 66567 | 0 | 1 | 1 | `[-35.840216373, -8.5977194262, -35.840217381, -8.5977196819]` |
| 66820 | 0 | 1 | 1 | `[-35.365436296, -7.9027199683, -35.365442732, -7.9026910353]` |
| 66823 | 0 | 1 | 1 | `[-35.36634017, -7.9020645748, -35.366341488, -7.9020642422]` |
| 68473 | 0 | 1 | 1 | `[-35.697824603, -8.5467913442, -35.697824512, -8.5467941985]` |
| 68478 | 0 | 1 | 1 | `[-35.699261561, -8.5528883763, -35.699260816, -8.5528894777]` |

## Interpretation

The current blocker is a same-contract definition problem, not a broad route failure.

The CuPy dense baseline uses the Goal3589 segment-intersection predicate, which rejects nearly parallel pairs when `fabs(denom) < 1.0e-7`. The RTDL/OptiX path appears to include eight additional near-degenerate or tiny-segment cases at this scale, so the immediate blocker is the missing shared near-degenerate segment policy.

That means a large-scale RayJoin composite cannot be published until the project makes one explicit contract decision:

- either align RTDL/OptiX to the current CuPy dense predicate;
- or align the CuPy baseline to the RTDL/OptiX predicate;
- or publish both as different contracts with different names and never compare them as one same-contract row.

The likely engineering fix is not RayJoin-specific. It should be a generic robust segment-pair intersection contract with explicit denominator, endpoint, collinearity, and tolerance policy.

## Boundary

This is a diagnostic correctness artifact, not a performance benchmark. It blocks the 4096-chain composite until same-contract LSI semantics are repaired.
