# Goal858 Segment/Polygon Docs OptiX Boundary

Date: 2026-04-23

## Purpose

Goal858 refreshes the public segment/polygon docs so they match the actual
OptiX app surface and current claim boundary.

The code already exposes:

- `--optix-mode auto`
- `--optix-mode host_indexed`
- `--optix-mode native`

But the feature docs did not yet explain those modes clearly enough, and they
did not show the current rejection boundary for `--require-rt-core`.

## Changed Files

- `/Users/rl2025/rtdl_python_only/docs/features/segment_polygon_hitcount/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/segment_polygon_anyhit_rows/README.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/segment_polygon_workloads.md`
- `/Users/rl2025/rtdl_python_only/tests/goal858_segment_polygon_docs_optix_boundary_test.py`

## What Changed

### Feature docs now describe the real OptiX surface

`segment_polygon_hitcount` now documents:

- host-indexed OptiX example
- native OptiX example
- the current `--require-rt-core` rejection boundary

`segment_polygon_anyhit_rows` now documents:

- compact `segment_counts` mode
- native OptiX only for the compact path
- rows-mode rejection under native OptiX
- current `--require-rt-core` rejection boundary

### Tutorial now explains mode semantics explicitly

`docs/tutorials/segment_polygon_workloads.md` now has an `OptiX mode boundary`
section that states:

- `auto` preserves current app default
- `host_indexed` forces the released host-indexed fallback
- `native` requests the experimental custom-AABB path

It also states plainly that these commands are still not released NVIDIA RT-core
claims and that pair-row native output does not exist yet.

## Boundary

This goal is documentation truth work only.

It does not:

- promote segment/polygon into the active RTX claim set
- authorize a public NVIDIA RT-core speedup claim
- claim that pair-row native OptiX output exists

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal858_segment_polygon_docs_optix_boundary_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal687_app_engine_support_matrix_test
```

Result:

```text
Ran 10 tests
OK
```

Additional local checks:

```text
python3 -m py_compile tests/goal858_segment_polygon_docs_optix_boundary_test.py
git diff --check
```

Both passed.

## Verdict

Goal858 is complete locally. The segment/polygon public docs now describe the
real OptiX surface and current RT-core honesty boundary more precisely.
