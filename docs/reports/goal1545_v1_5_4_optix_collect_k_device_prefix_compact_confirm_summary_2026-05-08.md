# Goal 1545: Device Prefix Compact Pod Runner Summary

## Verdict

Accepted by runner rule: `True`

The runner rule requires parity/topology success for all counts and a total-time improvement at the largest count.

## Results

| candidates | control total ms | candidate total ms | speedup | control launches | candidate launches | parity |
|---:|---:|---:|---:|---:|---:|---|
| 4097 | 0.153340 | 0.157087 | 0.976x | 6 | 7 | True |
| 65537 | 0.448761 | 0.429634 | 1.045x | 18 | 23 | True |
| 131072 | 0.491491 | 0.480390 | 1.023x | 18 | 23 | True |

## Artifacts

- `/root/rtdl_goal1545_pod/docs/reports/goal1545_v1_5_4_optix_collect_k_device_prefix_compact_pod_runner_2026-05-08_control_goal1543.json`
- `/root/rtdl_goal1545_pod/docs/reports/goal1545_v1_5_4_optix_collect_k_device_prefix_compact_pod_runner_2026-05-08_candidate_device_prefix.json`

## Claim Boundary

This runner summary does not authorize public speedup wording, true zero-copy wording, whole-app claims, stable primitive promotion, or release action.
