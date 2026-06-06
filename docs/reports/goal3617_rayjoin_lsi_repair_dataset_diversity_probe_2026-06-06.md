# Goal3617 - RayJoin LSI Repair Dataset-Diversity Probe

Date: 2026-06-06

Status: internal v2.9 diversity probe. This does not authorize release, public speedup wording, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true zero-copy, or native default-route claims.

## Purpose

Gemini's Goal3614 review accepted the Goal3612/Goal3613 repair with boundary and flagged dataset diversity as a remaining risk.

Goal3617 runs the repaired fast mixed route on a different public-CDB 4096-chain slice:

- Goal3613 evidence slice: `start=256`, `count=4096`
- Goal3617 diversity slice: `start=0`, `count=4096`

## Evidence

Pod:

- NVIDIA RTX A5000, driver 580.126.09
- SSH evidence host supplied by user: `root@69.30.85.203 -p 22057`

Source:

- commit `5dd0c6ea4b3569bd74207214951caf07710867aa`
- runner `scripts/goal3609_rayjoin_recommended_mixed_route_composite.py`
- artifact `docs/reports/goal3617_rayjoin_lsi_repair_dataset_diversity_a5000/start0_4096_fast_mixed.json`

Dataset:

- public CDB slices from `br_county.cdb` and `br_soil.cdb`
- start chain `0`
- chain count `4096`
- repeat `20`, warmup `5`

## Result

The repaired fast mixed route remains exact on the second 4096-chain slice.

| Chains | Start | All-CuPy Sum Median Sec | Repaired Mixed Sum Median Sec | Speedup | Counts Match |
| ---: | ---: | ---: | ---: | ---: | --- |
| 4096 | 0 | 1.536079022 | 0.009386375 | 163.650x | true |

Per-contract:

| Contract | All-CuPy Count | Repaired Count | All-CuPy Median Sec | Repaired Median Sec | Route Speedup |
| --- | ---: | ---: | ---: | ---: | ---: |
| PIP scalar count | 11331 | 11331 | 0.000980610 | 0.000980610 | 1.000x |
| LSI count | 5612 | 5612 | 1.338963458 | 0.000844310 | 1585.867x |
| Overlay active-count | 4678 | 4678 | 0.196134953 | 0.007561454 | 25.939x |

The key correctness signal is `all_counts_match=true`, including LSI `5612/5612`.

## Interpretation

Goal3617 does not close dataset diversity completely, but it improves the evidence:

- the strict predicate repair is not only valid on the original `start=256` slice that exposed the bug;
- it also validates on a separate `start=0` public-CDB slice with different counts;
- the repaired LSI route remains the performance driver.

The remaining boundary from Goal3614 still stands: public claims need a documented generic segment-pair primitive tolerance policy and broader dataset/adversarial coverage.

## Boundary

This is an internal diversity probe only. It is not a release packet and not a public claim packet.
