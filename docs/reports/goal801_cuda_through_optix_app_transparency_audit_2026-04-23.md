# Goal 801 CUDA-Through-OptiX App Transparency Audit

Date: 2026-04-23

Status: local-first transparency guard complete

## Purpose

This goal audits the OptiX-exposed spatial/scientific apps that are useful RTDL
applications but are **not** current NVIDIA RT-core traversal claims:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_hausdorff_distance_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_ann_candidate_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_barnes_hut_force_app.py`

These apps are important, but their current OptiX paths are classified as
`cuda_through_optix`, not `optix_traversal` or
`optix_traversal_prepared_summary`.

## Finding

The app support matrix already records the correct boundary:

- Hausdorff uses KNN rows through CUDA-style kernels in the OptiX backend
  library.
- ANN candidate search uses KNN rows through CUDA-style kernels and keeps
  recall/quality evaluation in Python.
- Barnes-Hut uses KNN/radius-style candidate generation plus Python
  tree/opening-rule/force reduction.

Before this goal, the boundary was visible in docs and matrix APIs, but the
apps' own JSON output did not consistently expose it. That makes app-level
benchmark logs easier to misread.

## Changes Made

Each app now includes an `optix_performance` object in its JSON output:

```json
{
  "class": "cuda_through_optix",
  "note": "..."
}
```

Changed files:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_hausdorff_distance_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_ann_candidate_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_barnes_hut_force_app.py`
- `/Users/rl2025/rtdl_python_only/tests/goal692_optix_app_correctness_transparency_test.py`

## Verification

Focused tests:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal692_optix_app_correctness_transparency_test \
  tests.goal505_v0_8_app_suite_test \
  tests.goal513_public_example_smoke_test \
  tests.goal705_optix_app_benchmark_readiness_test
```

Result:

- `23` tests;
- `OK`.

Compile check:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m py_compile \
  examples/rtdl_hausdorff_distance_app.py \
  examples/rtdl_ann_candidate_app.py \
  examples/rtdl_barnes_hut_force_app.py \
  tests/goal692_optix_app_correctness_transparency_test.py
```

Result:

- `OK`.

## Release Boundary

Allowed statement:

- Hausdorff, ANN candidate search, and Barnes-Hut are useful RTDL apps and can
  run through the OptiX backend interface, but their current OptiX app outputs
  explicitly classify the path as `cuda_through_optix`.

Disallowed statements:

- these apps are currently accelerated by NVIDIA RT cores;
- these apps are active RTX speedup claim candidates;
- whole-app performance for these apps is an OptiX RT-core traversal result.

## Next Step

Future work can still redesign these apps around true RT traversal primitives,
but that is a separate implementation goal. Until then, they should stay out
of paid RTX RT-core claim batches and be treated as GPU-compute or app-design
evidence only.
