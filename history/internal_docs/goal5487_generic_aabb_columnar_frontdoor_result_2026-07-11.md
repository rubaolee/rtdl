# Goal5487: Generic AABB Columnar Front Door

Date: 2026-07-11

Status: `implemented__local_contract_tests_passed__POD_tiny_gate_passed__review_pending`

## Objective

The Goal5486 LibRTS matrix exposed a generic system boundary problem. The
public `prepare_aabb_index_2d` path first materializes every input row as a
Python `Aabb2D`, then creates an identified Python row tuple, and finally
builds a ctypes array. On the largest exact inputs, this front door dominates
the measured route before the prepared OptiX query starts.

Goal5487 introduces an app-neutral host-column contract so callers that already
have numeric columns do not need to reconstruct one Python object per AABB.
This is a system API change, not a LibRTS-specific primitive.

## Implementation

New public type and entrypoint:

```python
columns = rt.Aabb2DColumns.from_mapping(
    {
        "id": ids,
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
    }
)
prepared = rt.prepare_aabb_index_2d_columns(columns, backend="optix")
```

The implementation:

- validates one-dimensional equal-length columns;
- rejects non-integer or out-of-range IDs instead of silently wrapping them;
- validates finite coordinates and max-bound ordering;
- keeps a CPU/reference fallback through the existing row-shaped path;
- packs OptiX input into an aligned NumPy structured array;
- validates the structured dtype size and field offsets against `_RtdlAabb2D`;
- creates a ctypes ABI view with `from_buffer` and retains the NumPy owner for
  the entire prepared-handle lifetime.

The new packing path avoids Python per-row `Aabb2D` and ctypes record
construction. It is **not** device zero-copy: the existing native OptiX
prepare ABI still uploads the host records to device memory. Device-resident
index construction is a separate future contract and is not claimed here.

## Genericity Boundary

The API names and schema are spatially generic: an AABB column set can serve
point containment, range queries, collision broadphases, or spatial joins.
There is no LibRTS, Figure-6, paper, author, or Embree identity in the core
implementation. The LibRTS app has not yet been changed to make this its
default route; the next POD gate will verify ABI/build behavior before any app
promotion or performance statement.

## Local Verification

Focused tests:

```text
$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5487_generic_aabb_columnar_frontdoor_test \
  tests.goal5485_librts_exact_point_contains_prepared_phase_gate_test \
  tests.goal5486_librts_prepared_phase_batch_test
Ran 10 tests OK
```

Also verified:

```text
py -m py_compile src/rtdsl/aabb_columns.py src/rtdsl/aabb_index.py \
  src/rtdsl/optix_runtime.py tests/goal5487_generic_aabb_columnar_frontdoor_test.py
git diff --check
```

The focused tests cover CPU behavior, ABI size/offset compatibility, owner
lifetime, invalid-column fail-closed behavior, and app-neutral source guards.

## POD Verification

The rebuilt OptiX library was tested on the active RTX 4000 Ada POD with the
same tiny boxes and points through both the new columnar API and the existing
row-shaped API. Both paths returned the same count and both reported RT-core
acceleration:

```text
columnar point_contains = 2
row      point_contains = 2
counts_match = true
columnar_rt_core_accelerated = true
row_rt_core_accelerated = true
```

The machine-readable result is
`Paper-reproduction-apps/librts-paper/results/librts_goal5487_generic_aabb_columnar_pod_gate.json`.
This is a tiny build/behavior gate, not a performance measurement.

## Claim Boundary

Authorized:

- a generic host-column AABB input contract;
- local CPU/reference behavior through the new contract;
- native ABI packing compatibility by structural test;
- a planned POD build/tiny OptiX verification gate.

Not authorized:

- device-resident or zero-copy AABB preparation;
- LibRTS performance improvement;
- Figure-6 or full-paper reproduction improvement;
- author-vs-RTDL performance ratio;
- changing the existing exact count claim boundary;
- Embree comparison.

## Next Step

Build the current RTDL OptiX library on the active POD, run a tiny
`prepare_aabb_index_2d_columns` count gate, and compare its count and phase
metadata with the existing row-shaped API. Only after that gate passes should
the LibRTS app-owned loader be adapted to emit columns for a measured
same-input front-door comparison.
