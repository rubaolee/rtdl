# Goal4449 / V3.0 M53 - Reusable Aggregate-Tree Fused Numba CUDA Partner

## Result

M53 promotes the M52 Barnes-Hut fused-subtree lesson into a reusable RTDL
app-reference partner surface:

```python
rt.prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda(...)
rt.sum_aggregate_tree_fused_weighted_vectors_2d_numba_cuda(...)
```

The new contract is:

```text
generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1
```

This API consumes generic weighted points plus DFS/resume-index aggregate tree
rows, then runs one Python-source Numba CUDA kernel that fuses traversal,
opening-rule acceptance, exact fallback, and vector accumulation. It does not
emit frontier rows and does not materialize contribution rows.

## Why This Matters

M52 proved the performance shape: fused traversal plus force accumulation beats
the prepared RTDL/OptiX aggregate-frontier route for Barnes-Hut's current
contract. M53 makes that shape reusable. A user no longer has to copy a
benchmark script to use the no-C++ fused CUDA partner route; they can call a
named RTDL app-reference API with claim-boundary metadata.

This is still not an RT-core primitive. It is the clean partner lane that V3 can
use while the deeper RT-native fused primitive design is being worked out.

## Smoke Evidence

Pod live smoke:

| Bodies | Bucket | Contribution rows | Hot kernel event | Max abs diff x | Max abs diff y | Result |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 64 | 8 | 2,070 | 0.395 ms | 5.68e-14 | 1.14e-13 | pass |

The hot event is a tiny-scale sanity timing after the first Numba compilation
run. It is not a benchmark claim.

## Boundary

What M53 can say:

- RTDL has a reusable no-C++ Numba CUDA partner API for fused aggregate-tree
  weighted-vector sums.
- The API preserves the app-agnostic surface: weighted points, aggregate tree
  rows, theta, and softening.
- Metadata explicitly records no frontier rows emitted, no contribution-row
  materialization, no app-specific native engine logic, and no RT-core speedup
  authorization.

What M53 cannot say:

- It is not an OptiX/RT-core fused primitive.
- It is not an Embree comparison.
- It does not authorize public speedup wording.
- It does not automatically select a partner for users.

## Raw Evidence

- `docs/reports/goal4449_v3_0_m53_aggregate_tree_fused_numba_cuda_partner_smoke_2026-06-16.json`
- `tests/goal4449_v3_0_m53_aggregate_tree_fused_numba_cuda_partner_test.py`
- `src/rtdsl/app_reference/aggregate_force_math.py`

## Next

The next architectural step is to design the RT-native counterpart to this
contract. The M53 API is the reference partner lane: it shows the desired
contract shape without putting Barnes-Hut-specific callback logic inside the
native engine.
