# Goal2659: v2.4 Benchmark Protocol Integration Slice

Status: implementation slice, local-test backed.

Date: 2026-05-27

## Purpose

Goal2658 added the v2.4 typed-buffer and prepared-session protocol foundation.
Goal2659 applies that protocol to two additional benchmark pressure points:

- bounded witness/contact-manifold, representing bounded row collection;
- RT-Graph-style triangle counting, representing row-heavy graph-to-ray
  lowering and scalar summary continuation.

This is metadata and contract integration only. It does not add Triton, Numba,
new native symbols, new pod evidence, or new public speedup claims.

## Implemented Surface

Contact-manifold benchmark:

- adds `describe_v2_4_bounded_witness_session()`;
- emits `v2_4_prepared_session` metadata from the Python reference path,
  generic AABB broadphase path, and native collect-k path;
- describes only generic int64 candidate rows, bounded int64 output rows, and
  `valid_count`;
- uses the generic primitive name `aabb_index_2d_bounded_i64_rows`;
- keeps contact/collision interpretation explicitly app-owned.

Triangle-counting benchmark:

- adds `describe_rt_graph_v2_4_prepared_session()`;
- emits `v2_4_prepared_session` metadata from RT-2A1 and RT-1A2 generic RT
  payloads;
- describes only generic rays, triangles, optional ray weights, and scalar
  summary outputs;
- uses generic primitive names `ray_triangle_weighted_any_hit_sum_3d` and
  `ray_triangle_hit_count_sum_3d`;
- keeps graph orientation, two-hop construction, and triangle-count
  interpretation app-owned.

## Boundary

The new descriptors are deliberately protocol-only:

- no native engine app vocabulary is added;
- no contact/collision native logic is introduced;
- no graph/triangle-counting native logic is introduced;
- no new zero-copy or device-resident performance claim is made;
- no existing benchmark timing row is replaced.

The descriptors are intended to make future Triton/Numba partner work easier to
integrate without changing the accepted RT-vs-Embree phase contract.

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal2659_v2_4_benchmark_protocol_integration_test
```

Expected:

```text
Ran 4 tests
OK
```

Also run the Goal2658 protocol tests to guard the shared contract.

## Next Work

The next v2.4 step should connect these descriptors to machine-readable phase
timing records for real benchmark runs. After that, the v2.5 partner prototype
can target Triton first and Numba as a secondary/fallback route, while the
current OptiX RT traversal remains the promoted performance path.
