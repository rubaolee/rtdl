# Goal2601 GPU-RMQ Prepared OptiX Reuse And Compact Rows

Date: 2026-05-24

## Purpose

This report answers why the earlier GPU-RMQ RTDL result was slow and records the
fix. The earlier path used the correct RT idea but measured it through the wrong
runtime shape: one-shot OptiX calls rebuilt static scenes and returned thousands
of Python dict rows. That made the benchmark mostly Python materialization and
scene-preparation overhead, not RT traversal.

The fix keeps the native engine app-agnostic:

- Native OptiX exposes a generic prepared static 3-D triangle scene plus generic
  closest-hit rows.
- The Python runtime now also exposes closest-hit row arrays for callers that
  naturally consume columns.
- GPU-RMQ owns all RMQ-specific geometry, query phase scheduling, block decoding,
  and final argmin assembly in app-side Python.
- No GPU-RMQ formula or app vocabulary is added to the native engine.

## Implemented Changes

- Added reusable app-side `PreparedPaperRtRmq` for the paper-style RT lowering.
- Added `paper_rt_prepared_reuse` mode to separate preparation from repeated
  query batches.
- Added generic `PreparedOptixStaticTriangleScene3D.ray_closest_hit_row_arrays`.
- Added compact NumPy assembly for GPU-RMQ query results to avoid Python dict row
  materialization.
- Replaced per-query Python scheduling in the compact path with vectorized NumPy
  phase construction.
- Added tests for the app-side scheduler boundary, packed ray y/z correctness,
  and source wiring of the generic prepared closest-hit array contract.

## Pod Evidence

Pod:

- SSH: `root@203.57.40.101 -p 10082`
- Key used from Mac: `~/.ssh/id_ed25519_rtdl_codex`
- Remote repo: `/workspace/rtdl_goal2598`
- Backend library: `/workspace/rtdl_goal2598/build/librtdl_optix.so`
- GPU: RTX A5000, from earlier pod probe
- CuPy: unavailable on this pod (`ModuleNotFoundError: No module named 'cupy'`)

Validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2594_gpu_rmq_benchmark_front_door_test \
  tests.goal2598_optix_generic_closest_hit_contract_test -v

Ran 19 tests in 0.845s
OK
```

## Performance Matrix

All rows matched the exact CPU oracle. Times are seconds. Prepared OptiX query
times are steady-state repeated query times after one warm prepared call; prepare
time is listed separately.

| Case | CPU exact | Local hierarchy | NumPy slice+argmin | OptiX one-shot | Prepared OptiX compact query | Prepared OptiX prepare |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| repeated 4K values / 1K queries | 0.01665 | 0.00512 | 0.00122 | 0.05575 | 0.00163 | 0.02512 |
| random 16K values / 4K queries | 0.14286 | 0.02938 | 0.00532 | 0.34891 | 0.00276 | 0.09957 |
| repeated 64K values / 8K queries | 0.55033 | 0.06237 | 0.01376 | 0.92688 | 0.00687 | 0.45409 |

Derived comparisons:

- Prepared OptiX compact is about `34x`, `52x`, and `80x` faster than exact CPU
  on these three cases.
- Prepared OptiX compact is about `3.1x`, `10.6x`, and `9.1x` faster than the
  local Python hierarchy.
- Prepared OptiX compact is about `0.75x`, `1.9x`, and `2.0x` the speed of the
  NumPy slice+argmin loop respectively. The small case is still launch/overhead
  dominated; the larger two cases favor the RT path.
- Plain one-shot OptiX is not a valid performance path for RMQ. It is `34x` to
  `135x` slower than prepared compact query because it charges repeated scene
  setup and Python row materialization.

Native traversal is not the main remaining bottleneck:

| Case | Prepared compact query | Native RT traversal in last run |
| --- | ---: | ---: |
| repeated 4K / 1K | 0.00163 | 0.00041 |
| random 16K / 4K | 0.00276 | 0.00043 |
| repeated 64K / 8K | 0.00687 | 0.00297 |

## Conclusion

The earlier slow result happened because we used the RT lowering through an
unoptimized runtime boundary, not because RTDL or RT cores are inherently a bad
fit for this app.

After fixing the boundary, the GPU-RMQ benchmark has a credible RTDL path:

- Correct against exact CPU reference.
- Engine remains app-independent.
- Reused prepared scene avoids static geometry rebuild per query batch.
- Compact row arrays avoid Python dict materialization.
- Vectorized app scheduling avoids Python per-query overhead.
- On larger tested workloads, prepared OptiX compact is about `1.9x` to `2.0x`
  faster than the NumPy slice+argmin baseline on this pod.

Remaining caveats:

- This is not yet a full GPU-RMQ paper reproduction.
- CuPy partner hierarchy could not be tested on this pod because CuPy was not
  installed.
- Public speedup claims remain blocked until the benchmark receives the required
  review/consensus pass and, if needed, stronger same-input author-code evidence.
