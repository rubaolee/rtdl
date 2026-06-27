# Goal3559 RayDB Sum/Count Stability Probe

Date: 2026-06-06

## Purpose

Goal3558 refreshed the full A5000 v2.9/v2.3 packet after RTNN same-scalar cleanup. The weakest rows in that single full-packet run were RayDB sum (`0.944x`) and RayDB count (`0.973x`).

Goal3559 checks whether those RayDB gaps are stable before changing code.

## Probe

Artifact directory:

`docs/reports/goal3559_raydb_sum_count_probe_a5000/`

Protocol:

- GPU: NVIDIA RTX A5000
- modes: `count`, `sum`
- lanes: v2.3 overlay and v2.8/v2.9 current
- copies: `120000`
- warmup: `2`
- repeat: `20000`
- trials: 3 alternating trials per mode/lane
- primary scalar: `metadata.timings.query_median_sec`

## Results

| Mode | v2.3 median sec | v2.8/v2.9 median sec | v2.8/v2.9 speedup |
| --- | ---: | ---: | ---: |
| count | 0.000589041 | 0.000590743 | 0.997119x |
| sum | 0.000748003 | 0.000757813 | 0.987055x |

Per-trial scalar values:

| Mode | Lane | Trial values |
| --- | --- | --- |
| count | v2.3 | 0.000589041, 0.000601526, 0.000550143 |
| count | v2.8/v2.9 | 0.000590743, 0.000555901, 0.000592432 |
| sum | v2.3 | 0.000787175, 0.000748003, 0.000745556 |
| sum | v2.8/v2.9 | 0.000787120, 0.000757813, 0.000744855 |

## Interpretation

The RayDB rows are not stable regressions at the scale probed here. Count is effectively parity (`0.997x`), and sum is a small near-parity negative (`0.987x`). The Goal3558 full-packet RayDB sum result should be treated as a one-run weak observation, not a code-change mandate.

This means the current v2.9 performance picture is:

- no major negative row after RT-DBSCAN and RTNN cleanup;
- full-packet geomean remains positive (`1.0165x`);
- median remains near parity (`0.9938x`);
- remaining work should prioritize broader repeat robustness and claim-boundary reporting, or only tune rows that show repeated stable gaps under alternating probes.

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
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3559_raydb_sum_count_stability_probe_test tests.goal3558_v2_9_full_packet_after_rtnn_same_scalar_test
```

## Next Step

Do not change RayDB code solely from Goal3558's single weak sum row. The next useful v2.9 work is either a repeated full-packet summary protocol or targeted alternating probes for any remaining row that appears below parity in a future packet.
