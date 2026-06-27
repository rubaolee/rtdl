# Goal 16 Testing Package Review

Claude's proposal was partially available in three small successful outputs:

- file recommendations:
  - `tests/dsl_negative_test.py`
  - `tests/cpu_embree_parity_test.py`
  - `tests/report_smoke_test.py`
- negative/adversarial targets:
  - malformed geometry / input
  - invalid numeric parameters
  - missing required CLI arguments
  - resource-exhaustion style failures

Claude's longer proposal for a single top-level verification command timed out, so Codex is completing that part directly.

## Accepted package

1. Add `tests/dsl_negative_test.py`
   Focus: negative compiler/runtime entry cases that are not already covered in `rtdsl_py_test.py`.

2. Add `tests/cpu_embree_parity_test.py`
   Focus: one central parity suite covering all six current workloads with shared comparison policy.

3. Add `tests/report_smoke_test.py`
   Focus: lightweight smoke tests for report generators and CLI-ish entry paths without making the suite fragile or too slow.

4. Add a top-level verification script and Make target.
   Codex recommendation:
   - script: `scripts/run_full_verification.py`
   - Make target: `make verify`
   This should run `make test` semantics plus a small curated set of smoke commands and artifact checks.

## Rejected or constrained parts

- No huge resource-exhaustion tests will be added to the normal suite; those are too unstable for a default local verification path.
- No broad benchmark expansion is part of Goal 16.
- No NVIDIA-dependent checks are allowed.

## Expected outcome

The repo should gain:
- broader negative-path coverage
- one explicit higher-level verification path
- more direct artifact/report smoke coverage
- a materially larger passing test count than 57
