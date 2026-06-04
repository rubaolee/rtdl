# Goal3278 RayJoin PIP Point-Order Locality Probe

Date: 2026-06-03

Status: implemented, pod-measured on NVIDIA A40, and accepted as internal
RayJoin-performance evidence only.

## Purpose

Goal3276 showed that the remaining RayJoin PIP gap is not explained by input
size alone. The 128/256/384/512 scale rows moved non-monotonically, suggesting
that candidate locality and query organization matter.

Goal3278 tests a low-risk generic lever before adding more native machinery:
reorder PIP probe points before packing while preserving caller point IDs. This
is an app/runner locality probe over the existing generic closed-shape
membership primitive. It does not add RayJoin-specific native engine logic.

## Implementation

The RayJoin benchmark app now accepts:

```text
point_order_mode = natural | x_then_y | y_then_x | morton_xy
```

The repeated comparison runner exposes the same control through:

```text
--rtdl-pip-point-order natural|x_then_y|y_then_x|morton_xy
```

The ordering happens before `pack_points`, and the original caller point IDs
are preserved. `morton_xy` computes a deterministic 16-bit Morton key over the
probe-point bounding box and breaks ties by caller point ID.

The option is currently restricted to PIP closed-shape membership workloads.
Non-PIP workloads fail closed if a non-natural point order is requested.

## Pod Evidence

Pod:

```text
GPU: NVIDIA A40, driver 570.211.01
Commit: e5ff4da332d96e09ebba4ff96f1cf93604bcba30
RTDL mode: device_filtered_validated
Query axis: z_point
Exact validation: enabled for every RTDL PIP sample
RayJoin/RTDL inputs: same start0/count512 public CDB slice
```

Artifacts:

- `docs/reports/goal3278_point_order_pod/natural.json`
- `docs/reports/goal3278_point_order_pod/x_then_y.json`
- `docs/reports/goal3278_point_order_pod/y_then_x.json`
- `docs/reports/goal3278_point_order_pod/morton_xy.json`

All four artifacts record `source_dirty: []`, PIP count `1430`, and all claim
boundary flags false.

## Results

| Point order | RTDL PIP median ms | RayJoin PIP median ms | RTDL / RayJoin | Native count-pass median ms | Exact-validation median ms | Count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `natural` | 0.326065 | 0.202143 | 1.613x | 0.256134 | 0.465678 | 1430 |
| `x_then_y` | 0.368252 | 0.203204 | 1.812x | 0.296304 | 0.501864 | 1430 |
| `y_then_x` | 0.335628 | 0.201392 | 1.667x | 0.239396 | 0.525808 | 1430 |
| `morton_xy` | 0.286076 | 0.205445 | 1.392x | 0.207583 | 0.435228 | 1430 |

`morton_xy` is the only positive order in this sweep:

- whole prepared PIP improves `1.14x` over natural order
  (`0.326065 / 0.286076`);
- native count-pass improves `1.23x` over natural order
  (`0.256134 / 0.207583`);
- exact validation remains count-preserving at `1430`;
- `x_then_y` regresses, and `y_then_x` is roughly neutral/slower.

## Interpretation

This is a useful locality win, but not a final RayJoin closure:

1. The result confirms that query ordering affects the generic
   point/closed-shape membership primitive.
2. Morton order is a better generic locality hint than simple x/y sorting on
   this public CDB slice.
3. The best RTDL/RayJoin PIP gap drops from `1.613x` to `1.392x` in the
   source-clean rerun, but RTDL is still slower than upstream RayJoin for this
   scalar PIP query.
4. Because this is app/runner ordering, not a new native primitive, it is a
   good recommended benchmark setting but not the deeper runtime feature we
   still need.

The next engineering target remains a generic native locality/grouping
primitive: something that can make the engine itself reuse closed-shape edge
work across spatially close probe groups, or produce a device-resident grouped
continuation without host materialization.

## Boundary

This goal does not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, RayJoin paper-reproduction claims, or `RTDL
beats RayJoin` claims.

The narrow accepted conclusion is:

```text
Morton-ordered probe packing is a useful generic app-level locality hint for
the RayJoin PIP benchmark, improving the current RTDL scalar PIP route while
preserving exact validation, but a larger native locality/grouping primitive is
still required to close the remaining RayJoin gap.
```

## Verification

Local:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal3278_rayjoin_pip_point_order_locality_probe_test \
  tests.goal3244_rayjoin_same_slice_repeated_count_runner_test \
  tests.goal3276_rayjoin_scale_runner_input_parity_repair_test
```

Result: 16 tests passed.

Pod:

```text
python3 -m unittest \
  tests.goal3278_rayjoin_pip_point_order_locality_probe_test \
  tests.goal3244_rayjoin_same_slice_repeated_count_runner_test
```

Result: 14 tests passed.
