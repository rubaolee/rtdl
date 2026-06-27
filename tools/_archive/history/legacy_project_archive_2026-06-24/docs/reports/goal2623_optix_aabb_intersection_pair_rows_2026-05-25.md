# Goal2623 OptiX AABB Intersection Pair Rows

Date: 2026-05-25

## Decision

Goal2623 promotes one missing runtime subpath from Goal2622: generic OptiX row
output for `AABB_INDEX_QUERY_2D` `range_intersection_rows`.

The native engine now emits only app-agnostic rows:

```text
(query_id, indexed_id)
```

It does not know about contact, collision, manifolds, triangles, physics, or
robot semantics. The contact-manifold benchmark still owns exact triangle
intersection refinement and contact-summary interpretation in Python.

## Implementation Boundary

New native ABI:

```text
rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows
```

New Python surface:

```text
rtdsl.collect_aabb_intersection_pair_rows_2d_optix(...)
rtdsl.aabb_intersection_pair_rows_2d(..., backend="optix", row_capacity=...)
```

Overflow contract:

- The caller supplies `row_capacity`.
- The public OptiX dispatch rejects missing `row_capacity` instead of defaulting
  to an all-pairs allocation.
- If native traversal observes more raw rows than capacity, the path fails
  closed and returns no partial row table.
- The Python wrapper raises an error containing
  `failure_mode=fail_closed_overflow`.
- Because the OptiX implementation uses bidirectional traversal before host
  de-duplication, capacity must cover the pre-deduplication raw hit count, which
  can reach up to `2x` the final unique pair count.

## Local Tests

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2580_optix_aabb_index_native_symbol_test \
  tests.goal2622_contact_manifold_generic_aabb_discovery_test \
  tests.goal2623_optix_aabb_pair_rows_test
```

Result:

```text
Ran 18 tests in 0.039s
OK (skipped=3)
```

The skips are expected on the Mac because no local OptiX shared library is
loaded.

## Pod Evidence

Pod command:

```bash
ssh root@69.30.85.198 -p 22148 -i /Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

Observed GPU:

```text
NVIDIA RTX A5000, driver 570.211.01, 24564 MiB
CUDA 12.8
OptiX headers: /root/vendor/optix-dev-9.0.0/include/optix.h
```

Build command:

```bash
cd /root/rtdl_goal2622
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev-9.0.0 CUDA_PREFIX=/usr/local/cuda-12.8 NVCC=/usr/local/cuda-12.8/bin/nvcc
```

Pod test command:

```bash
cd /root/rtdl_goal2622
RTDL_OPTIX_LIBRARY=build/librtdl_optix.so PYTHONPATH=src:. python3 -m unittest \
  tests.goal2580_optix_aabb_index_native_symbol_test \
  tests.goal2622_contact_manifold_generic_aabb_discovery_test \
  tests.goal2623_optix_aabb_pair_rows_test
```

Result:

```text
Ran 18 tests in 0.694s
OK
```

## Pressure Results

All rows below used the contact-manifold grid fixture. This fixture has
`N` scene triangles and `N` query triangles, but only `N` exact witnesses. The
RTDL path uses generic AABB rows first, then app-owned exact refinement, then
`COLLECT_K_BOUNDED`.

| Backend | Grid count | Candidate pairs | All possible pairs | Best broadphase sec | Best wall sec | Correct |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| OptiX | 512 | 512 | 262,144 | 0.008688 | 0.014364 | yes |
| OptiX | 4,096 | 4,096 | 16,777,216 | 0.077909 | 0.125423 | yes |
| OptiX | 16,384 | 16,384 | 268,435,456 | 0.295021 | 0.491620 | yes |
| OptiX | 65,536 | 65,536 | 4,294,967,296 | 1.282198 | 2.105445 | yes |
| CPU reference | 512 | 512 | 262,144 | 0.016226 | 0.020971 | yes |
| CPU reference | 4,096 | 4,096 | 16,777,216 | 0.343354 | 0.383711 | yes |
| CPU reference | 16,384 | 16,384 | 268,435,456 | 3.630003 | 3.816834 | yes |
| CPU reference | 65,536 | 65,536 | 4,294,967,296 | 50.224182 | 51.043744 | yes |

Overflow probe:

```text
OptiX AABB_INDEX_QUERY_2D range_intersection_rows overflowed capacity 16;
emitted at least 512; failure_mode=fail_closed_overflow
```

## Interpretation

The key engineering result is not a public speedup claim. The result is that the
contact-manifold benchmark no longer needs Python all-pairs candidate discovery
and no longer needs a contact-specific native row emitter. The generic OptiX
AABB row path is reusable by any app that can lower candidate discovery to
2-D AABB intersection rows.

The measured OptiX path is faster than the CPU reference on large grid cases
because candidate discovery is moved to RT traversal and row emission is bounded
by explicit capacity. The remaining app-owned exact triangle refinement and
Python row handling are still outside the native primitive.

## Claim Boundary

Allowed:

- `AABB_INDEX_QUERY_2D` has a generic OptiX `range_intersection_rows` path.
- The path emits app-agnostic `(query_id, indexed_id)` rows.
- Overflow is fail-closed.
- The contact-manifold benchmark can use this path without native
  contact/collision logic.

Not allowed:

- No public whole-app speedup claim.
- No claim that RTDL implements contact manifolds natively.
- No claim that the engine owns triangle intersection or contact semantics.
- No claim that this row path is a stable external public API beyond the
  current internal benchmark/reconstruction surface.

## Review Fixes

Claude's first review accepted the design with low-severity issues. The current
revision addresses them by:

- documenting that OptiX capacity covers pre-deduplication bidirectional hits;
- adding `RtdlAabbPairRow` layout `static_assert`s;
- adding a GPU-skipped OptiX overflow regression test that asserts
  `failure_mode=fail_closed_overflow`.
