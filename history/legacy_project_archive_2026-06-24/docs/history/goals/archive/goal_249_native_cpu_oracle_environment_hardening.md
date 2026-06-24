# Goal 249: Native CPU/Oracle Environment Hardening

## Objective

Close the remaining system-audit follow-ups on the public CPU/oracle runtime
surface by making native-oracle failures more actionable and re-checking the
released workspace behavior directly.

## Scope

This pass covers:

- `src/rtdsl/runtime.py`
- `src/rtdsl/oracle_runtime.py`
- focused quality tests for native-oracle diagnostics

## Required Checks

- native-oracle build/setup failures produce RTDL-specific guidance rather than
  raw linker-only output
- the released workspace still runs a direct `run_cpu(...)` probe successfully
- the audit DB can close the remaining quality follow-ups if the runtime surface
  is now actionable and verified
