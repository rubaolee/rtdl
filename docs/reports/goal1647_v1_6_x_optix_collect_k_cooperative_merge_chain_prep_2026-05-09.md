# Goal1647 v1.6.x OptiX Collect-K Cooperative Merge-Chain Prep

## Verdict

`cooperative_merge_chain_probe_prepared_locally`

The next useful pod run should first validate cooperative-launch capability, then attempt an opt-in cooperative or multi-level merge-chain diagnostic only if the device supports it.

## Problem

Goal1641 showed that the final materialize and mark kernels are small. Goal1642 showed that the remaining final-pair wait is mostly deferred merge-chain work. Goal1644 and Goal1645 rejected smaller local candidates. Goal1646 consensus therefore moved the next serious `1.3x-1.5x` good-win attempt to merge-chain restructuring.

## Local Preparation

This change adds a narrow native capability entry point:

- `rtdl_optix_collect_k_cooperative_launch_capability(...)`
- Reports CUDA cooperative-launch support for CUDA device index `0`.
- Reports cooperative multi-device launch support for informational completeness only.
- Reports multiprocessor count, max threads per block, and max opt-in shared memory.
- Does not launch kernels.
- Does not change `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`.

It also adds `scripts/goal1647_v1_6_x_optix_collect_k_cooperative_capability_probe.py` so the next pod can produce a small JSON/Markdown capability artifact before we spend time implementing or measuring the full cooperative merge-chain candidate.

## Local Linux Validation

The Goal1647 patch was copied into a temporary clean checkout on the local Linux host `192.168.1.20` and built with:

`make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev`

That build passed. The new capability probe then loaded `build/librtdl_optix.so` through `ctypes` and returned `next_probe_allowed: true` on the local GTX 1070 smoke host. This is capability evidence only, not performance evidence and not accepted RTX performance evidence for the target long workload.

Artifacts:

- `docs/reports/goal1647_linux_local_cooperative_capability_2026-05-09.json`
- `docs/reports/goal1647_linux_local_cooperative_capability_2026-05-09.md`

## Pod Run Plan

1. Fetch/reset a clean pod checkout to `origin/main`.
2. Build OptiX with the pod's compatible OptiX SDK.
3. Run the capability probe against `build/librtdl_optix.so`.
4. If `cooperative_launch_supported` is false, stop this direction and do not burn pod time.
5. If true, implement the opt-in cooperative merge-chain diagnostic behind a new diagnostic flag only.
6. Measure against the same accepted long workload: `candidate_count=262144`, stage profile enabled, fastest accepted baseline as control.
7. Require exact parity and at least `1.15x` first-probe speedup before considering more work.

## Candidate Boundary

The candidate must remain diagnostic until accepted evidence exists:

- It must not be enabled by `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`.
- It must preserve parity with the existing collect-k result rows.
- It must report merge-event time, wrapper median, profile total time, and transfer counts.
- It must fail closed on devices without cooperative launch support.
- It must not authorize public speedup wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, release tags, or release action.

## Expected Risk

The main technical risk is cooperative launch residency: all blocks participating in a grid-wide synchronization must be resident together. The first full probe should therefore keep the grid size bounded by the device capability and should reject configurations that cannot satisfy that condition.

On multi-GPU pods, this first readiness probe is device-0-specific. If a future pod run routes RTDL work to a nonzero CUDA device, the probe should be extended to accept an explicit device index before drawing a capability conclusion for that target device.
