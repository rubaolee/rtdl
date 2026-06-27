# Goal3951: Direct CUDA PTX Loader Debt Inventory

Date: 2026-06-08

## Purpose

Goals3933, 3942, and 3946 repaired driver-loaded CUDA module paths that were
better served by CUBIN loading on current RTX pods. Goal3951 records the
remaining direct `cuModuleLoadData(..., ptx.c_str())` sites so future hardening
can proceed from a checklist instead of rediscovering failures row by row.

This is an inventory only. It does not convert the remaining sites.

## Current Remaining Driver-Loaded PTX Sites

| File | Line | Module | Kernel file |
| --- | ---: | --- | --- |
| none | - | - | - |

## Recommended Migration Order

No remaining direct `cuModuleLoadData(..., ptx.c_str())` debt is currently
tracked by this inventory. OptiX pipeline PTX remains out of scope and should not
be counted as direct driver-loaded CUDA-module PTX debt.

## Follow-Up

Goal3952 migrated the device-column grouped reduction and segment-pair count
helpers out of this debt list. The current remaining driver-loaded PTX count is
`16`.

Goal3954 migrated the partner triangle/ray device-column pack helpers out of
this debt list. The current remaining driver-loaded PTX count is `12`.

Goal3958 migrated the point-group-nearest split/reduce helpers out of this debt
list. The current remaining driver-loaded PTX count is `9`.

Goal3962 migrated the collect-k helpers out of this debt list. The current
remaining driver-loaded PTX count is `0`.

## Boundary

This goal records compatibility debt. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, AMD performance
wording, paper reproduction, package-install wording, or app-specific
native-engine logic.
