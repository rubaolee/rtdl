# Current V4 Status

V4 is the current RTDL user surface for generic RT-core operator work.

Status: formal V4.0.0 bounded operator release authorized.

## User Promise

V4 gives users a clean Python front door for measured, reusable RT-shaped
operators. The engine may contain fused generic continuation operators such as
count/threshold, grouped reduction, weighted sum, component union, nearest
witness, and AABB query count. It must not contain app-identity kernels such as
"DBSCAN kernel" or "Barnes-Hut kernel" as public V4 features.

## Current Scorecard State

The frozen Goal4639 scorecard passed on the RTX A5000 POD:

| Metric | Result |
| --- | --- |
| Measured V4 operator surfaces | `8/8` passed |
| Strong benchmark families | `4/4` passed |
| Partial control families | `4/4` passed |
| Candidate surfaces | `0` |
| Failed scorecard surfaces | `0` |
| Public performance wording | distribution + denominator required |

The public performance wording is intentionally distribution-based:

- most measured operators are 1.2x-1.7x faster than their stated
  brute-force partner/CPU baselines;
- ray/triangle any-hit flags is `5.671x` against its Torch reference baseline;
- point-group nearest witness and AABB all-ops are large scale-dependent
  algorithmic-complexity wins where the alternative is brute force or a slower
  same-contract index control.

Do not headline the raw scorecard geomean. These are operator-level scorecard
rows with denominators, not whole-application speedup claims and not
near-hand-written-OptiX claims.

## Measured Surface Summary

| Surface | Partner scope | Representative result | Baseline / denominator | Scale |
| --- | --- | ---: | --- | --- |
| Fixed-radius count-threshold | Torch CUDA | `1.697x` | Torch brute-force/reference | script default fixture; repeat `7`, warmup `1` |
| Closest-hit grouped argmin | Torch CUDA | `1.257x` | Torch brute-force/reference | script default grouped-argmin fixtures; repeat `7`, warmup `1` |
| Ray/triangle any-hit flags | Torch CUDA | `5.671x` | Torch brute-force/reference | `max_torch_reference_count=8192`; repeat `5`, warmup `1` |
| Primitive grouped-i64 reduction | Torch CUDA | `1.384x` | Torch brute-force/reference | ray counts `32768,131072`; group widths `1,16,256`; repeat `7`, warmup `2` |
| Point-group nearest witness | Torch CUDA | `389.707x` | brute-force nearest-witness reference | query counts `32768,131072`; fixtures `mixed4,mixed6`; repeat `7`, warmup `2`; scale-dependent O(n²)-vs-BVH win |
| Ray/triangle any-hit weighted sum | Torch CUDA | `1.482x` | Torch brute-force/reference comparable route | Goal4633 shapes `32768,131072,262144,524288` |
| Fixed-radius graph component union | Numba | `1.203x` | legacy prepared-runner wall route; Embree controls recorded | clustered3d `262144` points; repeat `5`, warmup `1` |
| AABB all-ops count | RTDL native | `164.716x` | Embree same-contract prepared AABB query control | `1000000` boxes, `1000` queries, all ops, `240` repeats; scale-dependent indexed-control win |

Use [../future/v4/tier2_operator_catalog.md](../future/v4/tier2_operator_catalog.md)
for the exact API surface, partner scope, and caveats for each row.

## Start Command

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python scripts/v4_catalog_regression_gate.py --mode dry-run
```

## Boundary

Allowed wording:

- RTDL V4.0.0 is a bounded operator release for 8 documented generic RT-core
  operators that beat their stated brute-force partner/CPU baselines.
- V4 has eight measured generic Tier-2 operator surfaces.
- The frozen Goal4639 scorecard passed for those documented surfaces.

Not authorized:

- broad V4 speedup wording;
- whole-application speedup wording;
- all-benchmark speedup wording;
- public true-zero-copy wording;
- Tier-3 callback/PTX support wording;
- raw OptiX callback support wording;
- CuPy performance wording;
- embedding, C ABI, or non-Python host binding wording.
