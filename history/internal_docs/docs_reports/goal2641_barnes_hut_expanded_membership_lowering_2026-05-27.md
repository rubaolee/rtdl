# Goal2641 Report: Barnes-Hut Aggregate-Frontier Lowering Through Generic Expanded AABB Membership

Date: 2026-05-27

Status: CPU/Embree implementation complete; OptiX mode validated on the
Goal2640 RTX A5000 pod using the generic RT-core primitive.

## Purpose

Goal2640 proved a generic RT-core primitive:

```text
EXPANDED_AABB_POINT_MEMBERSHIP_2D
```

This goal uses that primitive from the Barnes-Hut benchmark app without adding
Barnes-Hut-specific native engine logic.

The app-level lowering is:

1. Build the existing bucketized aggregate tree.
2. For each aggregate node, construct an app-owned conservative near-zone AABB.
3. Use `EXPANDED_AABB_POINT_MEMBERSHIP_2D` to collect generic
   `(source_id, node_id, metadata_flags)` near-zone candidate rows.
4. In Python app code, apply the Barnes-Hut opening rule:
   - if a node contains the source, descend;
   - if the source is outside the near-zone rows, safely accept the aggregate;
   - if the source is inside the near zone, do the exact theta/distance check;
   - if still not open, descend or emit exact leaf-body rows.
5. Interpret accepted aggregate rows and exact fallback rows with app/partner
   force math outside the engine.

## Why The Lowering Is Correct

Barnes-Hut accepts an aggregate when:

```text
(2 * node.half_size) / distance(source, node.center) < theta
```

Equivalently, the source is far enough away:

```text
distance(source, node.center) > 2 * node.half_size / theta
```

The lowering creates a square near-zone AABB centered on the aggregate center
with half extent:

```text
2 * node.half_size / theta
```

If a source is outside that square, its Euclidean distance is definitely larger
than the radius, so the aggregate opening test is safely true. If a source is
inside the square, the app still performs the exact Euclidean theta check. This
is conservative: the primitive can over-report near candidates, but it must not
miss a near candidate that would require exact opening logic.

## Engine Boundary

Native/generic engine owns only:

- source points;
- indexed AABBs;
- IDs;
- row capacity;
- row emission.

App/Python/partner code owns:

- near-zone construction policy;
- theta;
- tree containment;
- aggregate vs exact fallback decisions;
- mass;
- force law;
- inverse-square math;
- vector reductions.

No native Barnes-Hut ABI, mass field, force field, theta field, or inverse-square
kernel was added.

## Added Modes

```text
aggregate_frontier_expanded_membership_cpu
aggregate_frontier_expanded_membership_embree
aggregate_frontier_expanded_membership_optix
```

The OptiX mode uses the generic Goal2640 point/AABB row primitive. That means
it is RT-core-assisted candidate discovery, not native Barnes-Hut traversal and
not a whole-app speedup claim.

## Local Evidence

CPU command:

```bash
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py \
  --mode aggregate_frontier_expanded_membership_cpu \
  --body-count 128 \
  --bucket-size 8
```

Result summary:

```text
accepted_aggregate_row_count: 1556
fallback_exact_row_count: 2987
frontier_row_count: 4543
near_zone_candidate_row_count: 1340
safe_far_accept_count: 1436
exact_opening_test_count: 902
baseline_validation.matches_collect_aggregate_frontier_2d: true
```

Embree command:

```bash
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py \
  --mode aggregate_frontier_expanded_membership_embree \
  --body-count 128 \
  --bucket-size 8
```

Result: same frontier counts and same baseline validation result as CPU.

## Pod OptiX Evidence

Pod:

```text
ssh root@194.68.245.16 -p 22072 -i ~/.ssh/id_ed25519_rtdl_codex
```

Command:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  python3 examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py \
  --mode aggregate_frontier_expanded_membership_optix \
  --body-count 128 \
  --bucket-size 8 \
  --require-rt-core \
  --json-out docs/reports/goal2641_optix_lowering_smoke.json
```

Result summary:

```text
accepted_aggregate_row_count: 1556
fallback_exact_row_count: 2987
frontier_row_count: 4543
near_zone_candidate_row_count: 1340
safe_far_accept_count: 1436
exact_opening_test_count: 902
membership_backend: optix
membership_rt_core_accelerated: true
native_generic_symbol: rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows
baseline_validation.matches_collect_aggregate_frontier_2d: true
```

Artifact:

```text
docs/reports/goal2641_optix_lowering_smoke.json
```

## Interpretation

The app now has a real lowering from aggregate-frontier discovery pressure onto
the generic expanded-AABB membership primitive. The lowering demonstrates how
RTDL can use RT cores for Barnes-Hut-relevant spatial candidate discovery while
preserving the app-independent engine boundary.

This is deliberately not the final full RT-BarnesHut implementation:

- Python still performs tree continuation.
- Python/app code still performs exact theta checks for near-zone hits.
- Python/app or partner code still performs force math and vector reduction.
- The next performance step is to scale the OptiX mode and decide whether
  continuation should become a generic device-resident primitive.

## Claim Boundary

Authorized:

> Barnes-Hut aggregate-frontier discovery can now be lowered through
> `EXPANDED_AABB_POINT_MEMBERSHIP_2D` near-zone candidate rows, preserving exact
> frontier parity with `collect_aggregate_frontier_2d` on local CPU/Embree and
> pod OptiX evidence.

Not authorized:

- whole Barnes-Hut speedup claims;
- public RT-BarnesHut reproduction claims;
- claims that the native engine understands theta, mass, force, or Barnes-Hut;
- claims that full aggregate-frontier continuation is device-resident.
