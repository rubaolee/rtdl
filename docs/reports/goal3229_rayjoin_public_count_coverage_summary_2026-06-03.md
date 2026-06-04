# Goal3229: RayJoin Public Count Coverage Summary

Date: 2026-06-03

## Purpose

Goal3229 consolidates the current public-data count/parity evidence for the
Spatial RayJoin benchmark family after Goals3218, 3225, and 3227.

This summary is reader-facing planning evidence only. It records that all three
current RayJoin count-family workloads now have bounded public CDB coverage:

- PIP: public positive-assignment count,
- LSI: public segment-intersection count via fused dense left-id count,
- overlay_seed: public active pair-dependency count.

## Evidence Table

| Workload | Goal | Public Cases | Count Contract | Observed Counts | Median Prepared/Count Time |
| --- | --- | --- | --- | --- | --- |
| `pip` | Goal3227 | `pip_county512` | `positive_assignment_count` | `1430` | 0.06793256662786007 s |
| `lsi` | Goal3218 | `lsi_county256_soil256_count48` | `intersection_count` | `34` | 0.00014243647456169128 s |
| `lsi` | Goal3218 | `lsi_county256_soil256_count128` | `intersection_count` | `56` | 0.000667918473482132 s |
| `lsi` | Goal3218 | `lsi_county256_soil256_count192` | `intersection_count` | `85` | 0.0010464414954185486 s |
| `lsi` | Goal3218 | `lsi_county256_soil256_count256` | `intersection_count` | `88` | 0.0010501518845558167 s |
| `lsi` | Goal3218 | `lsi_county256_soil256_count384` | `intersection_count` | `116` | 0.0010411553084850311 s |
| `lsi` | Goal3218 | `lsi_county256_soil256_count512` | `intersection_count` | `269` | 0.0010526198893785477 s |
| `overlay_seed` | Goal3225 | `overlay_county128_soil128` | `active_seed_count` | `1` | 0.022716183215379715 s |
| `overlay_seed` | Goal3225 | `overlay_county256_soil256` | `active_seed_count` | `9` | 0.05908652022480965 s |

## Interpretation

This closes the immediate public-data gap for count/parity coverage across the
three RayJoin workload families. It does not close full RayJoin paper
reproduction and does not claim RTDL beats RayJoin.

The coverage is intentionally contract-specific:

- PIP counts positive point-to-shape assignments.
- LSI counts segment-pair intersections using the fused dense left-id route.
- Overlay counts active seed pairs, not full row overlay continuation.

The native engine remains app-agnostic. These routes use generic point/shape,
segment-pair, segment-pair grouped-count, and shape-pair relation contracts.
RayJoin interpretation remains in Python.

The PIP and overlay rows use the refreshed `92e16b86` artifacts, which
normalize the six false claim-boundary flags at the top, row, and measurement
levels.

## Remaining Gaps

- Full paper-scale Brazil county/soil datasets are still open.
- Cross-system RTDL-vs-RayJoin execution on identical inputs is still open.
- Row overlay continuation remains deferred Tier B work.
- Broader GPU-family evidence remains open.
- Public speedup, broad RT-core speedup, true zero-copy, release, and paper
  reproduction claims remain unauthorized.

## Boundary

This summary does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.
