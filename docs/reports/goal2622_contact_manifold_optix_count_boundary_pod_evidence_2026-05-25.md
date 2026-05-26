# Goal2622 Contact-Manifold OptiX AABB Count Boundary Pod Evidence

Date: 2026-05-25

Pod:

```text
ssh root@69.30.85.198 -p 22148 -i /Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

GPU:

```text
NVIDIA RTX A5000, driver 570.211.01
```

Workspace:

```text
/root/rtdl_goal2622
```

## Build

The pod already had OptiX headers at:

```text
/root/vendor/optix-dev-9.0.0/include/optix.h
```

OptiX backend build command:

```bash
make build-optix \
  OPTIX_PREFIX=/root/vendor/optix-dev-9.0.0 \
  CUDA_PREFIX=/usr/local/cuda-12.8 \
  NVCC=/usr/local/cuda-12.8/bin/nvcc
```

Output library:

```text
/root/rtdl_goal2622/build/librtdl_optix.so
```

## Tests

Goal2622 test command:

```bash
PYTHONPATH=src:. python3 -m unittest tests/goal2622_contact_manifold_generic_aabb_discovery_test.py
```

Result:

```text
Ran 6 tests in 0.095s
OK
```

Grid-512 local pod timing command:

```bash
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py \
  --mode baseline_comparison \
  --dataset grid \
  --grid-count 512 \
  --witness-capacity 512 \
  --repeat-count 3
```

Observed:

```json
{
  "all_pairs_count": 262144,
  "aabb_candidate_pair_count": 512,
  "aabb_pruning_ratio": 0.998046875,
  "aabb_broadphase_collect_k_best_sec": 0.32705474086105824,
  "cpu_reference_best_sec": 7.9387615118175745,
  "collect_k_reference_best_sec": 0.0011431779712438583,
  "matches_cpu_reference": true,
  "aabb_broadphase_matches_cpu_reference": true
}
```

After pressure testing, the app default was changed from `resolution=grid_count`
to adaptive `min(256, max(16, sqrt(grid_count)))`. The earlier `grid_count`
policy can become effectively quadratic for skinny AABB scenes because every
box spans the full y-range and therefore all y-cells.

With the adaptive policy, local Mac grid-512 best timing over three repeats was:

```json
{
  "all_pairs_count": 262144,
  "aabb_candidate_pair_count": 512,
  "aabb_pruning_ratio": 0.9534759521484375,
  "aabb_broadphase_collect_k_best_sec": 0.013075542025035247,
  "cpu_reference_best_sec": 5.78300075000152,
  "collect_k_reference_best_sec": 0.0008610830118414015,
  "matches_cpu_reference": true,
  "aabb_broadphase_matches_cpu_reference": true
}
```

## OptiX AABB Count Boundary

Command shape:

```python
cpu = rt.query_aabb_index_2d(
    scene_boxes,
    box_queries=query_boxes,
    operation="range_intersects",
    resolution=512,
    backend="cpu",
)
optix = rt.query_aabb_index_2d(
    scene_boxes,
    box_queries=query_boxes,
    operation="range_intersects",
    resolution=512,
    backend="optix",
)
```

Observed:

```json
{
  "primitive": "AABB_INDEX_QUERY_2D",
  "operation": "range_intersects",
  "dataset": "grid_512",
  "cpu_count": 512,
  "optix_count": 512,
  "matches_cpu": true,
  "optix_rt_core_accelerated": true,
  "cpu_elapsed_sec": 0.07328933291137218,
  "optix_elapsed_sec": 0.29551454819738865,
  "optix_claim_boundary": "Generic OptiX AABB_INDEX_QUERY_2D count-only subpath for point_contains, range_contains, and range_intersects; not LibRTS-specific."
}
```

The OptiX count path matches CPU on the contact benchmark's AABB broadphase
count. It is count-only evidence, not witness-row evidence.

## Pressure Test Addendum

CPU generic AABB row output with the initial unsafe `resolution=n` policy was
aborted at `n=32768` after it showed the skinny-grid cell explosion. The app now
uses adaptive `sqrt`-capped resolution by default.

Adaptive CPU row-output pressure on the RTX A5000 pod:

| Grid rows | Resolution | All pairs | AABB checks | Exact checks | Wall sec | Broadphase sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 16,384 | 128 | 268,435,456 | 2,097,152 | 16,384 | 4.6566408053040504 | 4.420795859768987 |
| 32,768 | 181 | 1,073,741,824 | 5,952,735 | 32,768 | 13.109987791627645 | 12.724467724561691 |
| 65,536 | 256 | 4,294,967,296 | 16,777,216 | 65,536 | 46.39201201684773 | 45.557122245430946 |

Count-only OptiX pressure on the same AABB workload:

| Grid rows | OptiX count | Matches expected | OptiX query sec | Wall sec |
| --- | ---: | --- | ---: | ---: |
| 512 | 512 | true | 0.11136076040565968 | 0.6649863235652447 |
| 1,024 | 1,024 | true | 0.0030676908791065216 | 0.013137107715010643 |
| 2,048 | 2,048 | true | 0.003988778218626976 | 0.02260599657893181 |
| 4,096 | 4,096 | true | 0.008483218029141426 | 0.045620860531926155 |
| 8,192 | 8,192 | true | 0.016092700883746147 | 0.09050010703504086 |
| 16,384 | 16,384 | true | 0.03729544021189213 | 0.21789994277060032 |

Pressure conclusion: exact refinement and bounded collection are not the
large-scale bottleneck. Generic CPU AABB row emission is. The next engine target
should be native generic AABB/candidate row output, not collision-specific
native contact logic.

## Row Output Boundary

This command intentionally fails:

```python
rt.aabb_intersection_pair_rows_2d(
    ((0, 0, 1, 1),),
    ((0, 0, 1, 1),),
    backend="optix",
)
```

Observed error:

```text
ValueError
AABB_INDEX_QUERY_2D row output is currently CPU reference only; OptiX supports count-only range_intersects until a native row emitter is added
```

## Conclusion

The pod confirms the Goal2622 boundary:

- `AABB_INDEX_QUERY_2D` has working OptiX count-only `range_intersects` parity
  for the contact grid-512 AABB workload.
- The new generic AABB row-output helper is currently CPU reference only.
- The next engine target, if this benchmark needs RT speedup evidence, is a
  native generic AABB/candidate row emitter rather than collision-specific
  engine logic.
