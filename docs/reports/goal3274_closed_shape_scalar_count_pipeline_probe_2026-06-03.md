# Goal3274 Closed-Shape Scalar-Count Pipeline Probe

Date: 2026-06-03

Status: implemented and pod-measured on NVIDIA A40; retained as a gated
neutral/negative probe, not promoted to default.

Short verdict: gated scalar-count pipeline probe, not promoted to default.
This is not a clear performance win.

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

## Pod Measurement

The pod run measured the same bounded public CDB same-slice PIP comparison as
Goal3272 at commit `45d10aa9c2dc7406c3f587d5ce20cd357d88cb53`:

1. current best `device_filtered_validated` without the gate;
2. gated scalar-count pipeline with
   `RTDL_OPTIX_POINT_PRIMITIVE_USE_SCALAR_COUNT_PIPELINE=1`;
3. same count-validation boundary against exact prepared count.

Both artifacts are source-clean and preserve count `1430`.

| Lane | Median prepared query ms | Median native count pass ms | RayJoin PIP ms | RTDL / RayJoin | Count |
| --- | ---: | ---: | ---: | ---: | ---: |
| Default shared PIP pipeline | 0.376221 | 0.261271 | 0.203260 | 1.851x | 1430 |
| Gated scalar-count pipeline | 0.369888 | 0.267136 | 0.203260 | 1.820x | 1430 |

## Interpretation

The gated scalar-count pipeline is correct, but it is not a clear performance
win. Whole prepared-query median improves only about `1.7%` versus the same-run
default control, while the native count-pass median gets slightly worse
(`0.267 ms` vs `0.261 ms`). Both lanes remain slower than the previously
accepted best scalar-count evidence range from Goals 3263/3264/3272.

Goal3274 therefore does not promote the scalar-count pipeline. The gate remains
available only for future comparison. The accepted default remains the shared
PIP pipeline with `device_filtered_validated` plus explicit `z_point` query-axis
selection.

## Boundary

This report does not authorize release, public speedup wording, broad RT-core
claims, true zero-copy claims, RayJoin paper reproduction claims, or
`RTDL beats RayJoin` claims.
