# Goal 17 Report: Low-Overhead Embree Runtime Slice

## Scope

Goal 17 implements the first low-overhead runtime slice for RTDL on top of Embree.

The objective of this round is not to replace the Python-like DSL.

The objective is to preserve the DSL while reducing the host/runtime overhead that Goal 15 identified in the current RTDL + Embree path.

This slice focuses on:

- `lsi`
- `pip`

## What Was Added

- packed native-ready input containers:
  - `pack_segments(...)`
  - `pack_points(...)`
  - `pack_polygons(...)`
- prepared execution API:
  - `prepare_embree(kernel)`
  - `PreparedEmbreeKernel`
  - `PreparedEmbreeExecution`
- thin native result view:
  - `EmbreeRowView`

The current prepared path supports:

- `segment_intersection`
- `point_in_polygon`

## Main Architectural Result

Packed inputs alone are not enough.

For `lsi`, the prepared dict-return path was not materially faster than the current RTDL Embree path. The remaining cost is dominated by Python result rematerialization.

The real speedup came from the new raw-row view path:

- pack inputs once
- bind once
- run the backend
- return an `EmbreeRowView`
- materialize Python dictionaries only when needed

This confirms the central architecture rule:

- Python can remain the control plane
- Python should not remain the main data plane

## Measured Result

Measured on the Goal 15 comparison fixtures:

### LSI

- current RTDL Embree total: `0.012566375 s`
- prepared dict hot median: `0.015598333 s`
- prepared raw hot median: `0.000558667 s`
- raw speedup vs current RTDL Embree: about `22.49x`
- raw gap vs Goal 15 native lower-bound path: about `0.95x`

### PIP

- current RTDL Embree total: `0.011545791 s`
- prepared dict hot median: `0.011060042 s`
- prepared raw hot median: `0.000267833 s`
- raw speedup vs current RTDL Embree: about `43.11x`
- raw gap vs Goal 15 native lower-bound path: about `0.82x`

## Interpretation

This round does **not** prove that the ordinary Python-dictionary result path has reached native-like performance.

It does prove that:

- the current gap is largely a host/data-plane problem
- compiled-once + packed-input execution is the correct direction
- a thin native result view can move RTDL much closer to the pure native path

So the honest conclusion is:

- the DSL itself is not the main performance problem
- the old runtime data path was the main performance problem
- the first low-overhead slice is successful for `lsi` and `pip`, especially when the caller consumes thin native result views instead of immediate Python dict rows

## Remaining Gap

What is still not solved:

- the ordinary `run_embree(...)` dict-return path is still materially slower than native
- the current low-overhead slice does not yet cover all workloads
- the benchmark baseline still uses the Goal 15 native wrapper path, which includes wrapper/application overhead rather than pure Embree traversal cost alone

## Main Files

- [embree_runtime.py](../../src/rtdsl/embree_runtime.py)
- [__init__.py](../../src/rtdsl/__init__.py)
- [goal17_compare_prepared_embree.py](../../scripts/goal17_compare_prepared_embree.py)
- [goal17_prepared_runtime_test.py](../../tests/goal17_prepared_runtime_test.py)
