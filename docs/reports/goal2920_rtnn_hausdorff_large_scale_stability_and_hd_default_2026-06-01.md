# Goal2920: RTNN And Hausdorff Large-Scale Stability

Date: 2026-06-01
Status: implemented; full packet rerun still required

## Purpose

Goal2914 flagged two performance-stability risks in the scaled v2.5 packet:

- RTNN uniform was green but still short in absolute time;
- Hausdorff/X-HD was green but near parity.

Goal2920 runs larger targeted pod probes and uses the result to tune the
Hausdorff reduced grouped witness default without changing the RTDL native
engine or adding app-specific native logic.

Artifact directory:

`docs/reports/goal2920_hausdorff_rtnn_large_probe_pod/`

## RTNN Result

The RTNN 262,144-point repeat-9 probe removes the short-row concern for the
same-contract CuPy-grid comparison:

| Distribution | RTDL median sec | CuPy median sec | CuPy/RTDL |
| --- | ---: | ---: | ---: |
| uniform | `0.000962` | `0.003598` | `3.740x` |
| clustered | `0.222661` | `0.438910` | `1.971x` |
| shell | `0.033273` | `0.144478` | `4.342x` |

All rows pass correctness checks against the same-contract CuPy grid opponent.
This is still internal evidence, not a public RTNN speedup claim.

## Hausdorff Finding

The larger 16,384 x 16,384 repeat-9 probe exposed a real instability with the
old reduced grouped witness default:

| Configuration | RTDL median sec | CuPy median sec | RTDL/CuPy |
| --- | ---: | ---: | ---: |
| old default target `2048`, repeat 9 | `0.023916` | `0.013889` | `1.722x` |

The follow-up sweep showed that the issue was the reduced group target, not
the RT-core path itself:

| Configuration | RTDL median sec | CuPy median sec | RTDL/CuPy |
| --- | ---: | ---: | ---: |
| target `512` | `0.015222` | `0.015678` | `0.971x` |
| target `1024` | `0.014947` | `0.015712` | `0.951x` |
| target `2048` | `0.014787` | `0.015724` | `0.940x` |
| target `4096` | `0.013961` | `0.015662` | `0.891x` |
| target `8192` | `0.015106` | `0.015714` | `0.961x` |
| adaptive method | `0.345015` | `0.015682` | `22.001x` |
| target `2048` plus threshold seed | `0.042191` | `0.015782` | `2.673x` |

The repeat-9 confirmation for target `4096` remained green:

| Size | RTDL median sec | CuPy median sec | RTDL/CuPy | Exact match |
| --- | ---: | ---: | ---: | --- |
| 8192 x 8192 | `0.007911` | `0.008340` | `0.949x` | yes |
| 16384 x 16384 | `0.014761` | `0.015675` | `0.942x` | yes |

## Code Change

`scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py` now defaults
`DEFAULT_REDUCED_TARGET_POINTS_PER_GROUP` to `4096` and bumps the entrypoint
version to:

`rtdl.goal2801.hausdorff_xhd_v2_5_canonical_entrypoint.v2.reduced_target4096`

This changes the canonical app harness parameter. It does not change the RTDL
native engine and does not add app-specific native logic.

## Boundary

This is not a v2.5 release authorization, public speedup claim, broad RT-core
claim, whole-app speedup claim, true-zero-copy claim, automatic Triton-selection
claim, package-install claim, or paper-reproduction claim.

The targeted probes justify changing the Hausdorff harness default, but the
seven-app packet must be rerun after this commit before readiness should point
at the new default.

## Validation

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal2801_hausdorff_xhd_v25_canonical_entrypoint_test tests.goal2920_rtnn_hausdorff_large_scale_stability_test

Ran 9 tests
OK
```
