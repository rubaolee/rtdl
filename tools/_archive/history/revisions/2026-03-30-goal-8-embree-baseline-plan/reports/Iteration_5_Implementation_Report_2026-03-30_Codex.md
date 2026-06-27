# Iteration 5 Implementation Report

## Scope of This Implementation

This iteration implements Step 1 and Step 2 of the Embree baseline plan:

1. freeze the baseline workload set,
2. define schema and ABI artifacts,
3. define the baseline precision comparison policy,
4. name representative datasets for the baseline.

## Main Artifacts Added

### Machine-readable contracts

- `src/rtdsl/baseline_contracts.py`

This file now defines:

- the frozen workload order,
- the fixed baseline precision mode,
- float comparison tolerances,
- machine-readable workload contracts,
- shared input contract definitions,
- representative dataset names,
- a kernel-vs-contract validator,
- a cross-backend result comparison helper.

### Human-readable contracts

- `docs/embree_baseline_contracts.md`

This document mirrors the machine-readable contract and explains:

- fixed workload scope,
- precision mode,
- shared runtime ABI,
- per-workload input/output schema,
- comparison rules,
- named representative datasets.

### Test coverage

- `tests/baseline_contracts_test.py`

This test file now verifies:

- the frozen workload order,
- the reference kernels match the frozen contracts,
- the LSI comparison policy uses float tolerance,
- exact-mode comparisons reject changed integer/count outputs.

## Updated Existing Files

- `src/rtdsl/__init__.py`
  - exports baseline contract APIs
- `README.md`
  - links the Embree baseline plan and contract docs

## Validation Results

Targeted contract tests:

- `PYTHONPATH=src:. python3 -m unittest tests/baseline_contracts_test.py`
- result: pass

Full test suite:

- `PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'`
- result: 36 tests pass

## Codex Position

Step 1 and Step 2 are implemented in a way that is both:

- reviewable in docs, and
- enforceable in code.

The next review question for Gemini is whether these artifacts are sufficient to count Step 1 and Step 2 as complete, or whether the contract/module/docs still leave meaningful ambiguity.
