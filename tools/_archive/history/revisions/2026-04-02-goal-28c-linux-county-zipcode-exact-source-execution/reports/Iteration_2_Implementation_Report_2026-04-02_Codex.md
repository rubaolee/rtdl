# Goal 28C Implementation Report

Date: 2026-04-02
Round: 2026-04-02-goal-28c-linux-county-zipcode-exact-source-execution

## Implemented

- ArcGIS page conversion in:
  - `/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py`
- public polygon helper:
  - `chains_to_polygons(...)`
- Linux execution harness:
  - `/Users/rl2025/rtdl_python_only/scripts/goal28c_convert_and_run_county_zipcode.py`
- conversion tests:
  - `/Users/rl2025/rtdl_python_only/tests/goal28c_conversion_test.py`
- Linux portability fixes:
  - `/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py`
  - `/Users/rl2025/rtdl_python_only/src/native/rtdl_embree.cpp`

## Host Run

Host:

- `192.168.1.20`

Converted artifacts:

- `uscounty_full.cdb`: full county exact-source conversion
- `zipcode_partial.cdb`: valid staged-checkpoint zipcode conversion
- `uscounty_exec.cdb`: 1-feature county execution subset
- `zipcode_exec.cdb`: 1-feature zipcode execution subset

Result summary:

- LSI:
  - cpu rows: `0`
  - embree rows: `0`
  - parity: `True`
  - cpu sec: `3.626239`
  - embree sec: `1.407477`
- PIP:
  - cpu rows: `6`
  - embree rows: `6`
  - parity: `True`
  - cpu sec: `0.003355`
  - embree sec: `0.002007`

## Verification

Local:

- `PYTHONPATH=src:. python3 -m unittest tests.goal28c_conversion_test tests.goal28b_staging_test`
- `make build`

Host-backed:

- `/home/lestat/work/rayjoin_sources/goal28c_exact_source_run/goal28c_summary.json`
- `/home/lestat/work/rayjoin_sources/goal28c_exact_source_run/goal28c_summary.md`

## Boundary

This round closes:

- full-county exact-source conversion
- staged-checkpoint zipcode conversion
- first feature-limited Linux exact-source `lsi` / `pip` execution slice

This round does not close:

- full paper-scale `County ⊲⊳ Zipcode` execution
- full Zipcode acquisition
- exact polygon-face reconstruction
