# Goal 91 Report: Test Expansion For RayJoin Reproduction

Date: 2026-04-05
Status: complete

## Scope

Goal 91 expands milestone-level regression coverage around the accepted
RayJoin-style backend story instead of adding only report-helper checks.

The emphasis is:

- backend comparison invariants
- runtime fast-path behavior
- documented current API/contract limits
- stronger parser/view assertions for accepted dataset helpers

## Test additions and updates

### Backend comparison artifact regression

Added:

- `/Users/rl2025/rtdl_python_only/tests/goal89_backend_comparison_refresh_test.py`

This test loads the published Goal 81/82/83/87/88 artifact summaries and
asserts milestone-level invariants directly:

- accepted row count remains `39073`
- accepted SHA-256 digest remains stable across backends
- PostGIS plans remain indexed on the accepted surfaces
- OptiX and Embree retain their accepted ordering relative to PostGIS
- Vulkan remains parity-clean but slower on the repeated raw-input row

### Runtime fast-path coverage

Updated:

- `/Users/rl2025/rtdl_python_only/tests/goal80_runtime_identity_fastpath_test.py`

New coverage:

- Vulkan now has the same identity-based repeated-call fast-path checks already
  used for OptiX and Embree
- CDB-derived canonical views now prove that Vulkan can also reuse primed
  packed inputs

### Boundary-mode contract coverage

Added:

- `/Users/rl2025/rtdl_python_only/tests/goal91_backend_boundary_support_test.py`

This test captures the current honest native contract:

- authored kernels with unsupported boundary modes still compile
- native lowering rejects unsupported `boundary_mode` values before backend
  execution

This avoids silently implying broader native support than the current runtime
  actually implements.

### Parser/view helper assertions

Updated:

- `/Users/rl2025/rtdl_python_only/tests/rtdsl_py_test.py`

The accepted RayJoin CDB parser/view test now asserts actual offset/count
relations for `chains_to_polygon_refs(...)` instead of only checking lengths.

## Validation

Passed:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal91_backend_boundary_support_test \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal89_backend_comparison_refresh_test
```

Result:

- `8` tests
- `OK`

Passed:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.rtdsl_py_test.RtDslPythonTest.test_rayjoin_cdb_parser_and_views \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal89_backend_comparison_refresh_test \
  tests.goal76_runtime_prepared_cache_test
```

Result:

- `11` tests
- `OK`

## Outcome

Goal 91 strengthens the current milestone package in three ways:

- backend claims now have direct regression checks against published artifacts
- Vulkan is no longer the odd backend out in fast-path coverage
- current native API limits are now tested instead of merely implied in prose
