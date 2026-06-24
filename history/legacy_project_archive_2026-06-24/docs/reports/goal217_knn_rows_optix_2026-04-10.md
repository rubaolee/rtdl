# Goal 217 Report

## Scope

Implement OptiX support for `knn_rows`.

## Main Changes

- added `RtdlKnnNeighborRow` to the OptiX C ABI
- added `rtdl_optix_run_knn_rows(...)`
- added a CUDA `knn_rows` helper kernel
- added host-side OptiX/CUDA launch and row extraction
- added Python runtime dispatch and ctypes registration
- added dedicated tests in
  `/Users/rl2025/rtdl_python_only/tests/goal217_knn_rows_optix_test.py`

## Validation

Local macOS slice:

- `PYTHONPATH=src:. python3 -m unittest tests.goal217_knn_rows_optix_test`
- result:
  - `Ran 5 tests`
  - `OK (skipped=5)`

Linux host `lestat@192.168.1.20`:

- `cd /home/lestat/work/rtdl_python_only && make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev`
- `cd /home/lestat/work/rtdl_python_only && PYTHONPATH=src:. python3 -m unittest discover -s tests -p "goal217_knn_rows_optix_test.py" -v`
- result:
  - `Ran 5 tests`
  - `OK`

Regression confirmation:

- `goal216_fixed_radius_neighbors_optix_test.py`
- result:
  - `Ran 5 tests`
  - `OK`

## Boundary

- GPU distance values are float32-derived, so tests use tolerant distance
  comparison rather than exact double equality.
