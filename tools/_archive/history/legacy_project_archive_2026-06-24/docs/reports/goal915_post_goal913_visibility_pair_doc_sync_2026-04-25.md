# Goal915 Post-Goal913 Visibility Pair Documentation Sync

Date: 2026-04-25

## Purpose

Goal913 fixed the graph `visibility_edges` RTX cloud shape by replacing
Cartesian observer-target visibility expansion with explicit candidate-edge
pair semantics. Goal914 then added a targeted graph/Jaccard rerun driver for
the next pod session. This goal synchronizes the public docs, support matrices,
cloud manifest, runbook, and honesty tests with that post-Goal913 state.

## Changes

- `docs/app_engine_support_matrix.md` now says the graph app is current after
  Goal914 and that `visibility_edges` maps graph candidate edges to
  `rt.visibility_pair_rows(...)`.
- `docs/current_main_support_matrix.md` now lists
  `visibility_pair_rows(..., backend=...)` across CPU, Embree, OptiX, Vulkan,
  HIPRT, and Apple RT, with an implementation note distinguishing pair
  semantics from Cartesian `visibility_rows(...)`.
- `docs/features/visibility_rows/README.md` now documents both APIs:
  `visibility_rows(...)` for all observer-target combinations and
  `visibility_pair_rows(...)` for sparse graph/LOS candidate pairs.
- `docs/rtx_cloud_single_session_runbook.md` now prioritizes the Goal914
  targeted graph/Jaccard rerun when that is the only pending cloud follow-up.
- `scripts/goal759_rtx_cloud_benchmark_manifest.py` and the generated
  `goal759` JSON artifact now name `RTDL visibility_pair_rows` for graph
  candidate edges.
- `docs/reports/goal889_graph_visibility_rt_core_subpath_2026-04-24.md` now
  records the later Goal913 correction so the historical report does not look
  like an active recommendation to use Cartesian visibility rows for copied
  graph edges.
- `tests/goal690_optix_performance_classification_test.py` now accepts
  `graph_analytics` as `optix_traversal`, matching the current matrix. The
  bounded claim is still only graph visibility any-hit plus explicit native
  graph-ray candidate generation; BFS/frontier bookkeeping, triangle
  set-intersection, shortest paths, graph databases, and whole-app graph-system
  acceleration remain outside the claim.

## Boundaries

- This is a documentation and gate-contract synchronization goal.
- It does not add new cloud performance evidence.
- It does not authorize public RTX speedup claims.
- It does not promote Jaccard; Goal913 still requires the Goal914 targeted RTX
  rerun because the 20k Jaccard artifact had parity failure diagnostics.
- `visibility_rows(...)` remains the correct API for dense observer-target
  matrices. `visibility_pair_rows(...)` is the correct API for explicit sparse
  candidate pairs.

## Verification

Regenerated the Goal759 manifest JSON:

```bash
PYTHONPATH=src:. python3 scripts/goal759_rtx_cloud_benchmark_manifest.py \
  --output-json docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json
```

Compiled the changed manifest script:

```bash
PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal759_rtx_cloud_benchmark_manifest.py
```

Focused test suite:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal654_current_main_support_matrix_test \
  tests.goal685_engine_feature_support_contract_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal830_rtx_goal_sequence_doc_sync_test \
  tests.goal633_visibility_rows_test \
  tests.goal914_rtx_targeted_graph_jaccard_rerun_test \
  -v
```

Result: `43 tests OK`.

Whitespace audit:

```bash
git diff --check
```

Result: clean.

## Next Cloud Action

Do not restart a pod only for broad reruns. When a pod is available, run the
Goal914 targeted graph/Jaccard rerun first:

```bash
PYTHONPATH=src:. python3 scripts/goal914_rtx_targeted_graph_jaccard_rerun.py \
  --mode run \
  --copies 20000 \
  --graph-chunk-copies 100 \
  --jaccard-chunk-copies 100,50,20 \
  --output-json docs/reports/goal914_rtx_targeted_graph_jaccard_rerun_rtx.json
```

That run should collect the fixed graph artifact and Jaccard diagnostic
variants in one pod session before any broader cloud testing resumes.
