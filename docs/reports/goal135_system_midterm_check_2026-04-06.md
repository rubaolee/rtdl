# Goal 135 System Midterm Check

## Verdict

Current `main` is credible as a live whole-system branch on the accepted
primary platform after one integration-surface repair. The strongest remaining
whole-system weakness is not Linux correctness but branch-state clarity:

- Linux clean-checkout whole-system matrix is green
- Linux `v0_2_full` matrix is green
- this Mac is still not a whole-system green platform because the broad unit
  group depends on native `geos_c` linkage that is not present locally
- the front-door docs had remained too v0.1-heavy for the actual state of
  `main`; that gap was corrected in this goal

## Evidence

### Local Mac

- `python3 -m compileall src examples scripts tests`
  - `OK`
- `python3 scripts/run_test_matrix.py --group v0_2_local`
  - `28 tests`, `OK`, `3 skipped`
- `python3 scripts/run_test_matrix.py --group integration`
  - `31 tests`, `OK`, `5 skipped`
- `python3 scripts/run_test_matrix.py --group system`
  - `34 tests`, `OK`
- `python3 scripts/run_test_matrix.py --group unit`
  - `193 tests`
  - `FAILED`, `24 errors`, `11 skipped`
  - dominant failure mode:
    - `ld: library 'geos_c' not found`

### Linux primary platform

All Linux whole-system evidence in this goal used a clean throwaway clone of
current `main` at commit `68075bab222877b6f3dd3635e1bbe06015d67cae`:

- `/tmp/rtdl_system_midterm_20260406`

Results:

- `python3 -m compileall src examples scripts tests`
  - `OK`
- `python3 scripts/run_test_matrix.py --group v0_2_full`
  - `36 tests`, `OK`, `3 skipped`
- `python3 scripts/run_test_matrix.py --group full`
  - initially failed with one real code defect:
    - `tests.baseline_integration_test` omitted the new
      `segment_polygon_anyhit_rows` workload from its kernel map
  - after repair:
    - `281 tests`, `OK`, `2 skipped`

### Correctness and performance state reused from the current accepted Linux reports

The current system midterm check also relies on the already-published Linux
large-scale audit evidence from Goal 131.

Current accepted large-row summary at `x4096`:

`segment_polygon_hitcount`

- PostGIS `1.167043 s`
- CPU `0.149339 s`
- Embree `0.133990 s`
- OptiX `0.135224 s`
- Vulkan `0.150495 s`
- parity `true`

`segment_polygon_anyhit_rows`

- PostGIS `0.419224 s`
- CPU `0.154114 s`
- Embree `0.143328 s`
- OptiX `0.140265 s`
- Vulkan `0.136616 s`
- parity `true`

## Real issue found and fixed

### Missing integration coverage for the second segment/polygon family

Broad Linux `full` failed because
`tests/baseline_integration_test.py` iterated over
`rt.BASELINE_WORKLOAD_ORDER` but did not provide a kernel for
`segment_polygon_anyhit_rows`.

Repair:

- add `segment_polygon_anyhit_rows_reference` to the representative kernel map
- extend the Goal 10 baseline-runner integration check to include that family

This was a genuine whole-system regression gap, not a platform/environment
artifact.

## Documentation consistency result

Before this goal:

- `README.md` and `docs/README.md` still surfaced a mostly v0.1 front door
- the live v0.2 state existed, but was not prominent enough from the entry path

After this goal:

- `README.md` now distinguishes:
  - archived `v0.1` trust anchor
  - live `v0.2` midterm state on `main`
- `docs/README.md` now surfaces:
  - `docs/v0_2_user_guide.md`
  - the live presence of the two closed segment/polygon families

## Honest boundary

Current `main` should be treated as:

- whole-system green on the accepted Linux primary platform
- strongly tested but not fully whole-system green on this Mac
- because the broad local unit surface still depends on missing `geos_c`
  linkage

That is a platform-boundary limitation of the current local environment, not a
new Linux system regression.
