# Goal 79 Report: Linux Performance Reproduction Matrix

Date: 2026-04-04

Status:
- complete
- published

## Goal

Goal 79 asked for a Linux-only performance reproduction matrix covering the
available RayJoin-style experiment surfaces that can be compared honestly in the
current RTDL project environment.

Compared systems:

- PostGIS
- RTDL Embree
- RTDL OptiX

Excluded systems:

- Python oracle
- native C oracle
- Vulkan

## Most Important Rule

This package keeps timing boundaries separate.

It does **not** merge these into one comparison table:

- `end_to_end`
- `prepared_execution`
- `cached_repeated_call`

That boundary separation is the main condition that makes the matrix honest.

## Included Linux-Measured Rows

The matrix includes six accepted Linux-measured rows:

1. `county_zipcode` / positive-hit `pip` / `end_to_end`
2. `blockgroup_waterbodies` / positive-hit `pip` / `end_to_end`
3. `county_zipcode` / positive-hit `pip` / `prepared_execution` / OptiX
4. `county_zipcode` / positive-hit `pip` / `prepared_execution` / Embree
5. `county_zipcode_selected_cdb` / positive-hit `pip` / `cached_repeated_call` / OptiX
6. `county_zipcode_selected_cdb` / positive-hit `pip` / `cached_repeated_call` / Embree

All included rows are derived from accepted Linux artifacts already recorded in
Goals 69, 70, 71, and 77.

## Results By Boundary

### End-to-End

#### County/Zipcode `top4_tx_ca_ny_pa`

- PostGIS: `3.238477414 s`
- Embree: `12.668624839 s`
- OptiX: `15.652318004 s`
- parity: exact for Embree and OptiX
- winner: PostGIS

#### BlockGroup/WaterBodies `county2300_s10`

- PostGIS: `0.007254268 s`
- Embree: `0.070980010 s`
- OptiX: `0.069386854 s`
- parity: exact for Embree and OptiX
- winner: PostGIS

### Prepared Execution

#### County/Zipcode `top4_tx_ca_ny_pa` / OptiX

- OptiX best/worst rerun: `2.642049846 / 2.652621304 s`
- PostGIS best/worst rerun: `3.313063422 / 3.333370466 s`
- parity preserved on all reruns: `true`
- beats PostGIS on all reruns: `true`

#### County/Zipcode `top4_tx_ca_ny_pa` / Embree

- Embree best/worst rerun: `1.026593471 / 1.347775829 s`
- PostGIS best/worst rerun: `3.148009729 / 3.203224316 s`
- parity preserved on all reruns: `true`
- beats PostGIS on all reruns: `true`

### Cached Repeated Call

These rows use the archived selected county/zipcode CDB slice from
`goal28d_larger_run`. They prove the runtime-owned cache effect, not a new long
county prepared-execution result.

#### Selected County/Zipcode / OptiX

- first raw-input run: `0.485947633 s`
- best repeated run: `0.000862041 s`
- PostGIS first / best repeated: `0.000527199 / 0.000350572 s`
- parity preserved on all reruns: `true`
- winner on repeated-call boundary: PostGIS

#### Selected County/Zipcode / Embree

- first raw-input run: `2.464383211 s`
- best repeated run: `0.000774917 s`
- PostGIS first / best repeated: `0.000497615 / 0.000325370 s`
- parity preserved on all reruns: `true`
- winner on repeated-call boundary: PostGIS

## Performance Landscape

Current honest summary:

- PostGIS wins on the accepted `end_to_end` rows
- Embree wins on the long `county_zipcode` `prepared_execution` row
- OptiX wins on the long `county_zipcode` `prepared_execution` row
- PostGIS still wins on the selected-slice `cached_repeated_call` rows

This means the project now has a coherent performance picture:

- RTDL backends can beat PostGIS on the long prepared execution boundary
- RTDL still loses on the broader end-to-end package boundary
- the runtime cache helps repeated identical calls, but does not itself produce
  a new PostGIS win on the selected-slice cached boundary

## Explicitly Skipped Surfaces

- `lakes_parks_continent_families`
  - unavailable or unstable dataset acquisition path
- `vulkan_performance_matrix`
  - explicitly out of scope for this goal
- `oracle_backends_performance`
  - correctness references, not performance targets
- `lsi_or_overlay_postgis_matrix`
  - no accepted current comparison package with the same explicit PostGIS
    contract as the positive-hit `pip` rows

## Validation

Local validation:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m py_compile scripts/goal79_linux_performance_reproduction_matrix.py tests/goal79_linux_performance_reproduction_matrix_test.py
PYTHONPATH=src:. python3 -m unittest tests.goal79_linux_performance_reproduction_matrix_test
python3 scripts/goal79_linux_performance_reproduction_matrix.py --output-dir docs/reports/goal79_linux_performance_reproduction_matrix_artifacts_2026-04-04
```

Result:

- `1` test
- `OK`

Artifacts:

- `docs/reports/goal79_linux_performance_reproduction_matrix_artifacts_2026-04-04/goal79_summary.json`
- `docs/reports/goal79_linux_performance_reproduction_matrix_artifacts_2026-04-04/goal79_summary.md`

Reviews:

- `history/ad_hoc_reviews/2026-04-04-codex-review-goal79-linux-performance-reproduction-matrix.md`
- `history/ad_hoc_reviews/2026-04-04-gemini-review-goal79-linux-performance-reproduction-matrix-rerun.md`

## Accepted Meaning

Goal 79 establishes the first consolidated Linux performance matrix for the
available and finishable RTDL RayJoin-style comparison surfaces, with explicit
timing-boundary separation and explicit skipped rows.

## Non-Claims

- Goal 79 does not claim that RTDL beats PostGIS on all available rows
- Goal 79 does not merge end-to-end, prepared, and cached timing boundaries
- Goal 79 does not claim unavailable dataset families were reproduced
- Goal 79 does not include Vulkan or oracle backends in the performance matrix
