# Goal1337 Graph Raw Summary Metadata Label Refresh

Date: 2026-05-05

## Scope

Refresh active graph raw-row summary metadata labels so the graph BFS and
triangle summary paths no longer report generic `oracle_cpp_raw_row_view` or a
composed `oracle_cpp+oracle_cpp` backend.

Changed active labels:

- Graph BFS raw summary: `native_graph_bfs_raw_summary`.
- Graph triangle raw summary: `native_graph_triangle_raw_summary`.
- Unified graph summary aggregation now composes graph-specific backend labels.

## Boundary

- This is metadata precision only.
- No public speedup wording is added.
- No new OptiX, Embree, Vulkan, HIPRT, or Apple implementation path is added.
- Historical v1.0 status files are not rewritten.

## Local Validation

Source commit before pod validation:
`9d74de9f0dc53d5de47197b76aa0da7b041e80b9`.

Commands:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1158_graph_raw_summary_contract_test \
  tests.goal957_graph_hausdorff_native_continuation_metadata_test \
  tests.goal949_graph_native_summary_continuation_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal690_optix_performance_classification_test
PYTHONPATH=src:. python3 -m unittest $(find tests -maxdepth 1 -name 'goal13*_test.py' -exec basename {} .py \; | sed 's/^/tests./')
git diff --check
```

Result:

- Focused tests: 31 tests OK.
- Goal13 sweep: 76 tests OK.
- `git diff --check`: OK.

## Pod Validation

Pod SSH:

```bash
ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex
```

Environment:

- Ubuntu 24.04.3 LTS.
- Embree package already installed during Goal1336 pod validation:
  Ubuntu `libembree-dev` / `libembree4-4`, version `4.3.0+dfsg-2`.

Validation command after resetting from Git:

```bash
cd /root/rtdl_python_only
git fetch origin main
git reset --hard origin/main
git rev-parse HEAD
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1158_graph_raw_summary_contract_test \
  tests.goal957_graph_hausdorff_native_continuation_metadata_test \
  tests.goal949_graph_native_summary_continuation_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal690_optix_performance_classification_test
```

Result:

- Commit: `9d74de9f0dc53d5de47197b76aa0da7b041e80b9`.
- Focused pod tests: 31 tests OK in 0.224s.
