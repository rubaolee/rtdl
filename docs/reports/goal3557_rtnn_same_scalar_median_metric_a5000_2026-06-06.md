# Goal3557 RTNN Same-Scalar Median Metric A5000 Evidence

Date: 2026-06-06

## Purpose

Goal3556 added `elapsed_median_sec` to the RTNN prepared 3D runner and moved the current Goal2626 RTNN rows to that scalar. The first targeted A5000 rerun exposed a comparison bug: the v2.3 overlay emitted `elapsed_median_sec`, but the v2.3 Goal2626 registry still selected `elapsed_sec`.

Goal3557 fixes that overlay selector and reruns the targeted RTNN row with both sides using the same scalar.

## Fix

- Updated the v2.3 measurement-overlay patch so both v2.3 RTNN rows select `primary_metric_path=("elapsed_median_sec",)`.
- Strengthened the Goal3556 test to assert that the overlay contains those primary-metric selectors.
- Reapplied the corrected overlay to a clean v2.3 checkout on the A5000 pod and verified the registry before running.

## A5000 Result

Artifact directory:

`docs/reports/goal3557_rtnn_same_scalar_median_metric_a5000/`

| Row | v2.3 median sec | v2.8/v2.9 median sec | Speedup |
| --- | ---: | ---: | ---: |
| `rtnn_optix_prepared_3d_ranked_summary` | 0.001328629 | 0.001356328 | 0.979578x |

Both sides met the 10-second observed target:

- v2.3 observed measured seconds: `12.667153`
- v2.8/v2.9 observed measured seconds: `12.358864`
- target plan met: `true/true`
- target observed met: `true/true`

## Interpretation

The corrected same-scalar packet moves RTNN from the earlier Goal3553 `0.956x` observation to near parity at `0.980x`. This is not a performance win, but it is no longer a major negative row. The remaining gap is small enough that the next full packet should use this corrected overlay before choosing any RTNN code-tuning target.

The earlier `goal3556_rtnn_median_metric_a5000` targeted run is rejected as final evidence because it compared v2.3 `elapsed_sec` to v2.8/v2.9 `elapsed_median_sec`.

## Boundaries

This is internal benchmark evidence only.

This goal does not authorize:

- release or tag action;
- public v2.9 speedup claims;
- broad RT-core speedup claims;
- whole-app acceleration claims;
- true zero-copy claims.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3557_rtnn_same_scalar_median_metric_a5000_test tests.goal3556_rtnn_median_repeat_metric_hardening_test
```

Pod validation:

```text
Goal3556 + Goal2626 registry tests: Ran 15 tests OK
Corrected v2.3 overlay registry check: RTNN Embree/OptiX primary_metric_path == ("elapsed_median_sec",)
Targeted RTNN A5000 same-scalar run: observed target met true/true
```

## Next Step

Refresh the full 11-row v2.9/v2.3 A5000 packet with the corrected v2.3 overlay. If the packet remains target-compliant, the next performance triage should focus on rows that remain materially below parity after same-scalar cleanup.
