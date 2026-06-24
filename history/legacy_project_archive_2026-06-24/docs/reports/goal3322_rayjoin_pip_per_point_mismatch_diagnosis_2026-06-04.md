# Goal3322 - RayJoin PIP Per-Point Mismatch Diagnosis

Date: 2026-06-04

## Purpose

Goal3320 found that the current fast prepared point / closed-shape scalar-count route is exact for the soil start256 slice but overcounts the county start256 slice. Goal3321 added a preflight gate. Goal3322 diagnoses the mismatch shape so the next primitive design can target the real gap.

## Pod Evidence

- GPU: NVIDIA RTX A5000, driver 580.126.09
- Commit: `568d95227cf6c83638ecdc4a86d2500d1d75d29f`
- Query axis: `z_point`
- Boundary mode: `inclusive`
- Artifact: `docs/reports/goal3322_rayjoin_pip_per_point_mismatch_diagnosis_2026-06-04.json`

## Result

| Dataset | Exact total | Fast total | Delta | Mismatch points | Positive deltas | Negative deltas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `br_county_start256_count512.cdb` | 1417 | 1429 | +12 | 7 | 7 | 0 |
| `br_soil_start256_count512.cdb` | 1471 | 1471 | 0 | 0 | 0 | 0 |

County mismatch sample:

| Point id | x | y | Exact | Fast | Delta |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 522 | -53.001066428 | -2.6712524436 | 2 | 3 | +1 |
| 523 | -53.001066428 | -2.6712524436 | 2 | 3 | +1 |
| 538 | -48.999986134 | -4.832694058 | 2 | 4 | +2 |
| 539 | -48.999986134 | -4.832694058 | 2 | 4 | +2 |
| 540 | -49.000030006 | -4.8326123986 | 2 | 4 | +2 |
| 564 | -47.638011567 | -1.3744132563 | 2 | 4 | +2 |
| 565 | -47.638011567 | -1.3744132563 | 2 | 4 | +2 |

## Interpretation

The failure is structured:

- all mismatches are overcounts;
- no point undercounts;
- several mismatching rows have duplicate coordinates with adjacent caller IDs;
- exact counts remain small per point, while the fast route adds one or two extra memberships.

This points away from random launch instability and toward a semantic contract gap around CDB topology, boundary degeneracy, duplicate ownership, ring/chain identity, or face assignment policy.

The next major primitive should therefore not be another RayJoin-specific native function. It should be a generic face/topology-aware closed-shape membership/count contract with explicit deterministic boundary ownership and duplicate policy. The current fast route should remain guarded by Goal3321 preflight until that richer primitive is designed and validated.

## Claim Boundary

- `release_authorized`: false
- `public_speedup_claim_authorized`: false
- `rt_core_speedup_claim_authorized`: false
- `true_zero_copy_claim_authorized`: false
- `rtdl_beats_rayjoin_claim_authorized`: false
- `rayjoin_paper_reproduction_claim_authorized`: false

