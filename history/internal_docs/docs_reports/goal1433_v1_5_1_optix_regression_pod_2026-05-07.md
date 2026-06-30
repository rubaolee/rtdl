# Goal 1433 v1.5.1 OptiX Regression Pod Rerun

## Verdict

ACCEPTED for the measured RTX A5000 OptiX regression package.

After `93f4259b74cb7570497827e4b36789fd554ed7ed` was pushed to `origin/main`, the pod checkout was reset to `origin/main`, OptiX was rebuilt, the focused collect-k/OptiX slice passed, and the broader `*optix*test.py` discovery passed.

## Evidence

- OptiX rebuild transcript: `docs/reports/goal1433_v1_5_1_optix_regression_build_optix_2026-05-07.txt`
- Focused OptiX regression transcript: `docs/reports/goal1433_v1_5_1_optix_regression_focused_slice_2026-05-07.txt`
- Broad OptiX discovery transcript: `docs/reports/goal1433_v1_5_1_optix_regression_broad_discover_2026-05-07.txt`

## Run Scope

- Host: GPU pod at `root@69.30.85.196`, SSH port `22030`
- GPU: NVIDIA RTX A5000
- Driver: `580.126.09`
- Repository path: `/workspace/rtdl`
- Git HEAD: `93f4259b74cb7570497827e4b36789fd554ed7ed`
- Focused slice: collect-k production wrapper route, generic i64 ABI parity, OptiX closure, v1.5 generic OptiX evidence, and OptiX interop tests
- Broad slice: `python3 -m unittest discover -s tests -p '*optix*test.py'`

## Result

- Focused OptiX slice: `Ran 47 tests in 1.085s`, `OK`
- Broad OptiX discovery: `Ran 309 tests in 137.184s`, `OK`
- Required backend failures: none
- Required backend skips: none reported by unittest

## Claim Boundary

This is NVIDIA pod regression evidence only. It does not authorize stable `COLLECT_K_BOUNDED` promotion, public speedup wording, zero-copy wording, whole-app claims, broad workload claims, release tags, or release action.
