# Goal3274 Closed-Shape Scalar-Count Pipeline Probe

Date: 2026-06-03

Status: implemented locally as a gated scalar-count pipeline probe; pod verdict pending.

## Purpose

Goal3272 showed that the richer point-ID grouped-count device-column route is
correct, but the current RayJoin PIP scalar-count benchmark should keep using
the scalar `device_filtered_validated` contract. Goal3274 therefore tests a
narrower generic optimization: compile a dedicated OptiX pipeline for prepared
point/closed-shape scalar counts.

The new gate is:

```text
RTDL_OPTIX_POINT_PRIMITIVE_USE_SCALAR_COUNT_PIPELINE=1
```

This is not a default behavior change. The default remains the previously
accepted shared PIP pipeline until pod measurement proves the specialized path
is better.

## What Changed

The gated pipeline specializes only the generic count-only path:

- keep the same point/closed-shape predicate;
- keep the same prepared shape handle and query-axis specialization;
- remove row-output and any-hit program use from the compiled count pipeline;
- accumulate per-ray positive counts in payload register 2 and atomically add
  once per query point in raygen.

This is not a RayJoin-specific native primitive. RayJoin remains only the
benchmark app that exercises generic closed-shape membership.

## Measurement Plan

Run the same bounded public CDB same-slice PIP comparison as Goal3272:

1. current best `device_filtered_validated` without the gate;
2. gated scalar-count pipeline with
   `RTDL_OPTIX_POINT_PRIMITIVE_USE_SCALAR_COUNT_PIPELINE=1`;
3. same count-validation boundary against exact prepared count.

Pod verdict pending.

## Boundary

This report does not authorize release, public speedup wording, broad RT-core
claims, true zero-copy claims, RayJoin paper reproduction claims, or
`RTDL beats RayJoin` claims.
