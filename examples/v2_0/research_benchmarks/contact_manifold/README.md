# Bounded Contact-Witness Benchmark App

This study uses a contact/collision-flavored app to exercise one generic RTDL
behavior: bounded witness-row collection. The benchmark app may discuss contact
manifolds, but the primitive under test is only `COLLECT_K_BOUNDED`.

## Contract

- Input scene: static 2-D scene triangles plus query triangles grouped by an
  app-owned `query_group_id`.
- Witness row schema: `(query_group_id, query_triangle_id, scene_triangle_id)`.
- Correctness oracle: deterministic Python exact triangle-intersection rows.
- Optimized discovery path: generic `AABB_INDEX_QUERY_2D` broadphase rows,
  followed by app-owned exact triangle-intersection refinement. The discovery
  backend can be the CPU reference path or the generic OptiX native row path.
- Bounded output rule: collect all canonical witness rows if `valid_count <= k`.
- Overflow rule: fail closed before result materialization if `valid_count > k`.
- Native-engine boundary: no collision, contact, robot, manifold, or physics
  semantics are allowed inside the engine primitive.

## Run

From the repository root:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode scope
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode cpu_reference --dataset tiny
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode collect_k_reference --dataset tiny --witness-capacity 3
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode aabb_broadphase_collect_k --dataset grid --grid-count 512 --witness-capacity 512
RTDL_OPTIX_LIBRARY=build/librtdl_optix.so PYTHONPATH=src:. python examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode aabb_broadphase_collect_k --dataset grid --grid-count 512 --witness-capacity 512 --discovery-backend optix --discovery-row-capacity 1024
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode native_collect_k --backend embree --dataset tiny --witness-capacity 3
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode cpp_baseline --dataset grid --grid-count 512 --repeat-count 5
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode baseline_comparison --dataset grid --grid-count 512 --witness-capacity 512
```

Overflow is intentionally a non-success path:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py --mode collect_k_reference --dataset tiny --witness-capacity 2
```

The last command should raise a `COLLECT_K_BOUNDED overflowed capacity` error
instead of returning partial witness rows.

The `overflow` dataset alias uses the same tiny scene; overflow is controlled by
the witness capacity, not by a separate scene shape.

## Promotion State

This directory is a promoted internal benchmark app for generic bounded witness
collection. The promotion is limited:

- `COLLECT_K_BOUNDED` is the stable primitive under test.
- Goal2622 adds a generic `AABB_INDEX_QUERY_2D` broadphase row path so the
  optimized app path no longer performs full Python all-pairs discovery before
  bounded witness collection.
- Goal2623 adds the generic OptiX native row-output backend for the same
  `AABB_INDEX_QUERY_2D` row contract, with explicit fail-closed overflow when
  the app-provided row capacity is too small. OptiX row capacity covers the raw
  pre-deduplication bidirectional-pass hit count, so a safe app estimate may be
  larger than the final unique candidate-row count.
- Local Mac Embree parity, RTX A5000 OptiX parity, fail-closed overflow, and a
  standalone C++ CPU baseline are recorded in Goal2621 reports.
- No public speedup claim is authorized.
- Linux Embree parity has not been separately recorded; Mac Embree and Linux
  OptiX cover the generic primitive surface used for promotion.
- Exact triangle-intersection refinement and contact-summary interpretation
  remain app-owned; native generic AABB row output emits only app-agnostic
  `(query_id, indexed_id)` candidate rows.
