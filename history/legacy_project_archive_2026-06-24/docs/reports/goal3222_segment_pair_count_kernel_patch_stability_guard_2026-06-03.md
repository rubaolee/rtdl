# Goal3222: Segment-Pair Count Kernel Patch Stability Guard

Date: 2026-06-03

## Purpose

Goal3222 closes the remaining informational kernel-patch stability debt carried
forward from the Goal3214 and Goal3219 Claude reviews.

The fused dense segment-pair left-id count route is intentionally built by
starting from the canonical generic segment-pair intersection OptiX kernel and
patching three snippets:

- the row-stream record struct,
- the launch-parameter struct,
- the any-hit row write block.

The runtime already throws if those snippets are absent when the OptiX pipeline
is built. Goal3222 adds a static kernel-patch stability guard so this drift is
caught by ordinary unit tests before a pod-only runtime compile path is reached.

## Actions

Added `tests/goal3222_segment_pair_count_kernel_patch_stability_test.py`.

The guard verifies:

- the canonical segment-pair kernel still contains the exact three patch anchors
  once,
- both generated device-column pipelines patch the same canonical anchors,
- each patch path keeps explicit fail-closed "snippet not found" errors,
- the dense left-id count replacement writes a generic grouped count column with
  atomic count updates and `atomicOr(params.overflow, 1u)`,
- the dense left-id count path does not materialize row-stream records.

## Boundary

This is a static kernel-patch stability guard. It does not change the native ABI,
does not change the Python route contract, and does not change timings. It does
not authorize release, does not authorize public speedup claims, does not
authorize broad RT-core claims, does not authorize true zero-copy claims, and
does not authorize RayJoin paper-reproduction claims.

The string-patch construction still exists. Goal3222 narrows the maintenance
risk by making upstream-source drift visible in ordinary unit tests, rather than
claiming that the generated-kernel design is fully replaced.
