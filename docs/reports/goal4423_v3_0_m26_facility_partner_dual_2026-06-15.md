# Goal4423: V3.0 M26 Facility KNN Partner Dual-Path Closure

## Status

M26 closes the facility KNN exact-assignment partner gap at the app front door:
`examples/current/apps/geospatial/rtdl_facility_knn_assignment.py` now accepts
`--backend partner_exact --partner numba` in addition to the existing CuPy and
Torch routes.

This is intentionally not an RT-core claim. The route exercises the generic
`top_k_nearest_points_2d_partner_columns` primitive as a partner exact-reference
path for ranked nearest-depot assignment. Its purpose is to make the current
application surface follow the V3.0 partner rule: when an app needs partner
logic, expose and test both the likely best Python GPU partner, here CuPy, and
the no-C++/no-CUDA-source Numba reference.

## What Changed

- Added Numba host extraction in the facility app's partner column reader.
- Added `numba` to the public `--partner` choices for `partner_exact`.
- Sorted materialized rows by `(query_id, neighbor_rank)` so CuPy, Torch, and
  Numba share a deterministic app-level row contract.
- Added `scripts/v3_0_m26_facility_partner_dual_measure.py` to time the real
  app front door for CuPy and Numba at the same scale and compare compact
  output signatures.

## Contract Boundary

| Question | M26 answer |
| --- | --- |
| Does this use app-specific native engine customization? | No. |
| Does this use RT cores? | No. |
| Does this authorize RT-core speedup wording? | No. |
| Does this expose both best practical Python partner and Numba reference? | Yes: CuPy and Numba. |
| Does this preserve the generic RTDL primitive/partner architecture? | Yes. The app calls a generic top-k nearest point-column primitive and performs app interpretation outside the engine. |

## Pod Evidence

The M26 runner wrote compact evidence to:

- `docs/reports/goal4423_v3_0_m26_facility_partner_dual_copies2048_2026-06-15.json`
- `docs/reports/goal4423_v3_0_m26_facility_partner_dual_copies3072_2026-06-15.json`

Hardware:

- NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20,475 MiB.

Measured rows:

| copies | customers | depots | logical pairs | CuPy median full app wall s | Numba median full app wall s | best observed | signature match |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 2,048 | 8,192 | 8,192 | 67,108,864 | 0.282747 | 0.306065 | CuPy | true |
| 3,072 | 12,288 | 12,288 | 150,994,944 | 0.624098 | 0.506511 | Numba | true |

Evidence fields:

- `comparison.signature_match: true`;
- `claim_boundary.best_partner_and_numba_reference_exposed: true`;
- CuPy row with `partner_reference_contract: generic_exact_top_k_nearest_points_2d`;
- Numba row with `metadata_numba_status: device_grouped_topk_after_device_score_rows`;
- all public speedup and RT-core claim flags false.

## Interpretation

Facility ranked assignment remains a dense exact top-k reference path here. It
is useful for correctness, app reachability, and partner-policy closure; it is
not proof that RTDL has a native RT-core nearest-depot ranking primitive. The
RT-core-ready subpath for this app remains the prepared fixed-radius service
coverage decision, while ranked KNN assignment is deliberately reported as a
generic partner exact-reference route.

The best partner is scale-dependent. CuPy is slightly faster at 67M logical
pairs, but Numba's grouped device top-k path is faster at 151M logical pairs.
That supports the current V3 policy: expose the best practical Python partner
and the Numba no-C++ reference, then report the measured result rather than
assuming one partner always wins.

## Verification

Planned verification for this milestone:

```bash
PYTHONPATH=src:. python -m unittest tests.goal4423_v3_0_m26_facility_partner_dual_test
PYTHONPATH=src:. python scripts/v3_0_m26_facility_partner_dual_measure.py \
  --copies 2048 \
  --warmups 1 \
  --repeats 3 \
  --partners cupy,numba \
  --numba-cuda-home /tmp/rtdl_cuda124_home \
  --output docs/reports/goal4423_v3_0_m26_facility_partner_dual_copies2048_2026-06-15.json
PYTHONPATH=src:. python scripts/v3_0_m26_facility_partner_dual_measure.py \
  --copies 3072 \
  --warmups 1 \
  --repeats 3 \
  --partners cupy,numba \
  --numba-cuda-home /tmp/rtdl_cuda124_home \
  --output docs/reports/goal4423_v3_0_m26_facility_partner_dual_copies3072_2026-06-15.json
```
