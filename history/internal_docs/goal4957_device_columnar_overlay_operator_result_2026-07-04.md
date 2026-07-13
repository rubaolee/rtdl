# Goal4957 Device/Compiled Columnar Overlay Operator Result

Date: 2026-07-04

## Purpose

Continue v2.14.3, not v2.14.4. The owner requested the next step after
Goal4956:

- keep RayJoin as an app on top of RTDL;
- do not modify RTDL core or native runtime;
- make the writer-free Section 5.7 numeric/binary route closer to a real
  pipeline operator;
- move reprojection/sort/group work out of Python object loops where possible;
- prove the binary route with a downstream descriptor consumer, not with the
  paper text writer.

## Implementation

Updated:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `Paper-reproduction-apps/rayjoin-paper/README.md`
- `tests/goal4956_columnar_xsect_pipeline_test.py`

No `src/rtdsl/**` or `src/native/**` files were edited.

The app route now supports:

```bash
--device-columnar
--compiled-group
--validate-device-order
```

`--device-columnar` uses Numba CUDA for:

- numeric LSI intersection reprojection into column arrays;
- xsect sort-key generation and bitonic sort by `(edge_id, distance, tie_id, original_index)`.

`--compiled-group` uses a Numba-compiled columnar group builder for the
writer-free carrier:

- group lengths;
- descriptor labels;
- skipped group count;
- total point-row count.

The downstream descriptor consumer remains the Numba sorted-pair scan from the
previous route. It proves the writer-free binary route can feed a downstream
operator without invoking the paper text writer.

## Correctness Checks

Device sort was validated against the CPU long-double reference on the POD:

```json
{
  "map0_order_matches_cpu_longdouble_reference": true,
  "map1_order_matches_cpu_longdouble_reference": true
}
```

The 3 steady-state runs preserve the same semantic fingerprint:

```text
pair_count       = 28815
total_groups     = 64459
total_point_rows = 673371
```

This is not the paper text-output route and does not make a paper byte-equality
claim for the numeric route. The exact paper writer route remains separate.

## POD Evidence

POD:

```text
root@213.173.108.15 -p 10689
NVIDIA RTX 4000 Ada Generation
workspace: /root/rtdl_goal4955
```

Artifacts:

- `history/internal_docs/goal4955_artifacts/goal4957_device_columnar_probe_validate_2.json`
- `history/internal_docs/goal4955_artifacts/goal4957_device_compiled_group_validate_1.json`
- `history/internal_docs/goal4955_artifacts/goal4957_device_compiled_group_run_1.json`
- `history/internal_docs/goal4955_artifacts/goal4957_device_compiled_group_run_2.json`
- `history/internal_docs/goal4955_artifacts/goal4957_device_compiled_group_run_3.json`

Steady-state runs:

| Run | Writer-Free Hot Sec | Compiled Group Sec | Pair Count | Groups | Point Rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.9028722914 | 0.0099310428 | 28815 | 64459 | 673371 |
| 2 | 0.8994551385 | 0.0101114884 | 28815 | 64459 | 673371 |
| 3 | 1.0776243601 | 0.0100566773 | 28815 | 64459 | 673371 |

Median:

```text
writer_free_hot_sec = 0.9028722914
```

## Performance Comparison

| Route | Median / Reference Sec | Relative To Original 2.921366s | Notes |
| --- | ---: | ---: | --- |
| Goal4954-E original numeric binary route | 2.921366 | 1.00x | v2.14.2 reference |
| Goal4956 columnar xsect route | 2.309159 | 1.27x | CPU columnar arrays; Python group builder |
| Goal4957 device + compiled columnar route | 0.902872 | 3.24x | Numba CUDA reproj/sort + compiled group |

Compared with the current rerun baseline `2.947452s`, Goal4957 is `3.26x`
faster. Compared with Goal4956 `2.309159s`, Goal4957 is `2.56x` faster.

Compared with the author overlay compute reference `0.0421s`, Goal4957 is still
about `21.45x` slower. This closes the Python object/materialization gap, not
the Layer-4 in-traversal fusion gap.

## Median Phase Breakdown

| Phase | Median Sec |
| --- | ---: |
| `lsi_public_rows_sec` | 0.814879 |
| `intersection_reprojection_device_columnar_sec` | 0.014556 |
| `sort_map0_device_columnar_sec` | 0.011878 |
| `sort_map1_device_columnar_sec` | 0.012324 |
| `vertex_pip_map0_in_map1_sec` | 0.016414 |
| `vertex_pip_map1_in_map0_sec` | 0.006991 |
| `midpoint_points_map0_columnar_sec` | 0.003610 |
| `midpoint_points_map1_columnar_sec` | 0.006997 |
| `grouped_compiled_columnar_carrier_construction_sec` | 0.010057 |
| `grouped_descriptor_pair_count_consumer_sec` | 0.005886 |

The main remaining cost is now `lsi_public_rows_sec`, not Python grouping or
text output. This is the key result of Goal4957.

## What This Proves

Goal4957 proves that the v2.14.3 writer-free binary route can be made much more
pipeline-like without core/runtime changes:

- reprojection moved from CPU NumPy to Numba CUDA;
- xsect ordering moved from CPU `np.lexsort` to Numba CUDA sort;
- group construction moved from Python object/list loops to compiled columnar
  Numba code;
- downstream descriptor consumption stays as a Numba consumer;
- the RayJoin app remains the owner of overlay workflow and paper semantics;
- RTDL core remains generic.

The result is a real measured improvement: `2.921s -> 0.903s`.

## What This Does Not Prove

Not authorized:

- no public high-performance claim;
- no claim that the numeric/binary route is paper byte-equal;
- no claim that RTDL has matched the author C++/CUDA/OptiX overlay compute;
- no Layer-4 fusion claim;
- no claim that all intermediate columns stay device-resident end to end.

The route still copies selected arrays back to host for downstream Python/app
bookkeeping. However, the expensive Python object materialization and group
construction costs have been largely removed from the writer-free path.

## Next Technical Implication

The previous bottleneck diagnosis changes:

- Before Goal4957, the obvious costs were Python reprojection/sort/group.
- After Goal4957, those are millisecond-level.
- The remaining dominant cost is `lsi_public_rows_sec`.

Therefore, further major speedup requires work on the LSI primitive output path
itself: either a narrower pair-id/coordinate projection, more resident native
column output, or eventually Layer-4 fusion. More Python-side group/writer
micro-optimization is no longer the right target for this writer-free route.
