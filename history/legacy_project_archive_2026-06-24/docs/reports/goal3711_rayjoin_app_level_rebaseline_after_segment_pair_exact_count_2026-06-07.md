# Goal3711 RayJoin App-Level Rebaseline After Segment-Pair Exact Count

Date: 2026-06-07

Status: internal same-contract benchmark evidence. This is not a release packet, not a RayJoin paper reproduction, not an RTDL-beats-RayJoin claim, not a public speedup claim packet, not a broad RT-core speedup claim, and not a true zero-copy claim.

## Purpose

Goal3709 set the immediate next direction: give a user/reviewer a clear RayJoin app-level answer while continuing deeper generic scalar-count work.

This report refreshes the current app-level mixed-route benchmark after Goals 3700-3708:

- PIP scalar count stays on the current same-contract CuPy dense count route.
- LSI count uses the repaired RTDL/OptiX prepared-left exact segment-pair count route.
- Overlay active-count uses the RTDL/OptiX active-count route.

The result answers a narrower question than the RayJoin paper comparison:

> On the public 4096-chain CDB slice, how does the current recommended RTDL/partner mixed route compare with an all-CuPy dense same-contract baseline for the three promoted RayJoin subcontracts?

## Evidence

Pod:

- NVIDIA RTX A5000, driver `580.126.09`
- source commit `4129ca8f912c3ad197c3c70a27c8bea0b4327456`
- runner `scripts/goal3612_rayjoin_safe_mixed_route_composite.py`
- artifact `docs/reports/goal3711_rayjoin_app_level_rebaseline_a5000/summary.json`

Command:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS=1e-9 \
python3 scripts/goal3612_rayjoin_safe_mixed_route_composite.py \
  --counts 4096 \
  --repeat 20 \
  --warmup 5 \
  --output docs/reports/goal3711_rayjoin_app_level_rebaseline_a5000/summary.json
```

Dataset:

- public CDB slice from `br_county.cdb` and `br_soil.cdb`
- start chain `256`
- chain count `4096`
- repeat `20`, warmup `5`

## App-Level Result

| Chains | All-CuPy Sum Median Sec | Recommended Mixed Sum Median Sec | Mixed Speedup Vs All-CuPy | Counts Match |
| ---: | ---: | ---: | ---: | --- |
| `4096` | `1.430871006` | `0.005847813` | `244.685x` | `true` |

This is an app-level composite over the three promoted RayJoin subcontracts in the runner. It is an unweighted sum of each subcontract's hot median seconds. It is not a whole RayJoin-paper reproduction score.

## Subcontract Rows

| Subcontract | All-CuPy Median Sec | Recommended Route | Recommended Median Sec | Speedup Vs CuPy | Count |
| --- | ---: | --- | ---: | ---: | ---: |
| PIP scalar count | `0.000890258` | CuPy dense CUDA-core count | `0.000890258` | `1.000x` | `11316` |
| LSI count | `1.266241380` | RTDL/OptiX prepared-left exact count | `0.000157934` | `8017.551x` | `4977` |
| Overlay active-count | `0.163739367` | RTDL/OptiX active-count | `0.004799621` | `34.115x` | `4250` |

The LSI route is the main change from the older Goal3612 artifact. The current artifact records native phase timing:

| LSI Native Phase | Seconds / Value |
| --- | ---: |
| `mode` | `count_prepared_left` |
| `candidate_count_pass` | `0.000116165` |
| `candidate_write_pass` | `0.0` |
| `candidate_download` | `0.0` |
| `exact_refine` | `0.0` |
| `left_upload` | `0.0` |
| `raw_candidate_count` | `5012` |
| `emitted_count` | `4977` |

## Interpretation

The 4096-chain public CDB composite is now strong against the all-CuPy dense same-contract baseline:

- PIP remains on CuPy because the current RT relation-status route is not robust/fast enough for this scalar count.
- LSI now benefits heavily from the generic RTDL/OptiX prepared-left exact segment-pair count route.
- Overlay active-count remains a real RTDL/OptiX win against dense CuPy.

This is a useful language/runtime signal:

- The app author does not write OptiX shader code.
- RTDL provides the generic OptiX primitive route.
- Partner logic remains outside the native engine.
- The route is mixed because users are allowed to choose partners and because correctness decides promotion.

## Remaining Work

This result does not close the RayJoin performance campaign.

Required next:

1. Compare this app-level mixed route against the original RayJoin implementation on the same dataset/contract where possible, separately from the all-CuPy baseline.
2. Continue Goal3709's dense-boundary exact scalar-count work so PIP-style scalar counts can move from dense CuPy fallback toward a generic RTDL/partner route.
3. Expand the app-level matrix beyond the 4096-chain slice and include seconds-scale repeat windows.
4. Keep weak rows visible. In this artifact, PIP is exactly parity with CuPy because the recommended route is still CuPy.

## Boundary

This report does not authorize:

- release,
- public speedup wording,
- RTDL-beats-RayJoin wording,
- RayJoin paper reproduction wording,
- broad RT-core speedup wording,
- true zero-copy wording,
- native default-route promotion.

It is current internal evidence that the recommended mixed RTDL/partner route is `244.685x` faster than an all-CuPy dense same-contract baseline on the 4096-chain public CDB composite measured here.
