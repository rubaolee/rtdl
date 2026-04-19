# Goal630 v0.9.4 Goal15 Optional Native Skip Response

Date: 2026-04-19
Status: ready for review

## Trigger

An external release-level test report still observed one blocking error in
`tests.goal15_compare_test.Goal15CompareTest.test_native_compare_matches_rtdl_on_small_uniform_cases`.

The reported failure was a local optional native C++ comparison build crash while
linking against `-lembree4` and `-lgeos_c`. The intended release behavior is that
optional native comparison tests skip when their local C++ comparison toolchain
is unavailable; they must not force the portable Python test suite to exit with
code 1.

## Root Cause

The existing fix converted many optional native comparison failures into
`SkipTest` after an exception was raised. However, `goal15_compare_test.py` still
entered the native comparison compile path before proving that the local optional
toolchain was present. That left some external machines seeing a raw linker
failure as the visible test behavior.

## Fix

Added a preflight helper in `tests/_optional_native_compare.py`:

- verifies `c++` is present on non-Windows hosts
- verifies Embree headers/libraries are discoverable
- verifies GEOS C is discoverable through `pkg-config` or common library paths
- raises `unittest.SkipTest` before invoking the optional native comparison
  compiler when these dependencies are absent

Updated `tests/goal15_compare_test.py` to call the preflight helper before
`compare_goal15(...)`.

Also expanded the exception helper to include `cmd` and `stdout` when
classifying optional native comparison failures, so future
`CalledProcessError` variants expose more diagnostic context. The fallback
classification is keyed to native-comparison toolchain markers such as Embree,
GEOS, `-lembree4`, `-lgeos_c`, and the Goal15 native helper binaries; it does
not skip every arbitrary subprocess failure solely because a process returned
non-zero.

## Files Changed

- `/Users/rl2025/rtdl_python_only/tests/_optional_native_compare.py`
- `/Users/rl2025/rtdl_python_only/tests/goal15_compare_test.py`

## Validation

Focused release-blocker suite:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal15_compare_test \
  tests.goal17_prepared_runtime_test \
  tests.goal19_compare_test \
  tests.report_smoke_test
```

Result:

```text
Ran 13 tests in 41.240s
OK
```

Synthetic helper classification check:

```text
subprocess.CalledProcessError(1, ['c++', '-lembree4', '-lgeos_c'])
```

Result:

```text
SkipTest optional native comparison toolchain unavailable
```

## Boundary

This does not hide real RTDL correctness mismatches. The skip is only for the
optional external C++ native comparison toolchain. If the toolchain is available
and the native comparison runs, row mismatches still fail normally.
