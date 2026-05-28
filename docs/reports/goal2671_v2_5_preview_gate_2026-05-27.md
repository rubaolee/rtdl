# Goal2671: v2.5 Partner Preview Gate

Status: local preview gate added; pod validation required.

Date: 2026-05-27

## Purpose

v2.5 now has several local pieces:

- generic partner-continuation contract;
- Triton preview kernels for segmented count and sum;
- Numba fallback preview for segmented count and sum;
- Numba device-resident group-id validation;
- RayDB descriptor-only continuation plan;
- segmented min/max reference semantics.

This goal adds a machine-readable preview gate so this state is not confused
with a completed v2.5 release or a promoted benchmark result.

## Gate Status

The gate status is:

```text
internal_v2_5_preview_pod_validation_required
```

This is explicitly not a v2.5 completion gate.

## Operation Classification

Preview kernel operations:

- `segmented_count_i64`
- `segmented_sum_f64`

Reference/descriptor-only operations:

- `segmented_min_f64`
- `segmented_max_f64`
- `compact_mask_i64`
- `bounded_collect_finalize_i64`
- `grouped_argmin_f64`

The preview/reference partition must cover all v2.5 operations and must not
overlap.

## Blocked Claims

The preview gate blocks:

- public release tag;
- public speedup claim;
- CUDA execution validation claim;
- benchmark integration validation claim;
- 3-AI consensus claim;
- RT traversal replacement;
- CuPy RawKernel requirement.

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2671_v2_5_preview_gate_test
```

Expected:

```text
Ran 3 tests
OK
```

## Next Required Work

The next real milestone requires a live CUDA pod:

1. run the Goal2665 grouped continuation runner;
2. validate Triton count/sum correctness and timing;
3. optionally validate Numba fallback with `--include-numba`;
4. integrate the Triton path into RayDB count/sum;
5. compare against the existing OptiX-vs-Embree benchmark basis;
6. retry Claude review before any promotion or v2.5 completion claim.
