# Goal2805 v2.5 Broad Clean Pod Regression Gate

Date: 2026-05-31

Status: clean pod gate passed.

Verdict: accept-with-boundary.

## Purpose

Goal2805 records a broad v2.5 regression sweep after Goal2804 refreshed clean
artifact metadata and consensus. This is not a new performance result. It is a
clean-from-Git validation that the current v2.5 contract, partner, neutral
seam, manifest, selection-guidance, and app-harness reader tests still agree.

## Pod Environment

```text
Host: root@69.30.85.171
Port: 22167
Key: C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
Checkout: /root/rtdl_goal2785_work
Commit: 6faf7de8
GPU: NVIDIA RTX A5000, driver 570.211.01
```

Runtime environment:

```text
PYTHONPATH=src:.
RTDL_OPTIX_LIB=/root/rtdl_goal2785_work/build/librtdl_optix.so
RTDL_OPTIX_LIBRARY=/root/rtdl_goal2785_work/build/librtdl_optix.so
RTDL_EMBREE_PREFIX=/usr
```

## Scope

The 50-module pod slice covered:

- v2.5 partner-continuation contract and preview gate;
- Triton segmented, grouped, compact, bounded collect, top-k, vector-sum, and
  edge-list component previews;
- Numba fallback preview;
- neutral buffer seam, transfer planning, and torch-carrier reconciliation;
- partner support matrix and selection guidance;
- determinism policy;
- v2.5 tiered benchmark manifest;
- primitive-first RayDB, triangle-counting, Spatial RayJoin, and LibRTS rows;
- Tier B current harness readers for RTNN, Hausdorff/X-HD, RT-DBSCAN, and
  Barnes-Hut;
- Goal2804 clean artifact metadata and consensus checks.

## Result

```text
Ran 239 tests in 116.260s
OK
```

## Boundary

This gate does not authorize:

- v2.5 release;
- public speedup claims;
- whole-app speedup claims;
- true-zero-copy claims;
- Triton preview auto-selection;
- native app-specific engine logic.

The accepted claim is narrower: the current v2.5 internal evidence and
metadata package is coherent across the broad clean-pod regression slice.
