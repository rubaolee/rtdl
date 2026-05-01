# Goal1000 ctypes Packed-Layout Futureproofing

Date: 2026-04-26

## Scope

Eliminate Python 3.14 deprecation warnings for packed `ctypes.Structure`
definitions in native runtime bindings before they become Python 3.19 errors.

## Changes

- Added `_layout_ = "ms"` beside `_pack_ = 1` for packed ctypes ABI structs in:
  - `src/rtdsl/embree_runtime.py`
  - `src/rtdsl/apple_rt_runtime.py`
  - `src/rtdsl/hiprt_runtime.py`

## Rationale

Python 3.14 warns that structures using `_pack_` without an explicit layout rely
on the implicit MSVC-compatible layout. These RTDL bindings already rely on the
packed ABI layout shared with native runtime structs. Making `_layout_ = "ms"`
explicit preserves the current ABI intent and prevents the warning from becoming
a future import failure.

## Verification

Commands run:

```bash
python3 -W error::DeprecationWarning - <<'PY'
import sys
sys.path[:0] = ['src', '.']
import rtdsl.embree_runtime
import rtdsl.apple_rt_runtime
import rtdsl.hiprt_runtime
print('native runtime ctypes imports ok')
PY
PYTHONPATH=src:. python3 -m unittest \
  tests.goal825_tier1_profiler_contract_test \
  tests.goal718_embree_prepared_app_modes_test \
  tests.goal967_consensus_external_ai_compliance_test
python3 -m py_compile \
  src/rtdsl/embree_runtime.py \
  src/rtdsl/apple_rt_runtime.py \
  src/rtdsl/hiprt_runtime.py
git diff --check
```

Results:

- Deprecation-warning-as-error import probe: passed
- Focused tests: `Ran 9 tests`, `OK`
- `py_compile`: passed
- `git diff --check`: passed

Post-review full local discovery:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'
```

Result: `Ran 1927 tests in 156.203s`, `OK (skipped=196)`.

## Boundary

This is a Python binding layout declaration update only. It does not change
native kernels, does not run cloud/GPU workloads, and does not authorize public
performance claims.
