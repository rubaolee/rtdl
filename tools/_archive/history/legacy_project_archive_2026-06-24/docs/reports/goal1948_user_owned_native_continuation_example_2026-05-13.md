# Goal1948 - User-Owned Native Continuation Example

Status: executable-example-not-v2-speedup-claim

Date: 2026-05-13

## Scope

Goal1948 documents a small example showing that RTDL does not prevent users from
calling their own native code from Python.

Example:

`examples/rtdl_hausdorff_user_cpp_continuation.py`

The example uses RTDL for the RT-shaped part of the app and then calls a
learner-owned C++ continuation for the non-RT app reduction.

## App Shape

```text
Python orchestration
  -> RTDL generic k=1 nearest-neighbor rows
  -> learner-owned C++ max-distance reduction
  -> Python result assembly and oracle check
```

This is intentionally not a Torch/CuPy partner example. It exists to show
interoperability:

- RTDL can produce generic rows.
- Python can pass those rows to user code.
- User C/C++ can finish the app-specific continuation.
- The result can still be checked against a Python oracle.

## Command

Python continuation:

```bash
PYTHONPATH=src:. python examples/rtdl_hausdorff_user_cpp_continuation.py \
  --backend cpu_python_reference --continuation python
```

Learner-owned C++ continuation, when a C++17 compiler is available:

```bash
PYTHONPATH=src:. python examples/rtdl_hausdorff_user_cpp_continuation.py \
  --backend cpu_python_reference --continuation cpp
```

The C++ helper is built into `build/hausdorff_user_cpp/` by default. Users may
set `CXX` or `RTDL_HAUSDORFF_USER_CPP_CACHE` to control the compiler and cache.

## Validation

Windows local validation covers the Python continuation path and the static
claim boundary in `tests.goal1948_user_owned_native_continuation_example_test`.

The learner-owned C++ branch was also validated on the local Linux development
host `192.168.1.20` in an isolated temporary copy, not in the dirty Linux
checkout:

```bash
cd /tmp/rtdl_goal1948_min
PYTHONPATH=src:. timeout 90s python3 \
  examples/rtdl_hausdorff_user_cpp_continuation.py \
  --backend cpu_python_reference --continuation cpp
PYTHONPATH=src:. timeout 90s python3 -m unittest \
  tests.goal1948_user_owned_native_continuation_example_test
```

That Linux run compiled the helper with `/usr/bin/g++` and matched the Python
oracle for both the Hausdorff distance and witness direction. The validation
also caught and fixed the C++ tie rule: exact ties choose `b_to_a`, matching the
Python oracle's deterministic direction rule.

## Claim Boundary

This example does not count as a v2.0 partner speedup row.

The C++ continuation is user-owned application code. RTDL works fine with it
through Python, but v2.0's official partner model remains the reviewed
Torch/CuPy tensor-continuation path. Any performance from this C++ continuation
belongs to the user's application, not to RTDL's v2.0 partner speedup claims.

Allowed claim:

```text
RTDL Python apps can interoperate with user-owned C/C++ continuations.
```

Blocked claim:

```text
This C++ continuation is an official v2.0 partner acceleration path.
```
