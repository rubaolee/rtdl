# Current V4 Status

V4 is the current RTDL user surface for generic RT-core operator work.

Status: formal V4.0.0 release authorized.

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
| Representative operator geomean | `5.185x` |

The geomean is a frozen operator-scorecard result. It is not a
whole-application speedup claim.

## Measured Surface Summary

| Surface | Partner scope | Representative result |
| --- | --- | --- |
| Fixed-radius count-threshold | Torch CUDA | `1.697x` |
| Closest-hit grouped argmin | Torch CUDA | `1.257x` |
| Ray/triangle any-hit flags | Torch CUDA | `5.671x` |
| Primitive grouped-i64 reduction | Torch CUDA | `1.384x` |
| Point-group nearest witness | Torch CUDA | `389.707x` |
| Ray/triangle any-hit weighted sum | Torch CUDA | `1.482x` |
| Fixed-radius graph component union | Numba | `1.203x` |
| AABB all-ops count | RTDL native | `164.716x` |

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

- RTDL V4.0.0 is the formal high-performance generic RT-core operator release.
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
