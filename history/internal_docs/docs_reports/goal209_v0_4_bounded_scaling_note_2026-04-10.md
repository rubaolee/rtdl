# Goal 209 Report: v0.4 Bounded Scaling Note

## Summary

Goal 209 closes the `v0.4` acceptance requirement for at least one benchmark or
scaling note on the new nearest-neighbor workload family.

## Implementation

- added a bounded harness:
  - `/Users/rl2025/rtdl_python_only/examples/internal/rtdl_v0_4_nearest_neighbor_scaling_note.py`
- added tests:
  - `/Users/rl2025/rtdl_python_only/tests/goal209_nearest_neighbor_scaling_note_test.py`
- generated a bounded JSON artifact:
  - `/Users/rl2025/rtdl_python_only/build/goal209_nearest_neighbor_scaling_note.json`

## Honest Boundary

- This is a bounded local scaling note, not a benchmark-win claim.
- It uses deterministic fixture-derived cases only.
- SciPy is included only if present locally.
- PostGIS is not required for this slice.

## Local Results

Generated artifact:

- `/Users/rl2025/rtdl_python_only/build/goal209_nearest_neighbor_scaling_note.json`
- preserved repo copy:
  - `/Users/rl2025/rtdl_python_only/docs/reports/goal209_v0_4_bounded_scaling_note_data_2026-04-10.json`

Current local macOS run:

- `scipy_available = false`
- repeats per backend = `5`

Observed median timings from the generated artifact:

- `fixed_radius_neighbors`
  - `fixture` (`3 x 3`): Python `0.015709 ms`, CPU `0.023625 ms`, Embree `0.054875 ms`
  - `fixture_tiled_x8` (`24 x 24`): Python `0.235541 ms`, CPU `0.182750 ms`, Embree `0.212125 ms`
  - `fixture_tiled_x32` (`96 x 96`): Python `1.224417 ms`, CPU `0.541125 ms`, Embree `0.504125 ms`
- `knn_rows`
  - `fixture` (`3 x 3`): Python `0.026583 ms`, CPU `0.044458 ms`, Embree `0.055334 ms`
  - `fixture_tiled_x8` (`24 x 24`): Python `0.219000 ms`, CPU `0.209875 ms`, Embree `0.320625 ms`
  - `fixture_tiled_x32` (`96 x 96`): Python `3.848416 ms`, CPU `0.781208 ms`, Embree `1.106792 ms`

All recorded backend rows matched the Python reference rows under the workload
comparison contract.

## Correction Found During Goal 209

The first Goal 209 benchmark run exposed a real bug in the existing
`fixed_radius_neighbors` Embree path:

- `knn_rows` stayed correct
- `fixed_radius_neighbors` Embree returned zero rows on the fixture-derived
  benchmark cases

Root cause:

- `rtdl_embree_run_fixed_radius_neighbors(...)` did not set
  `g_query_kind = QueryKind::kFixedRadiusNeighbors` before `rtcPointQuery(...)`
- the shared callback therefore took the wrong query-kind branch

Repair applied during Goal 209:

- `/Users/rl2025/rtdl_python_only/src/native/embree/rtdl_embree_api.cpp`

After that repair:

- the original Goal 200 Embree test slice passed again
- the Goal 209 scaling harness passed with full row parity

## Verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal209_nearest_neighbor_scaling_note_test tests.goal208_nearest_neighbor_examples_test tests.goal207_knn_rows_external_baselines_test`
  - `Ran 13 tests`
  - `OK`
- `python3 -m compileall /Users/rl2025/rtdl_python_only/examples/internal/rtdl_v0_4_nearest_neighbor_scaling_note.py /Users/rl2025/rtdl_python_only/tests/goal209_nearest_neighbor_scaling_note_test.py`
  - `OK`
- `PYTHONPATH=src:. python3 examples/internal/rtdl_v0_4_nearest_neighbor_scaling_note.py --repeats 5`
  - `OK`
- `PYTHONPATH=src:. python3 -m unittest tests.goal200_fixed_radius_neighbors_embree_test`
  - `Ran 5 tests`
  - `OK`
