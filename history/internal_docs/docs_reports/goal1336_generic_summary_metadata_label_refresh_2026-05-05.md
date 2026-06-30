# Goal1336 Generic Summary Metadata Label Refresh

Date: 2026-05-05

## Scope

Refresh active ANN, Barnes-Hut, and graph summary-continuation metadata/docs so
they use specific native summary labels instead of generic `oracle_cpp` or
`native C++ continuation` wording.

Changed active labels:

- ANN compact rerank summaries: `native_knn_rerank_summary`.
- Barnes-Hut compact candidate summaries:
  `native_fixed_radius_candidate_summary`.
- Graph BFS summary mode: `native_graph_bfs_summary`.
- Graph triangle summary mode: `native_graph_triangle_summary`.
- Unified graph docs/support text: native graph BFS/triangle summary
  continuations.

## Boundary

- This is an active metadata/documentation precision update.
- No public v1.5 release wording is added.
- No new public speedup claim is added.
- No Vulkan, HIPRT, or Apple RT implementation work is added.
- Historical v1.0 status/report files are not rewritten by this cleanup.

## Local Validation

Source commit before pod validation:
`dc0be5b1851b3726b2ceac0d1c4c300435623ec3`.

Commands:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal735_ann_candidate_compact_output_test \
  tests.goal734_barnes_hut_embree_compact_output_test \
  tests.goal949_graph_native_summary_continuation_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal690_optix_performance_classification_test
PYTHONPATH=src:. python3 -m unittest $(find tests -maxdepth 1 -name 'goal13*_test.py' -exec basename {} .py \; | sed 's/^/tests./')
git diff --check
```

Result:

- Focused tests: 34 tests OK.
- Goal13 sweep: 76 tests OK.
- `git diff --check`: OK.

## Pod Validation

Pod SSH:

```bash
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Environment:

- Ubuntu 24.04.3 LTS.
- Initial focused validation failed because Embree was not installed at a
  configured prefix.
- Installed packaged Embree with:
  `apt-get install -y libembree-dev`.
- Installed Embree package: Ubuntu `libembree-dev` / `libembree4-4`,
  version `4.3.0+dfsg-2`.
- Header/library probe after install: `/usr/include/embree4`,
  `/lib/x86_64-linux-gnu/libembree4.so`.

Validation command after resetting from Git:

```bash
cd /root/rtdl_python_only
git fetch origin main
git reset --hard origin/main
git rev-parse HEAD
PYTHONPATH=src:. python3 -m unittest \
  tests.goal735_ann_candidate_compact_output_test \
  tests.goal734_barnes_hut_embree_compact_output_test \
  tests.goal949_graph_native_summary_continuation_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal690_optix_performance_classification_test
```

Result:

- Commit: `dc0be5b1851b3726b2ceac0d1c4c300435623ec3`.
- Focused pod tests: 34 tests OK in 8.477s.
