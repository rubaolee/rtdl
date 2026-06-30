# Goal 410: Tutorial And Example Cross-Platform Check

## Goal

Make the public tutorial and release-facing example surface runnable from a
fresh checkout on the user's OS, with an explicit verification report across
the three maintained machines.

## Required outcome

- fresh-checkout setup instructions are correct for:
  - macOS
  - Linux
  - Windows
- released graph workloads have real public example CLIs under `examples/`
- tutorial ladder and release-facing example docs point to runnable commands
- the public command surface is checked on:
  - local macOS
  - Linux `lestat-lx1`
  - Windows `lestat-win`

## Backend expectations

- on any OS:
  - `cpu_python_reference` must run
  - `cpu` must run
- if Embree is available on the host:
  - Embree example commands must run
- on Linux with the configured GPU stack:
  - OptiX example commands must run
  - Vulkan example commands must run

## Verification artifact

Produce one consolidated report that records:

- the checked command matrix
- setup assumptions
- per-machine backend availability
- per-command pass/fail/skip status
- any remaining bounded caveats
