# Goal2809 Hausdorff Warm/Tuned v2.5 Entrypoint

Date: 2026-05-31

Verdict: accept-with-boundary.

Goal2809 fixes a measurement flaw found by the Goal2808 current-head harness rerun: the Hausdorff/X-HD canonical entrypoint warmed the CuPy grouped-grid exact baseline but timed the RTDL/OptiX exact path cold. That made the reported RTDL/CuPy ratio look much worse than the steady-state path.

This goal does not claim RTDL beats CuPy, X-HD, or any paper implementation. It makes the benchmark fairer and records the remaining gap.

## Code Changes

| File | Change |
| --- | --- |
| `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py` | Added `default_adaptive_target_points_per_group()` and changed the adaptive grouped RT witness default to `growth_factor=8.0` with a 512-point minimum adaptive group size. |
| `scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py` | Added RTDL warmup, repeated median timing for both CuPy and RTDL paths, and explicit metadata for adaptive growth/group defaults. |
| `docs/research/future_version_to_do_list.md` | Captured the remaining exact-Hausdorff design gap as a future v2.5+ runtime/primitive hardening item. |
| `tests/goal2809_hausdorff_warm_tuned_entrypoint_test.py` | Guards the tuned defaults, final artifact, and claim boundary. |

## Pod Evidence

Clean-from-Git pod artifact:

`docs/reports/goal2809_hausdorff_warm_tuned_entrypoint_pod/hausdorff_xhd_v25_warm_median_4096.json`

| Field | Value |
| --- | --- |
| Source commit | `b328b9b3aafc14a862f1287a2948fa47474fe690` |
| Source dirty state | `[]` |
| GPU | `NVIDIA RTX A5000, 570.211.01` |
| Status | `pass` |
| Points | 4096 x 4096 |
| CuPy grouped-grid exact median | 0.004425011 s |
| RTDL/OptiX adaptive grouped exact median | 0.077697727 s |
| RTDL/CuPy elapsed ratio | 17.558764x |
| RTDL warmup | 1 run, 0.573615 s |
| Repeat count | 3 |
| Adaptive growth factor | 8.0 |
| Adaptive target points per group | 512 |
| Distance error | 0.0 |
| RT cores used | true |

The previous Goal2808 current-head artifact reported 151.635488x slower for the RTDL path on the same 4096x4096 scenario. Goal2809 reduces that to 17.558764x slower by removing cold-start timing asymmetry and using better existing adaptive parameters.

## Interpretation

This is a real benchmark-quality improvement, not a performance victory. The exact RTDL/OptiX path is now measured more fairly, but the optimized CuPy grouped-grid baseline is still much faster for this synthetic row.

The next useful work is generic runtime work, not a Hausdorff-specific native engine shortcut: device-resident nearest-witness/max-distance continuation, active-set compaction, and pruning that avoids repeated host-driven worklist churn.

## Claim Boundary

- No public speedup claim is authorized.
- No RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-X-HD claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No native engine customization is introduced.

## Validation

Local validation:

```text
py -3 -m py_compile examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py
py -3 -m unittest tests.goal2801_hausdorff_xhd_v25_canonical_entrypoint_test tests.goal2121_xhd_point_group_hausdorff_optix_enhancement_test
Ran 10 tests in 0.096s
OK
```

Pod command:

```text
python3 scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py --points-a 4096 --points-b 4096 --output /tmp/goal2809_hauptune/hausdorff_xhd_v25_warm_median_4096.json
```

Final clean-pod guard validation after this packet was pushed:

```text
commit: 0375bc607d835a9d540f2c7bd369dd3ca555f4eb
git status --short: 0 dirty lines
python3 -m unittest tests.goal2809_hausdorff_warm_tuned_entrypoint_test tests.goal2801_hausdorff_xhd_v25_canonical_entrypoint_test
Ran 10 tests in 0.001s
OK
```
