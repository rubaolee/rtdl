# Project Integrity Audit

Date: 2026-04-02

## Purpose

This audit was performed before the next real-data OptiX goal to make the
repository more internally consistent, more reproducible, and more trustworthy
as a foundation for the next development phase.

The audit focused on:

- top-level current-state documentation
- the live CPU/Embree/OptiX runtime story
- the new Goal 44 OptiX benchmark path
- regression-test and verification surface health

## Findings

### 1. Current-state documentation drift

Several live docs still described stale project state even after Goals 40, 43,
and 44:

- `README.md` still described `run_cpu(...)` as the Python reference path
- `README.md` still implied the current executable backend was only Embree on
  the Mac
- `docs/rtdl_feature_guide.md` still said the OptiX backend was not a real
  runnable execution path
- `docs/development_reliability_process.md` still framed OptiX as a future-only
  path

These statements were no longer correct after:

- Goal 40 native C/C++ oracle
- Goal 43 OptiX validation on `192.168.1.20`
- Goal 44 bounded OptiX performance baseline

### 2. Goal 44 benchmark reproducibility gap

The checked-in Goal 44 benchmark script and the checked-in Goal 44 report were
not tightly aligned:

- the script only ran one scale, while the report described two scales
- synthetic points were not seeded, so reruns were not deterministic
- raw row views were not explicitly closed
- parity language in the report was stronger than what the script actually
  measured

This was the largest trust issue found in the current live code/docs surface.

### 3. Verification surface health

The live test/verification surface itself was healthy:

- `make build` passed
- targeted tests for the modified CPU/OptiX paths passed
- the full `make test` suite still passed after the repair set
- `scripts/run_full_verification.py` passed

So the main issues were consistency and reproducibility, not active regression
breakage.

## Repairs Applied

### Documentation repairs

Updated:

- `README.md`
- `docs/rtdl_feature_guide.md`
- `docs/development_reliability_process.md`

These updates now reflect:

- `run_cpu(...)` is the native C/C++ oracle path
- `run_cpu_python_reference(...)` preserves the old Python semantics
- Embree and OptiX are both real controlled execution paths
- the current OptiX path is bounded and bring-up validated, not just a codegen
  skeleton

### Goal 44 benchmark repairs

Updated:

- `scripts/goal44_optix_benchmark.py`
- `docs/reports/goal44_optix_performance_2026-04-02.md`
- added `tests/goal44_optix_benchmark_test.py`

The benchmark now:

- models two explicit scales: `smoke` and `medium`
- uses deterministic synthetic points (`seed = 20260402`)
- closes raw result views explicitly
- records parity mode honestly:
  - `smoke`: exact-row parity
  - `medium`: row-count parity

The report was revised to match that benchmark contract and to avoid
overstating what the benchmark proves.

## Residual Risks

- Historical reports remain historical snapshots and may still describe earlier
  project states. They should not be treated as current-state docs.
- Goal 44 is still a bounded synthetic GPU benchmark, not a real exact-source
  OptiX reproduction of the RayJoin families.
- The repaired Goal 44 harness is now deterministic and internally aligned with
  its report contract, but this audit round did not rerun that revised harness
  on `192.168.1.20`. The archived Goal 44 numbers remain historically useful,
  but a fresh remote rerun should be done before treating them as the current
  benchmark baseline.
- The OptiX runtime is real and validated, but broader real-data GPU validation
  is still the next major step.
- The project still lacks CI and cross-platform automated enforcement.

## Audit Conclusion

After the repairs above, the repository is in a materially better state for the
next action:

- live current-state docs are aligned with the actual codebase
- the Goal 44 benchmark path is more reproducible and more honest
- the verification surface is still green

So the project is now a stronger and more trustworthy foundation for the next
OptiX and real-data development goals.
