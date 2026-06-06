# Goal3572 Grouped i64 Full-Reduction Small-Group Fast Path

Date: 2026-06-06

## Purpose

Goal3572 extends the v2.9 grouped-i64 small-group fast path beyond `sum` and
`sum_count`.

The design target is generic and app-agnostic:

- preserve the existing dense-small-group `sum` / `sum_count` path from v2.9;
- add small-group global-atomic-pressure reduction for `count`, `min`, `max`,
  and `stats`;
- keep all RayDB/database/app semantics outside the native engine;
- produce A5000 evidence against the v2.9 closeout commit.

This is not a release packet and does not authorize public speedup claims.

## Implementation

The final native implementation keeps two generic OptiX kernels:

| Kernel | Operations | Reason |
| --- | --- | --- |
| `device_column_grouped_i64_small_group_kernel` | `sum`, `sum_count` | Preserves the original v2.9 hot path and shared-memory shape. |
| `device_column_grouped_i64_small_group_reduction_kernel` | `count`, `min`, `max`, `stats` | Adds operation-specific shared-memory reductions for the remaining grouped-i64 operations. |

The launch selector in `src/native/optix/rtdl_optix_workloads.cpp` chooses the
specialized sum/sum-count kernel first, then the broader reduction kernel for
the newly covered operations. Shared-memory allocation is operation-specific:

- `count`: one shared array;
- `sum` / `sum_count`: two shared arrays;
- `min` / `max`: two shared arrays;
- `stats`: four shared arrays.

## A5000 Evidence

The accepted artifact is:

`docs/reports/goal3572_grouped_i64_full_reduction_fastpath_preserve_long_a5000/summary.json`

Run configuration:

| Field | Value |
| --- | ---: |
| baseline commit | `f5090057` |
| candidate commit | `bfcb943c` |
| candidate native dirty | `false` |
| GPU | RTX A5000 pod |
| copies | 120000 |
| warmup | 3 |
| repeat | 5000 |
| trials | 5 |

Summary:

| Metric | Value |
| --- | ---: |
| all modes correct | `true` |
| geomean speedup | `1.157044x` |
| median speedup | `1.245297x` |
| min speedup | `0.987797x` |
| max speedup | `1.324430x` |

Per-mode result:

| Mode | Baseline median sec | Candidate median sec | Speedup | Interpretation |
| --- | ---: | ---: | ---: | --- |
| `count` | `0.000584199` | `0.000441094` | `1.324430x` | New fast path win. |
| `min` | `0.000606282` | `0.000486857` | `1.245297x` | New fast path win. |
| `max` | `0.000562883` | `0.000445567` | `1.263298x` | New fast path win. |
| `avg_as_sum_count` | `0.000501193` | `0.000497831` | `1.007569x` | Preserved sum-count path, parity-positive. |
| `sum` | `0.000491094` | `0.000497161` | `0.987797x` | Preserved sum path, near parity; no new sum speedup claim. |

## Engineering Notes

An earlier generalized-kernel attempt made all operations share one branchy
kernel. That improved `count`, `min`, and `max`, but regressed `sum_count`.
The final implementation preserves the original sum/sum-count kernel name and
path, and moves the new behavior into a separate reduction kernel.

The remaining `sum` row is within a small micro-timing band around parity. Since
the sum path is not the new Goal3572 feature, the report treats it as preserved
near parity rather than as a claimed improvement.

## Boundary

This goal demonstrates an internal primitive improvement only.

It does not authorize:

- release or tag action;
- public speedup claims;
- whole-app acceleration claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- paper reproduction claims;
- package-install claims.

## Validation

Local structural validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3572_grouped_i64_small_group_full_reduction_fastpath_test tests.goal3564_grouped_i64_small_group_sum_fastpath_test
```

Pod evidence validation is covered by:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3572_grouped_i64_full_reduction_fastpath_a5000_test
```
