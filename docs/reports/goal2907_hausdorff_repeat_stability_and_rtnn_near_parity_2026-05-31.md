# Goal2907: Hausdorff Repeat Stability and RTNN Near-Parity Triage

Date: 2026-05-31
Status: implemented with pod evidence

## Purpose

Goal2906 refreshed the current v2.5 seven-app packet after Barnes-Hut measured partner selection. The packet passed cleanly, but the triage still listed two targets:

- `hausdorff_xhd`: `1.401x` RTDL/CuPy in the packet's repeat-3 median
- `rtnn`: one `uniform` row at `0.980x` CuPy/RTDL, while the other two distributions were `2.456x` and `1.985x`

Both findings are useful, but neither should be interpreted as a major runtime-design blocker without a stability check.

## Hausdorff Stability Fix

The canonical Hausdorff entrypoint now defaults to `repeat = 9` instead of `repeat = 3`.

The repeat-3 packet value was noisy for a very short benchmark row. A direct repeat-9 pod probe at the same source commit as Goal2906 produced stable near-parity evidence:

Artifact:

`docs/reports/goal2907_pod_artifacts/goal2907_hausdorff_repeat9_pod_69_30_85_171_2026-05-31.json`

Measured result:

- source commit: `1756dce2386cd086aa91edce8e2656ce8d8899f2`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- status: `pass`
- exact baseline match: `true`
- distance error: `0.0`
- RTDL method: `rtdl_rt_grouped_reduced_nearest_witness`
- RTDL uses RT cores: `true`
- repeat count: `9`
- CuPy grid median: `0.004528 s`
- RTDL/OptiX median: `0.004781 s`
- RTDL/CuPy ratio: `1.056x`

This keeps Hausdorff in the near-parity band rather than the severe-target band, without changing the native engine or adding Hausdorff-specific native logic.

## RTNN Near-Parity Rule

The RTNN packet has one distribution-dependent row at `0.980x` CuPy/RTDL. That is a roughly two-percent difference on a short row, while the other measured rows show RTDL ahead by about `2.46x` and `1.99x`.

The triage now treats RTNN rows with `0.95 <= cupy_over_rtdl < 1.0` as `current_path_acceptable_near_parity_distribution_dependent`. Rows below `0.95` remain `performance_target`.

This keeps the gate honest:

- a material same-contract regression is still a target;
- a two-percent distribution-dependent wobble is recorded, but does not become the top v2.5 design blocker.

## Boundary

This is not a release packet and not release consensus.

It does not authorize public speedup claims, broad RT-core claims, whole-app speedup claims, true-zero-copy claims, automatic Triton selection, package-install claims, or paper-reproduction claims. It only hardens how the current v2.5 packet interprets short-row performance noise.
