# Goal 91 Status: Test Expansion For RayJoin Reproduction

Date: 2026-04-05
Status: complete

## Added so far

### Milestone backend-comparison regression

New test:

- `/Users/rl2025/rtdl_python_only/tests/goal89_backend_comparison_refresh_test.py`

Purpose:

- lock down the accepted long exact-source backend matrix from published JSON
  artifacts
- confirm parity and the current backend-performance ranking are not drifting

### Vulkan fast-path regression coverage

Expanded:

- `/Users/rl2025/rtdl_python_only/tests/goal80_runtime_identity_fastpath_test.py`

Purpose:

- extend canonical tuple identity fast-path coverage to Vulkan
- extend primed packed-input reuse coverage to Vulkan

### Backend boundary-mode contract coverage

New test:

- `/Users/rl2025/rtdl_python_only/tests/goal91_backend_boundary_support_test.py`

Purpose:

- make the current native-backend `boundary_mode='inclusive'` limitation
  explicit and regression-tested

### Legacy face-reference helper coverage

Expanded:

- `/Users/rl2025/rtdl_python_only/tests/rtdsl_py_test.py`

Purpose:

- assert real offset/count relations for `chains_to_polygon_refs`

## Validation so far

Passed:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal89_backend_comparison_refresh_test \
  tests.goal76_runtime_prepared_cache_test
```

Passed targeted parser/view slice:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.rtdsl_py_test.RtDslPythonTest.test_rayjoin_cdb_parser_and_views \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal89_backend_comparison_refresh_test \
  tests.goal76_runtime_prepared_cache_test
```

## Outcome

- milestone backend claims now have direct regression coverage
- Vulkan now shares the same fast-path regression surface as OptiX and Embree
- current native `boundary_mode` limits are explicitly tested
