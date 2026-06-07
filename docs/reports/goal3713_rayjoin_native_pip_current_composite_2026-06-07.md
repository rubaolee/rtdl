# Goal3713 RayJoin Native-PIP Current Composite

Date: 2026-06-07

Status: internal same-contract performance evidence. This is not a release packet, not a public speedup claim, not an RTDL-beats-RayJoin claim, not a RayJoin paper reproduction claim, not a broad RT-core speedup claim, not a true zero-copy claim, and not a native default-route authorization.

## Purpose

Goal3711 refreshed the current RayJoin app-level mixed route after the segment-pair exact-count work. That packet still used CuPy for the PIP scalar-count leg.

Goal3713 refreshes the stronger candidate route from Goal3688 on current `main`:

- PIP scalar count uses the generic native RTDL/OptiX relation-status corrected scalar-count executor.
- LSI count uses the current repaired RTDL/OptiX prepared-left exact segment-pair count.
- Overlay active-count uses the RTDL/OptiX active-count route.

The goal is to answer:

> Can the generic native dense-boundary scalar-count primitive replace the CuPy PIP leg in the current RayJoin composite while preserving exact counts?

## Evidence

Pod:

- NVIDIA RTX A5000, driver `580.126.09`
- source commit `7cf5e2f37e4576a1d3a51d670fcde05cb79d310d`
- runner `scripts/goal3688_rayjoin_native_pip_safe_mixed_composite.py`
- artifact `docs/reports/goal3713_rayjoin_native_pip_current_composite_a5000/summary.json`

Command:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so \
RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS=1e-9 \
python3 scripts/goal3688_rayjoin_native_pip_safe_mixed_composite.py \
  --counts 4096 \
  --repeat 20 \
  --warmup 5 \
  --output docs/reports/goal3713_rayjoin_native_pip_current_composite_a5000/summary.json
```

Dataset:

- public CDB slice from `br_county.cdb` and `br_soil.cdb`
- start chain `256`
- chain count `4096`
- repeat `20`, warmup `5`

## Result

| Chains | All-CuPy Sum Median Sec | Native-PIP Mixed Sum Median Sec | Mixed Speedup Vs All-CuPy | Counts Match |
| ---: | ---: | ---: | ---: | --- |
| `4096` | `1.430714336` | `0.005322640` | `268.798x` | `true` |

Per-contract:

| Subcontract | All-CuPy Median Sec | Candidate Route | Candidate Median Sec | Speedup Vs CuPy | Count |
| --- | ---: | --- | ---: | ---: | ---: |
| PIP scalar count | `0.000890137` | RTDL/OptiX native relation-status corrected scalar count | `0.000343661` | `2.590x` | `11316` |
| LSI count | `1.266601922` | RTDL/OptiX prepared-left exact count | `0.000167544` | `7559.817x` | `4977` |
| Overlay active-count | `0.163222278` | RTDL/OptiX active-count | `0.004811435` | `33.924x` | `4250` |

## Comparison To Goal3711

Goal3711 used the same app-level structure but left PIP on CuPy. Goal3713 replaces that PIP leg with the generic native scalar-count executor.

| Packet | PIP Route | Composite Seconds | Speedup Vs All-CuPy |
| --- | --- | ---: | ---: |
| Goal3711 | CuPy dense scalar count | `0.005847813` | `244.685x` |
| Goal3713 | RTDL/OptiX native scalar count | `0.005322640` | `268.798x` |

This is a `1.099x` improvement in the mixed composite (`0.005847813 / 0.005322640`) and a `2.590x` improvement on the PIP leg alone.

## Interpretation

This is the concrete payoff from the dense-boundary scalar-count work:

- The native PIP leg avoids materializing dense boundary rows.
- The app author still does not write OptiX shader code.
- The native engine remains generic: closed-shape membership scalar count, relation-status correction, prepared points, and prepared shapes.
- The mixed route becomes more RTDL-native without losing the user-choice partner model.

The result supports using the native scalar-count executor as the internal recommended PIP leg for this measured same-contract packet, pending external review. It does not by itself authorize public RayJoin claims.

## Remaining Work

1. External review of Goal3713.
2. Compare the current mixed route against the original RayJoin implementation on the same dataset/contract where possible.
3. Expand to more chain counts and seconds-scale composite windows.
4. Continue investigating overlay and other weak rows without hiding the remaining gaps.

## Boundary

This report does not authorize:

- release,
- public speedup wording,
- RTDL-beats-RayJoin wording,
- RayJoin paper reproduction wording,
- broad RT-core speedup wording,
- true zero-copy wording,
- native default-route promotion.

It records internal evidence that the current native-PIP mixed route is exact and faster than the all-CuPy dense same-contract baseline on this 4096-chain public CDB packet.
