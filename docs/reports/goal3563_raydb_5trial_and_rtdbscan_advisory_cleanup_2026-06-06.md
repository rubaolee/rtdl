# Goal3563 RayDB 5-Trial and RT-DBSCAN Advisory Cleanup

Date: 2026-06-06

## Purpose

Goal3560 accepted the Goal3556-3559 v2.9 performance cleanup with boundaries.
After Goal3562 closed the required RTNN alternating-probe item, three advisory
items remained:

- RayDB de-escalation used the minimum useful 3-trial median.
- RT-DBSCAN's registry seed used `--warmup 1 --repeat 3`, which gives only two
  measured hot-loop samples before the 10-second planner stretches the row.
- The v2.3 overlay patch did not explicitly warn that several app `elapsed_sec`
  fields now carry median-of-measured-repeats semantics.

Goal3563 handles those advisory items without changing the native engine.

## Changes

- Updated the RT-DBSCAN Goal2626 registry seed from `--repeat 3` to
  `--repeat 4`, preserving `--warmup 1`, so the seed command now has three
  measured hot-loop samples.
- Updated the matching Goal3551 test.
- Added a header note to
  `docs/patches/goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch`
  explaining the overlay's median-repeat timing semantics and warning against
  comparing overlay-patched `elapsed_sec` values to pre-overlay historical
  `elapsed_sec` without checking the repeat protocol.

## Pod Evidence

Artifact directory:

`docs/reports/goal3563_raydb_5trial_and_advisory_cleanup_a5000/`

Pod:

- SSH target: `root@69.30.85.203 -p 22057`
- GPU: NVIDIA RTX A5000, driver 580.126.09, 24564 MiB
- v2.3 overlay root: `/root/rtdl_goal3556_v23_overlay`
- v2.8/v2.9 root: `/root/rtdl_goal3556_current`
- v2.3 source commit: `2a28365d0246d51f3e3322b546f8a68c58632db4`
- v2.8/v2.9 source commit: `4c1e0ee3f416514c22556a4e526c617295fd0730`

## RayDB 5-Trial Results

Protocol:

- copies: `120000`
- warmup: `2`
- repeat: `20000`
- trials: 5 alternating trials per mode/lane
- primary scalar: `metadata.timings.query_median_sec`

| Mode | v2.3 median sec | v2.8/v2.9 median sec | v2.8/v2.9 speedup |
| --- | ---: | ---: | ---: |
| count | 0.000585723 | 0.000584166 | 1.002664x |
| sum | 0.000753220 | 0.000787107 | 0.956948x |

Per-trial scalar values:

| Mode | Lane | Trial values |
| --- | --- | --- |
| count | v2.3 | 0.000585723, 0.000546982, 0.000591526, 0.000552635, 0.000587521 |
| count | v2.8/v2.9 | 0.000551220, 0.000594814, 0.000590224, 0.000584166, 0.000547191 |
| sum | v2.3 | 0.000789808, 0.000753220, 0.000799409, 0.000739740, 0.000751544 |
| sum | v2.8/v2.9 | 0.000787107, 0.000751615, 0.000794423, 0.000749020, 0.000788513 |

Interpretation:

- RayDB count is now de-escalated more robustly: `1.003x` under a 5-trial
  alternating probe.
- RayDB sum should no longer be described as pure one-run noise. The five-trial
  probe measures a small but real-looking near-parity negative (`0.957x`).
  This is not a release blocker by itself because this is internal evidence,
  but it is the next concrete v2.9 tuning target if we keep pushing performance.

## RT-DBSCAN Repeat-4 Seed Probe

Protocol:

- point count: `8192`
- warmup: `1`
- repeat: `4`
- measured hot-loop samples: `3`

| Lane | metric sec | repeat | warmup | measured run count |
| --- | ---: | ---: | ---: | ---: |
| v2.3 | 0.014903007 | 4 | 1 | 3 |
| v2.8/v2.9 | 0.014715746 | 4 | 1 | 3 |

RT-DBSCAN seed speedup: `1.012725x`.

The final Goal3558 10-second packet already stretched RT-DBSCAN to hundreds of
measured hot-loop iterations (`--repeat 989` for v2.3 and `--repeat 988` for
v2.8/v2.9), so the original two-measured-sample concern did not apply to the
final packet. Goal3563 still hardens the registry seed so future dry runs start
from at least three measured samples.

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
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3563_raydb_5trial_and_rtdbscan_advisory_cleanup_test tests.goal3551_rt_dbscan_internal_repeat_hook_test tests.goal3552_rt_dbscan_a5000_internal_repeat_evidence_test
```

## Next Step

If v2.9 continues as a performance-focused internal version, the next concrete
tuning target is RayDB `sum`: inspect whether the small regression is in the
generic grouped-i64 sum dispatcher, the partner-resident setup around it, or the
benchmark's measurement path. Do not change count based on this evidence.
