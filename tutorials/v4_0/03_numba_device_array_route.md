# Numba DeviceArray Route

Status: current V4.0.0 source-tree tutorial.

This route uses Numba `DeviceNDArray` columns through
`__cuda_array_interface__`. Numba owns the arrays and stream. RTDL borrows the
device columns for the same fixed-radius count/threshold route.

Run:

```bash
PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_numba_hello.py
```

The example validates:

- `ids`, `x`, and `y` are device columns;
- the Numba stream handle reaches the V4 route metadata;
- output columns stay caller-owned;
- the result matches `[1, 1, 0]` neighbor counts.

This tutorial authorizes only the bounded V4.0 M1 Numba DeviceArray route. It
does not authorize arbitrary Numba program acceleration, a full Numba partner
surface, async completion, public true-zero-copy wording, or speedup wording.
