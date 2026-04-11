# Goal 249 Report: Native CPU/Oracle Environment Hardening

Date: 2026-04-11
Status: implemented

## Summary

Goal 249 closes the last two live follow-ups left in the system-audit DB.

The earlier audit finding was not a semantic correctness problem in the RTDL
runtime. It was a supportability problem: when the native oracle build path
failed, `run_cpu(...)` could expose raw compiler or linker failure text without
enough RTDL-specific guidance.

## What Changed

Updated:

- [oracle_runtime.py](../../src/rtdsl/oracle_runtime.py)
- [test_core_quality.py](../../tests/test_core_quality.py)

The native oracle build path now wraps compiler failures in an RTDL-specific
`RuntimeError` that:

- states the failure happened while preparing `run_cpu(...)`
- gives OS-specific dependency guidance
- preserves the compiler command and tool output

## Verification

Focused test slice:

- `PYTHONPATH=src:. python3 -m unittest tests.test_core_quality tests.goal40_native_oracle_test`
  - `Ran 108 tests`
  - `OK`

Diagnostic probe:

- direct macOS probe of `run_cpu(...)` in the released workspace
  - result: `RUN_CPU_OK`

Diagnostic text probe:

- direct call to the new oracle failure wrapper on macOS
  - result includes:
    - `RTDL native oracle build failed while preparing run_cpu(...)`
    - `brew install geos pkg-config`

## Outcome

The remaining DB follow-ups on:

- `src/rtdsl/runtime.py`
- `src/rtdsl/oracle_runtime.py`

can now be closed for the released `v0.4.0` workspace.
