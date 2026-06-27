# Goal2642 Report: Barnes-Hut Expanded-Membership Lowering Embree vs OptiX Performance

Date: 2026-05-27

Status: completed internal app-level Embree-vs-OptiX timing pass for the
Goal2641 Barnes-Hut aggregate-frontier lowering.

## Purpose

Goal2641 made Barnes-Hut aggregate-frontier discovery use the generic
`EXPANDED_AABB_POINT_MEMBERSHIP_2D` primitive. This report measures whether
that RT-core-assisted path wins against the same lowering using Embree.

This is still not a whole RT-BarnesHut paper reproduction. It measures the
RTDL benchmark-app lowering path:

```text
bucketized aggregate tree
  -> app-owned near-zone AABBs
  -> EXPANDED_AABB_POINT_MEMBERSHIP_2D rows
  -> Python opening continuation
  -> Python/app force interpretation
```

## Pod Environment

```text
ssh root@194.68.245.16 -p 22072 -i ~/.ssh/id_ed25519_rtdl_codex
GPU: NVIDIA RTX A5000, driver 565.57.01
CUDA: 12.8
OptiX SDK: 8.1.0
Embree: 4.3.0
RTDL pod workdir: /workspace/rtdl_goal2640_min
```

The OptiX path used:

```text
rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows
```

That symbol is app-name-free and implements generic point/AABB membership row
emission.

## Commands

Smoke with reference validation:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  python3 scripts/goal2642_barnes_hut_embree_vs_optix_lowering_perf.py \
  --case 128:8 \
  --repeats 1 \
  --validate-first \
  --output docs/reports/goal2642_barnes_hut_embree_vs_optix_smoke.json
```

Scale ladder:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  python3 scripts/goal2642_barnes_hut_embree_vs_optix_lowering_perf.py \
  --case 512:16 \
  --case 2048:32 \
  --repeats 3 \
  --output docs/reports/goal2642_barnes_hut_embree_vs_optix_scale.json
```

Large case:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  python3 scripts/goal2642_barnes_hut_embree_vs_optix_lowering_perf.py \
  --case 8192:32 \
  --repeats 1 \
  --output docs/reports/goal2642_barnes_hut_embree_vs_optix_8192.json
```

## Results

| Bodies | Frontier Rows | Near-Zone Rows | Embree Total s | OptiX Total s | OptiX Total Speedup | Embree Membership s | OptiX Membership s | Membership Speedup |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 128 | 4,543 | 1,340 | 0.0947 | 0.7066 | 0.13x | 0.0405 | 0.6543 | 0.06x |
| 512 | 28,988 | 7,362 | 0.3946 | 0.2816 | 1.40x | 0.1156 | 0.0127 | 9.09x |
| 2,048 | 258,495 | 37,087 | 3.5560 | 1.8440 | 1.93x | 1.6563 | 0.0539 | 30.74x |
| 8,192 | 1,188,963 | 203,083 | 74.9243 | 11.1908 | 6.70x | 66.0805 | 0.8848 | 74.68x |

All compared Embree and OptiX cases produced matching row counts and matching
aggregate-frontier summary counts. The 128-body smoke case also validated exact
parity against `collect_aggregate_frontier_2d`.

## Interpretation

The conclusion is scale-dependent:

- At 128 bodies, OptiX loses because one-shot GAS setup, launch, and row
  transfer dominate a very small workload.
- At 512 bodies, OptiX wins total app-lowering time by 1.40x and the generic
  membership primitive by 9.09x.
- At 2,048 bodies, OptiX wins total app-lowering time by 1.93x and the generic
  membership primitive by 30.74x.
- At 8,192 bodies, OptiX wins total app-lowering time by 6.70x and the generic
  membership primitive by 74.68x.

The RT primitive is already strong. The remaining total-time limiter is not RT
candidate discovery; it is app-side Python continuation and force
interpretation. At 8,192 bodies, OptiX membership takes 0.885 s while Python
force interpretation takes 6.867 s.

## Engineering Conclusion

For this Barnes-Hut benchmark app, the Embree-vs-OptiX question is now answered
for the Goal2641 lowering:

```text
OptiX/RT wins for meaningful scales, but total speedup is capped by Python
continuation and force interpretation.
```

The next real optimization is not another app-specific native Barnes-Hut kernel.
It should be one of:

1. a generic device-resident continuation primitive over point/AABB row pages;
2. a generic compacted row pipeline to avoid host row materialization;
3. a partner-resident force/vector reduction path consuming generic frontier
   rows.

## Claim Boundary

Authorized internal statement:

> The Barnes-Hut aggregate-frontier lowering through
> `EXPANDED_AABB_POINT_MEMBERSHIP_2D` shows OptiX/RT wins over Embree at
> 512+ bodies on an RTX A5000, with 6.70x total app-lowering speedup at 8,192
> bodies and 74.68x speedup for the generic membership primitive.

Not authorized:

- public whole-Barnes-Hut speedup wording;
- RT-BarnesHut paper reproduction claims;
- claims that native engine code embeds Barnes-Hut theta/mass/force logic;
- claims that full continuation and force reduction are device-resident.
