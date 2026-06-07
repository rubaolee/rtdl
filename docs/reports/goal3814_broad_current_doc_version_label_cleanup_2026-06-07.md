# Goal3814 Broad Current Doc Version-Label Cleanup

Date: 2026-06-07

## Purpose

Goal3812 refreshed the main learner doors to the current v2.10 surface. A
broader scan then found child tutorial pages, benchmark READMEs, and a few
benchmark app CLI descriptions still calling the current path `v2.8`.

Goal3814 removes those stale current-facing labels while preserving historical
method names and artifact keys such as `rtdl_v2_user_cuda`.

## Files Updated

| Area | Operation |
| --- | --- |
| `docs/tutorials/*.md` | Replaced current-facing `v2.8-facing` tutorial labels with `v2.10-facing` or current wording. |
| `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md` | Reworded the user CUDA continuation as a current RTDL path while preserving the historical method key. |
| `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md` | Reworded RayJoin expression/current-scope text from `RTDL v2.8` to current RTDL. |
| `examples/v2_0/research_benchmarks/rt_dbscan/README.md` and `raydb_style/README.md` | Updated current-scope recommendation wording to v2.10. |
| `rtdl_hausdorff_v2_user_benchmark.py`, `rtdl_hausdorff_v2_language_lab.py`, and `rtdl_rt_dbscan_benchmark_app.py` | Updated CLI/print descriptions only; method names and artifact keys are unchanged. |

## Boundary

- This is documentation and CLI-description cleanup only.
- Historical method names, artifact keys, and report links remain unchanged.
- No native engine code changed.
- No release, package-install, public speedup, broad RT-core speedup, true
  zero-copy, paper-reproduction, AMD performance, automatic partner selection,
  or app-specific native-engine claim is authorized.

## Validation

Focused validation checks that broad learner/tutorial/benchmark Markdown and
changed benchmark CLI strings no longer contain stale current-facing v2.8/v2.9
phrases while preserving historical method names.
