# RTDL V4.0.0 Public Wording Boundaries

Status: locked for V4.0.0 publication.

## Allowed Short Wording

RTDL V4.0.0 is the current source-tree release for the Python GPU RT-core
operator lane. Its first route, `fixed_radius_count_threshold_2d`, accepts
CuPy, Numba, or PyTorch CUDA device columns and writes caller-owned fixed-size
CUDA output columns.

## Required Qualifiers

Every public V4.0.0 sentence must keep these qualifiers when relevant:

- source-tree release;
- exact route: `fixed_radius_count_threshold_2d`;
- fixed-size one-row-per-query output;
- CuPy, Numba, and PyTorch evidence only for this route;
- native calls synchronize before returning;
- benchmark evidence is route-scoped and not a public speedup claim.

## Forbidden Wording

Do not claim that V4.0.0 includes:

- package install, PyPI, wheel, stable SDK, or generated binding packages;
- public multi-language C ABI release;
- public true-zero-copy or general no-copy execution;
- async or nonblocking completion;
- public speedup, RTX speedup, or RT-core speedup;
- full PyTorch, full Numba, full DLPack, JAX, C++, or Rust support;
- automatic acceleration of arbitrary framework programs.
