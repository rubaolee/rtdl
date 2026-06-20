# CuPy Fixed-Radius Route

Status: current V4.0.0 source-tree tutorial.

This is the smallest V4.0 route with CuPy-owned CUDA arrays. CuPy owns the input
and output columns; RTDL borrows the device pointers, runs the OptiX-backed
fixed-radius route, and writes into the output columns.

Run:

```bash
PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_cupy_hello.py
```

Expected output:

```json
{
  "neighbor_counts": [1, 1, 0],
  "query_ids": [1, 2, 3],
  "threshold_flags": [1, 1, 0]
}
```

The example uses this shape:

```python
search = {"ids": ..., "x": ..., "y": ...}
query = {"ids": ..., "x": ..., "y": ...}
outputs = {"query_ids": ..., "neighbor_counts": ..., "threshold_flags": ...}
```

The route call is:

```python
result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
    query,
    search,
    radius=1.1,
    threshold=1,
    partner="cupy",
    output_columns=outputs,
    stream=stream.ptr,
    return_metadata=True,
)
```

Read the metadata as a boundary contract:

- caller stream propagation is evidence-backed for this route;
- named CUDA column handoff has no observed host staging for named columns;
- public true-zero-copy wording remains blocked;
- async completion remains blocked;
- public speedup and RT-core speedup wording remain blocked.
