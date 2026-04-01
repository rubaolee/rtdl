# Goal 16 Implementation Report

Implemented changes:

- added `tests/dsl_negative_test.py`
  - duplicate input name rejection
  - invalid input role rejection
  - kernel must return `rt.emit(...)`
  - unexpected runtime input rejection
  - invalid polygon vertex count rejection
  - invalid `run_baseline_case(..., backend=...)` rejection

- added `tests/cpu_embree_parity_test.py`
  - one central authored-case parity suite across all six current workloads

- added `tests/report_smoke_test.py`
  - baseline runner missing-argument CLI failure
  - baseline runner invalid-dataset CLI failure
  - full verification smoke path
  - evaluation artifact smoke output

- added `scripts/run_full_verification.py`
  - top-level local verification package
  - runs unittest suite, CLI smokes, artifact smokes, and a small Embree parity smoke

- updated `Makefile`
  - new `make verify`

- updated `README.md`
  - documents `make verify`

- updated `src/rtdsl/baseline_runner.py`
  - direct function validation for invalid backend values

Validation results:

- full unittest suite passes: `68` tests
- `make verify` passes
- verification output now records the unittest transcript plus CLI/artifact/Embree smoke results

Real defects found and fixed during Goal 16:

1. CLI smoke checks initially failed because subprocess-based tests were not setting `PYTHONPATH=src:.`.
   - fixed in `tests/report_smoke_test.py`
   - fixed centrally in `scripts/run_full_verification.py`

2. An apparent codegen failure surfaced during a parallel validation attempt, but that was a shared-build-path concurrency artifact from running the full suite and `make verify` at the same time.
   - resolved by using sequential validation for the authoritative evidence

Net effect:

- the repo now has a clearer test package story
- negative-path coverage is stronger
- CPU/Embree parity has one central six-workload check
- the project now has a stronger top-level local verification command than `make test` alone
