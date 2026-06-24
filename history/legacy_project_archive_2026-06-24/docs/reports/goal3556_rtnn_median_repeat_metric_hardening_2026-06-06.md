# Goal3556 RTNN Median Repeat Metric Hardening

Date: 2026-06-06

## Purpose

Goal3553 left `rtnn_optix_prepared_3d_ranked_summary` as a mild negative row in the full A5000 v2.9/v2.3 packet. The row was already internally repeated, but the runner and comparison registry still selected the last repeat as the primary scalar. That is too noisy for a sub-2 ms prepared query.

Goal3556 changes the RTNN prepared 3D runner to emit median/min/max repeat scalars and moves the Goal2626 benchmark registry to `elapsed_median_sec` for both RTNN Embree and OptiX current rows.

## A5000 Diagnostic Probe

Before changing the primary metric, an A5000 diagnostic probe ran three alternating v2.3/v2.8 trials with `repeat=3000`:

| Measure | v2.3 seconds | v2.8 seconds | v2.8 speedup vs v2.3 |
| --- | ---: | ---: | ---: |
| last-repeat median across trials | 0.001349749 | 0.001407324 | 0.959x |
| median-of-repeats median across trials | 0.001383608 | 0.001427201 | 0.969x |

The median-of-repeats view narrows the apparent RTNN gap, but it does not eliminate it. This goal is therefore a measurement hardening step, not a performance win.

## Changes

- Added `statistics` to `scripts/goal2348_rtnn_v2_2_external_runner.py`.
- Added `elapsed_median_sec`, `elapsed_min_sec`, and `elapsed_max_sec` to:
  - `run-rtdl-batched-3d-neighbors`
  - `run-rtdl-adaptive-partitioned-3d-neighbors`
- Updated `scripts/goal2626_benchmark_embree_optix_baseline.py` so current RTNN Embree and OptiX rows use `elapsed_median_sec` as the primary metric.
- Refreshed `docs/patches/goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch` so the v2.3 overlay can emit the same median scalar when the comparison worktree is rebuilt.
- Preserved `elapsed_sec` as the last-repeat scalar for compatibility with older reports and tests.

## Boundaries

This is internal benchmark evidence only.

This goal does not authorize:

- release or tag action;
- public v2.9 speedup claims;
- broad RT-core speedup claims;
- whole-app acceleration claims;
- true zero-copy claims.

## Interpretation

RTNN is still the next useful measured target after the harness is cleaned up. The current evidence says the stable gap is small, roughly 3 percent under this probe, and concentrated in prepared ranked-summary overhead rather than a large native traversal problem. The next full packet should use the median metric before deciding whether to tune RTNN code.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3556_rtnn_median_repeat_metric_hardening_test tests.goal3553_v2_9_full_packet_after_rt_dbscan_cleanup_test tests.goal3554_contact_manifold_phase_probe_a5000_test tests.goal3555_collect_k_microprobe_contact_correction_test
```

Result:

```text
Ran 13 tests
OK
```

The Goal3556 test directly imports the Goal2626 benchmark registry and verifies that both current RTNN rows now use `elapsed_median_sec`.

The v2.3 overlay patch was checked against a fresh v2.3 worktree before this report:

```powershell
git apply --check docs/patches/goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch
py -3 -m py_compile scripts/goal2348_rtnn_v2_2_external_runner.py scripts/goal2626_benchmark_embree_optix_baseline.py
```

## Next Step

Rebuild the v2.3 overlay worktree on the A5000 pod, rerun the targeted RTNN row using `elapsed_median_sec`, and then refresh the full 11-row v2.9/v2.3 packet if the targeted row is clean.
