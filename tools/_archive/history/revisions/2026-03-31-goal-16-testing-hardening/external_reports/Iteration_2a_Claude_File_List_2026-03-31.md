Based on the Goal 16 spec (testing hardening) and the existing test suite, here are 3 recommended test files:

`tests/dsl_negative_test.py` — negative/error-path tests for the DSL compiler (invalid kernels, malformed ops, type mismatches) to cover currently untested failure modes

`tests/cpu_embree_parity_test.py` — parametrized parity checks across all 6 baseline workloads verifying CPU and Embree produce numerically matching results on identical inputs

`tests/report_smoke_test.py` — smoke tests for the benchmark report pipeline (artifact generation, JSON schema validation, no silent failures on dry runs)

file-list done.
