# Goal3562 RTNN Alternating Same-Scalar Probe

Date: 2026-06-06

## Purpose

Goal3560 Claude review accepted the Goals3556-3559 cleanup with a boundary: RTNN needed an alternating multi-trial same-scalar probe because Goal3557 targeted evidence (`0.979578x`) and Goal3558 full-packet evidence (`1.061225x`) disagreed.

Goal3562 runs that probe.

## Protocol

Artifact directory:

`docs/reports/goal3562_rtnn_alternating_same_scalar_probe_a5000/`

- GPU: NVIDIA RTX A5000
- v2.3 and v2.8/v2.9 point-file SHA-256: `ad1b4b58b569f7012ef62ab19b602b4048c3bd57f2fd095f3743e0701cf0b0e3`
- query count: `65536`
- search count: `65536`
- radius: `0.02`
- `k_max`: `50`
- result mode: `ranked-summary-raw`
- repeat: `9000`
- trials: 5 alternating trials per lane
- scalar: `elapsed_median_sec`

## Results

| Lane | Median of trial medians |
| --- | ---: |
| v2.3 | 0.001387625 |
| v2.8/v2.9 | 0.001372598 |

Overall v2.8/v2.9 speedup vs v2.3: `1.010948x`.

Per-trial values:

| Trial | v2.3 median sec | v2.8/v2.9 median sec |
| ---: | ---: | ---: |
| 1 | 0.001387625 | 0.001586790 |
| 2 | 0.001334101 | 0.001325731 |
| 3 | 0.001542503 | 0.001372598 |
| 4 | 0.001495484 | 0.001400112 |
| 5 | 0.001362249 | 0.001338017 |

## Interpretation

RTNN is near parity. The Goal3558 single-packet `1.061x` value should not be treated as a stable positive row, and the Goal3557 targeted `0.980x` value should not be treated as a stable negative row. The better current interpretation is `~1.01x` under a 5-trial alternating same-scalar probe.

This closes the required Goal3560 review item.

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
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3562_rtnn_alternating_same_scalar_probe_test tests.goal3561_near_parity_rows_probe_test
```

## Next Step

Treat RTNN as near parity in v2.9 summaries. Future work should focus on repeated-packet robustness rather than RTNN code changes.
