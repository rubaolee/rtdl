# Goal4954-C Grouped Carrier Prototype Results

Date: 2026-07-04

Status: completed_pending_review

Parent:

- `history/internal_docs/goal4954c_measured_pre_fusion_bottleneck_prototype_plan_2026-07-04.md`
- Antigravity verdict: `approve_goal4954c_grouped_carrier_prototype`

Exit label requested:

`grouped_carrier_win_continue`

## Purpose

Goal4954-C C1 tested whether the largest measured pre-fusion bottleneck from
Goal4954-B could be reduced without RTDL core/runtime changes and without
Layer 4 fusion.

Goal4954-B's largest measured components were:

- binary grouped row construction: `1.748s`;
- descriptor-pair consumer: `0.688s`.

C1 replaced the flat repeated-label representation with a grouped columnar
carrier.

## What Changed

Changed only the internal app-owned measurement representation.

Goal4954-B flat representation repeated group labels per point row:

```text
group_id, item_order, x, y, label_a, label_b, alt_label,
source_side_id, source_element_id, keep
```

Goal4954-C grouped carrier stores:

Group-level columns:

- `group_offset`
- `group_length`
- `label_a`
- `label_b`
- `alt_label`
- `source_side_id`
- `source_element_id`

Point-level columns:

- `x`
- `y`

The downstream consumer computes descriptor-pair counts from group-level labels
and `group_length`, avoiding repeated label columns per point.

## What Did Not Change

Held constant:

- public County x Soil input;
- RTDL public LSI route;
- intersection reprojection implementation;
- sort implementation;
- public point-location/PIP route;
- midpoint generation;
- midpoint PIP;
- AuthorOfficial overlay-compute reference;
- OptiX SDK/native build;
- no RTDL core/runtime edits;
- no public API exposure;
- no Layer 4 fusion.

## Environment

Same as Goal4954-B:

```text
POD: root@213.173.108.15:14399
GPU: NVIDIA RTX 4000 Ada Generation
RTDL HEAD: 8cc0597b
OptiX SDK: NVIDIA/optix-sdk v9.0.0
OptiX SDK commit: 083bffe2011019ca2b9078f53206ff9f0193b63a
RTDL OptiX library: /root/rtdl_goal4954/build/librtdl_optix.so
```

## Artifacts

Goal4954-C run artifacts:

```text
history/internal_docs/goal4954c_artifacts/grouped_carrier_summary_run1.json
history/internal_docs/goal4954c_artifacts/grouped_carrier_summary_run2.json
history/internal_docs/goal4954c_artifacts/grouped_carrier_summary_run3.json
```

Internal script:

```text
history/internal_docs/goal4954c_grouped_carrier_measure.py
```

## 3-Run Results

| Metric | Run 1 | Run 2 | Run 3 | Median |
|---|---:|---:|---:|---:|
| writer-free hot path (s) | 3.883113 | 3.832422 | 3.835318 | 3.835318 |
| ratio vs AuthorOfficial overlay compute | 92.24x | 91.03x | 91.10x | 91.10x |
| LSI rows (s) | 1.190062 | 1.155147 | 1.149959 | 1.155147 |
| reprojection (s) | 0.749170 | 0.736441 | 0.736632 | 0.736632 |
| sort total (s) | 0.839912 | 0.842339 | 0.863470 | 0.842339 |
| grouped columnar carrier construction (s) | 0.964725 | 0.961306 | 0.948936 | 0.961306 |
| grouped descriptor-pair consumer (s) | 0.062514 | 0.060369 | 0.060236 | 0.060369 |

Binary grouped carrier shape:

```text
group_count: 64,459
point_row_count: 673,371
skipped_group_count: 1,756
```

Downstream consumer:

```text
unique descriptor pairs: 28,815
total point rows represented: 673,371
```

## Comparison Against Goal4954-B

| Metric | Goal4954-B flat rows median | Goal4954-C grouped carrier median | Change |
|---|---:|---:|---:|
| writer-free hot path | 5.309487s | 3.835318s | -1.474169s |
| writer-free hot speedup | baseline | 1.384x | win |
| ratio vs AuthorOfficial overlay compute | 126.12x | 91.10x | improved but still far |
| binary construction | 1.748347s | 0.961306s | -0.787041s |
| descriptor consumer | 0.688320s | 0.060369s | -0.627951s |
| construction + consumer | 2.436667s | 1.021675s | 2.385x faster |

## Interpretation

C1 is a real pre-fusion win:

- It reduces total writer-free hot time by `1.474s`.
- It improves the binary construction + downstream consumer path by `2.385x`.
- It does so without RTDL core/runtime changes.
- It confirms that grouped columnar carriers are the right representation for
  binary overlay intermediates.

But C1 does not close the overall gap:

```text
3.835318s / 0.0421s = 91.10x slower than AuthorOfficial overlay compute
```

Remaining median pre-fusion components after C1:

| Remaining phase | Median seconds |
|---|---:|
| LSI rows | 1.155147 |
| reprojection | 0.736632 |
| sort total | 0.842339 |
| grouped carrier construction | 0.961306 |
| grouped descriptor consumer | 0.060369 |

The next meaningful pre-fusion targets are:

1. reprojection + sort columnarization;
2. grouped carrier construction further reduction;
3. LSI row production/warm-control investigation.

Layer 4 traversal fusion remains out of scope.

## Generic-System Boundary

This remains app-owned prototype work. It is not yet RTDL core progress.

The grouped carrier design is generic, but promotion into RTDL core would still
require the Goal4954-A non-RayJoin proof:

- no RayJoin imports;
- no CDB requirement;
- no AuthorOfficial dependency;
- same grouped carrier consumed by a non-RayJoin spatial workload.

## Decision

Close Goal4954-C C1 as:

`grouped_carrier_win_continue`

Recommended next:

Goal4954-D should target reprojection/sort columnarization and/or a non-RayJoin
proof of the grouped carrier. The choice should be made explicitly:

- If the goal is RayJoin public-sample speed, attack reprojection/sort next.
- If the goal is RTDL-core promotion, produce the non-RayJoin grouped-carrier
  proof next.

Because the owner objective is to complete Goal4954's pre-fusion work while
preserving RTDL genericity, the best next step is:

```text
Goal4954-D: non-RayJoin grouped-carrier proof + columnar reprojection/sort plan
```

No Layer 4 fusion is authorized by this result.
