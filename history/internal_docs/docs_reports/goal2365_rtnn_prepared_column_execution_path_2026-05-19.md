# Goal2365 - RTNN Prepared Column Execution Path

Date: 2026-05-19

## Purpose

Goal2363 showed that RTDL's serious nearest-neighbor path must avoid Python
tuple/dict record normalization in the steady-state loop. Goal2365 adds the
next harness-level step: packed columns plus prepared execution.

The intended high-performance shape is:

```python
points = rt.pack_points(ids=ids, x=xs, y=ys, z=zs, dimension=3)
prepared = rt.prepare_optix(kernel).bind(query_points=points, search_points=points)
rows = prepared.run_raw()
```

This keeps learner-friendly records available, but makes the benchmark harness
able to separate preparation cost from repeated execution by reporting three
different costs:

- one-time file/input packing into RTDL columns,
- one-time OptiX prepared binding over already-packed inputs,
- repeated execution over the same buffers.

## Implementation

`scripts/goal2348_rtnn_v2_2_external_runner.py` now accepts:

```text
--input-mode records|packed-columns
--execution-mode run-optix|prepared-optix
```

In `prepared-optix` mode, the runner calls
`rt.prepare_optix(_goal2348_current_fixed_radius_neighbors_3d).bind(...)` once
before the repeat loop. Each repeat then calls either `prepared.run_raw()` or
`prepared.run()` depending on `--result-mode`.

If prepared binding fails because the local machine lacks the current OptiX
library, the runner records `ok: false` and the preparation error in the JSON
artifact instead of exiting before writing evidence.

The emitted JSON now includes:

- `input_mode`
- `input_pack_sec`
- `execution_mode`
- `execution_prepare_sec`
- `phase_timings`
- `claim_boundary.prepared_execution_reuses_python_packed_inputs`

## Boundary

This is a harness/API usability improvement on the current v2.2 basis. It does
not claim RTNN paper equivalence, does not claim RT-core acceleration, and does
not authorize a release performance claim. Claim boundary: Goal2365 does not claim RTNN paper equivalence.
The current default native path is still the generic
uniform-cell bounded-neighbor traversal unless
`RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_RT` is explicitly enabled for diagnostic
OptiX custom-primitive probing.

## Design Lesson

For v2.x, `prepared_bounded_neighbor_search_3d` should be a first-class public
primitive shape: users should be able to prepare packed columns once, run many
queries, and inspect preparation, transfer, traversal, compaction, and output
costs separately.

Python records remain valuable for teaching and correctness tests. Packed
columns plus prepared execution are the performance contract.

## Validation

Local tests cover the CLI surface and claim boundary:

```text
py -3 -m unittest \
  tests.goal2365_rtnn_prepared_column_execution_path_test \
  tests.goal2363_rtnn_packed_column_neighbor_path_test \
  tests.goal2348_rtnn_v2_2_external_runner_test
```

Local Linux smoke validation was also run on `192.168.1.20` using a separate
clean checkout at `/home/lestat/work/rtdl_codex_goal2365`, commit `a88c33a8`.
The host built `build/librtdl_optix.so` with
`OPTIX_PREFIX=/home/lestat/vendor/optix-dev`, generated 4096 synthetic 3D
points, and ran:

```text
run-rtdl-current-3d-neighbors-smoke \
  --input-mode packed-columns \
  --execution-mode prepared-optix \
  --result-mode raw \
  --repeat 2
```

The artifact is
`docs/reports/goal2365_local_linux_prepared_smoke_4096.json`. It records
`ok: true`, `execution_mode: prepared-optix`, `input_mode: packed-columns`, and
`claim_boundary.prepared_execution_reuses_python_packed_inputs: true`.

Pod timing is intentionally deferred until a GPU pod is available. The next pod
run should compare:

- records + `run-optix`
- packed-columns + `run-optix`
- packed-columns + `prepared-optix`

at the existing 65,536 and 262,144 point scales, with `--repeat 3` or higher.
