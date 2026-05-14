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
