# Goal3613 - Exact Predicate For LSI Left-Id Dense Count

Date: 2026-06-06

Status: internal v2.9 native-route repair and timing evidence. This does not authorize release, public speedup wording, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true zero-copy, or native default-route claims.

## Purpose

Goal3610 found that the fast RTDL/OptiX `prepared_optix_left_id_dense_count` route counted eight extra LSI candidates on the 4096-chain public-CDB slice:

```text
CuPy dense baseline: 4977
RTDL/OptiX left-id dense count before Goal3613: 4985
```

The cause was that the specialized left-id dense count pipeline counted conservative OptiX candidate events. Goal3613 changes that specialized count pipeline to use the strict segment predicate in the OptiX any-hit program before incrementing the device-resident per-left counts.

The ordinary candidate-row route remains conservative and host-refined. This change is scoped to the count-only dense left-id reduction path.

## Native Change

File:

- `src/native/optix/rtdl_optix_workloads.cpp`

In `ensure_segment_pair_left_id_count_device_columns_pipeline()`, the generated specialized count kernel now rewrites the any-hit predicate from:

```text
seg_intersect_conservative_candidate(..., &ix, &iy)
```

to:

```text
float hit_t = 0.0f;
seg_intersect(..., &hit_t, &ix, &iy)
```

This keeps the route generic: it is still a segment-pair intersection count grouped by caller-owned left ids. No RayJoin or CDB logic enters the engine.

## Evidence

Pod:

- NVIDIA RTX A5000, driver 580.126.09
- SSH evidence host supplied by user: `root@69.30.85.203 -p 22057`

Source:

- commit `223981f7bd51862b183489976ca1cc661e3fd5a0`
- rebuilt `build/librtdl_optix.so` from `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- mismatch artifact `docs/reports/goal3613_lsi_left_id_dense_count_exact_predicate_a5000/mismatch_after_patch.json`
- composite artifact `docs/reports/goal3613_lsi_left_id_dense_count_exact_predicate_a5000/fast_mixed_after_patch.json`

Dataset:

- `br_county_start256_count4096.cdb + br_soil_start256_count4096.cdb`
- left segments: `68840`
- right segments: `114534`
- dense candidate pairs: `7884520560`

## Correctness Result

The fast left-id dense-count route now matches the CuPy same-contract baseline at 4096.

| Measure | Before Goal3613 | After Goal3613 |
| --- | ---: | ---: |
| CuPy LSI count | 4977 | 4977 |
| RTDL/OptiX left-id dense count | 4985 | 4977 |
| Differing left ids | 8 | 0 |
| Delta sum | 8 | 0 |

## Performance Result

After the exact-predicate repair, the fast mixed route is valid at 4096:

| Chains | All-CuPy Sum Median Sec | Repaired Mixed Sum Median Sec | Speedup | Counts Match |
| ---: | ---: | ---: | ---: | --- |
| 4096 | 1.436104300 | 0.007598563 | 188.997x | true |

Per-contract:

| Contract | All-CuPy Median Sec | Repaired Route | Repaired Median Sec | Route Speedup | Count |
| --- | ---: | --- | ---: | ---: | ---: |
| PIP scalar count | 0.000886021 | CuPy dense CUDA-core | 0.000886021 | 1.000x | 11316 |
| LSI count | 1.266512598 | RTDL/OptiX exact device left-id dense count | 0.000623005 | 2032.908x | 4977 |
| Overlay active-count | 0.168705681 | RTDL/OptiX active-count | 0.006089537 | 27.704x | 4250 |

The composite total is slightly lower than Goal3612's `193.939x` because overlay timing varied between runs. The important repair is the LSI leg: it is now both exact for this slice and materially faster than the host-refined exact LSI route measured in Goal3612.

## Design Meaning

Goal3613 closes the immediate large-scale LSI blocker without adding app-specific engine logic.

The remaining generic design question is broader than RayJoin: the project should document the segment-pair count contract as an explicit primitive policy, including denominator threshold, endpoint handling, collinearity policy, and whether float-side strict predicate counting is sufficient for all accepted datasets or should be backed by a heavier exact device/host fallback on detected ambiguity.

## Boundary

This is internal v2.9 evidence. It repairs the 4096 public-CDB LSI count mismatch for the tested route and dataset. It is not a RayJoin paper reproduction, not a release packet, and not a public speedup claim packet.
