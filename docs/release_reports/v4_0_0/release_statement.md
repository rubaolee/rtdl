# RTDL V4.0.0 Release Statement

Status: released as `v4.0.0`.

RTDL V4.0.0 makes the V4 reframing current: RTDL is the missing RT-core lane
for Python GPU programs, starting with one fixed-radius CUDA device-array
operator.

The released route is `fixed_radius_count_threshold_2d`. A caller can pass
CuPy, Numba, or PyTorch CUDA columns to RTDL, select the fixed-radius route, and
receive caller-owned CUDA output columns. The route is intentionally fixed-size:
one output row per query, not variable-length neighbor enumeration.

This release keeps the evidence boundary strict. It authorizes source-tree V4
operator-route wording only. It does not authorize package install, PyPI, wheel,
stable SDK, public true-zero-copy, async, public speedup, RT-core speedup, full
framework support, or non-Python host embedding wording.
